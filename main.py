import os
import time
import asyncio
import concurrent.futures
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes_cached
from backend.permission_compiler import compile_permissions
from backend.filters import (
    check_isolation, check_compliance,
    check_permission, check_temporal, check_derivability
)

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
db = create_client(url, key) if url and key else None

# ── Global cache ─────────────────────────────────────────────────────────────
_cache = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if db is None:
        print("[startup] WARNING: No DB connection — cache empty")
        yield
        return

    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor()

    results = await asyncio.gather(
        loop.run_in_executor(executor, lambda: db.table("knowledge_nodes").select("*").execute()),
        loop.run_in_executor(executor, lambda: db.table("hierarchy_levels").select("id, level_number, parent_ids, department").execute()),
        loop.run_in_executor(executor, lambda: db.table("users").select("*").execute()),
    )

    nodes_data  = results[0].data or []
    levels_data = results[1].data or []
    users_data  = results[2].data or []

    # Adjacency: {level_id: [parent_id, ...]}
    adjacency = {
        row["id"]: row.get("parent_ids") or []
        for row in levels_data
    }

    # Nodes indexed by level for fast BFS lookup
    nodes_by_level = {}
    for n in nodes_data:
        lvl = n.get("hierarchy_level_id")
        nodes_by_level.setdefault(lvl, []).append(n)

    # Global level IDs — levels whose department is NULL or marked global
    # Used to detect if a node is naturally reachable vs Zone 2 injected
    global_level_ids = {
        row["id"] for row in levels_data
        if row.get("department") is None or row.get("department") == ""
    }

    # Zone 2 nodes: zone=2 AND their level is a global level
    # Separating these ensures BFS doesn't accidentally include them
    # for dept-restricted users even when zone2=False
    global_nodes = [
        n for n in nodes_data
        if n.get("zone") == 2
        and n.get("hierarchy_level_id") in global_level_ids
    ]

    _cache["all_nodes"]        = {n["id"]: n for n in nodes_data}
    _cache["nodes_by_level"]   = nodes_by_level
    _cache["global_nodes"]     = global_nodes
    _cache["global_node_ids"]  = {n["id"] for n in global_nodes}
    _cache["global_level_ids"] = global_level_ids
    _cache["all_levels"]       = levels_data
    _cache["adjacency"]        = adjacency
    _cache["users"]            = {u["id"]: u for u in users_data}
    _cache["total_node_count"] = len(nodes_data)

    print(f"[startup] cached {len(nodes_data)} nodes | "
          f"{len(levels_data)} levels | "
          f"{len(users_data)} users | "
          f"{len(global_nodes)} zone2 nodes | "
          f"{sum(len(v) for v in adjacency.values())} edges")

    yield  # ── server live ──

    _cache.clear()
    print("[shutdown] cache cleared")


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/users")
async def get_users():
    """All 7 users for frontend dropdown — served from cache"""
    return list(_cache.get("users", {}).values())


@app.get("/pipeline/{user_id}")
async def run_pipeline(user_id: str, zone2: bool = True):
    """Full pipeline — zero DB calls during request"""
    if not _cache:
        return {"status": "error", "message": "Cache not initialised"}

    timings = {}
    total_start = time.perf_counter()

    # ── 1. User lookup ────────────────────────────────────────────────────
    user = _cache["users"].get(user_id)
    if not user:
        return {"status": "error", "message": f"User {user_id} not found"}

    all_levels     = _cache["all_levels"]
    user_dept      = user.get("department")
    user_ceiling   = user.get("ceiling_level", 15)
    role           = user.get("role")
    org_id         = user.get("org_id", "supra")
    user_clearance = user.get("compliance_clearance") or []

    # ── 2. Permission Compiler ────────────────────────────────────────────
    t = time.perf_counter()
    permission_map = compile_permissions(user, all_levels)
    timings["permission_compile_ms"] = round((time.perf_counter() - t) * 1000, 2)

    # ── 3. Entry Point Resolver ───────────────────────────────────────────
    entry_level = None

    if role == "ADMIN":
        for level in sorted(all_levels, key=lambda x: x["level_number"]):
            if level["level_number"] == 1:
                entry_level = level
                break
    else:
        # Deepest level in user's dept within their ceiling
        dept_levels = [
            l for l in all_levels
            if l.get("department") == user_dept
            and l["level_number"] <= user_ceiling
        ]
        if dept_levels:
            entry_level = max(dept_levels, key=lambda x: x["level_number"])

        # Fallback: any level in dept
        if not entry_level:
            dept_levels_any = [
                l for l in all_levels
                if l.get("department") == user_dept
            ]
            if dept_levels_any:
                entry_level = min(dept_levels_any, key=lambda x: x["level_number"])

        # Final fallback: root
        if not entry_level:
            for level in sorted(all_levels, key=lambda x: x["level_number"]):
                if level["level_number"] == 1:
                    entry_level = level
                    break

    entry_level_id = entry_level["id"] if entry_level else None

    # ── 4. BFS Traversal — pure Python, zero DB calls ─────────────────────
    t = time.perf_counter()

    reachable_levels    = get_reachable_nodes_cached(entry_level_id, _cache["adjacency"])
    reachable_level_ids = set(reachable_levels.keys())

    if role == "ADMIN":
        # ADMIN sees everything — but exclude global nodes here,
        # they are handled by Zone 2 injection below so the
        # toggle works correctly even for ADMIN
        bfs_nodes = [
            n for n in _cache["all_nodes"].values()
            if n["id"] not in _cache["global_node_ids"]
        ]
    else:
        # Only nodes whose level is reachable AND not a global level
        # Global levels are handled exclusively by Zone 2 injection
        bfs_nodes = []
        for lvl_id in reachable_level_ids:
            if lvl_id not in _cache["global_level_ids"]:
                bfs_nodes.extend(_cache["nodes_by_level"].get(lvl_id, []))

    timings["bfs_ms"] = round((time.perf_counter() - t) * 1000, 2)
    after_bfs = len(bfs_nodes)

    # ── 5. Zone 2 Injection ───────────────────────────────────────────────
    t = time.perf_counter()
    if zone2:
        bfs_ids = {n["id"] for n in bfs_nodes}
        for n in _cache["global_nodes"]:
            if n["id"] not in bfs_ids:
                bfs_nodes.append(n)
                bfs_ids.add(n["id"])
    after_zone2 = len(bfs_nodes)
    timings["zone2_inject_ms"] = round((time.perf_counter() - t) * 1000, 2)

    # ── 6. Five Sequential Checks ─────────────────────────────────────────
    t = time.perf_counter()
    pool = [n for n in bfs_nodes if check_isolation(n, org_id)]
    after_check1 = len(pool)
    timings["check1_isolation_ms"] = round((time.perf_counter() - t) * 1000, 2)

    t = time.perf_counter()
    pool = [n for n in pool if check_compliance(n, user_clearance)]
    after_check2 = len(pool)
    timings["check2_compliance_ms"] = round((time.perf_counter() - t) * 1000, 2)

    t = time.perf_counter()
    pool = [n for n in pool if check_permission(n, permission_map)]
    after_check3 = len(pool)
    timings["check3_permission_ms"] = round((time.perf_counter() - t) * 1000, 2)

    t = time.perf_counter()
    pool = [n for n in pool if check_temporal(n)]
    after_check4 = len(pool)
    timings["check4_temporal_ms"] = round((time.perf_counter() - t) * 1000, 2)

    t = time.perf_counter()
    pool = [n for n in pool if check_derivability(n)]
    after_check5 = len(pool)
    timings["check5_derivability_ms"] = round((time.perf_counter() - t) * 1000, 2)

    timings["total_ms"] = round((time.perf_counter() - total_start) * 1000, 2)

    # ── 7. Candidate Set Assembly ─────────────────────────────────────────
    candidate_set = []
    for node in pool:
        level_id = node.get("hierarchy_level_id")
        distance = reachable_levels.get(level_id, 99)

        if distance <= 1:
            compression_hint = "FULL"
        elif distance == 2:
            compression_hint = "COMPRESSED"
        else:
            compression_hint = "CONSTRAINT_ONLY"

        candidate_set.append({
            "id":                  node["id"],
            "type":                node.get("type"),
            "title":               node.get("title"),
            "content":             node.get("content"),
            "importance":          node.get("importance"),
            "zone":                node.get("zone"),
            "hierarchy_level_id":  level_id,
            "department":          node.get("department"),
            "distance_from_entry": distance,
            "compression_hint":    compression_hint,
        })

    candidate_set.sort(key=lambda x: x.get("importance") or 0, reverse=True)

    return {
        "user":            user_id,
        "user_name":       user.get("name"),
        "role":            role,
        "ceiling_level":   user_ceiling,
        "entry_point":     entry_level_id,
        "zone2_enabled":   zone2,
        "pipeline_timing": timings,
        "funnel": {
            "total_nodes":  _cache["total_node_count"],
            "after_bfs":    after_bfs,
            "after_zone2":  after_zone2,
            "after_check1": after_check1,
            "after_check2": after_check2,
            "after_check3": after_check3,
            "after_check4": after_check4,
            "after_check5": after_check5,
        },
        "candidate_set": candidate_set,
    }