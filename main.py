import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes, inject_zone2_nodes
from backend.permission_compiler import compile_permissions
from backend.filters import (
    check_isolation, check_compliance,
    check_permission, check_temporal, check_derivability
)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
db = create_client(url, key) if url and key else None


@app.get("/pipeline/{user_id}")
async def run_pipeline(user_id: str, zone2: bool = True):
    if db is None:
        return {"status": "error", "message": "Database not initialized"}

    timings = {}
    total_start = time.perf_counter()

    # ── 1. Fetch user ──────────────────────────────────────────
    user_resp = db.table("users").select("*").eq("id", user_id).single().execute()
    if not user_resp.data:
        return {"status": "error", "message": f"User {user_id} not found"}
    user = user_resp.data

    # ── 2. Permission Compiler (runs ONCE, O(1) lookup) ────────
    t = time.perf_counter()
    levels_resp = db.table("hierarchy_levels").select("*").execute()
    all_levels = levels_resp.data or []

    # Get actual total knowledge node count (not hierarchy level count)
    total_nodes_resp = db.table("knowledge_nodes").select("id", count="exact").execute()
    total_node_count = total_nodes_resp.count or 50

    permission_map = compile_permissions(user, all_levels)
    timings["permission_compile_ms"] = round((time.perf_counter() - t) * 1000, 2)

    # ── 3. Entry Point Resolver ────────────────────────────────
    user_dept = user.get("department")
    user_ceiling = user.get("ceiling_level", 15)
    role = user.get("role")

    entry_level = None

    if role == "ADMIN":
        # ADMIN always starts at root (L1)
        for level in sorted(all_levels, key=lambda x: x["level_number"]):
            if level["level_number"] == 1:
                entry_level = level
                break
    else:
        # Entry point = the level in user's department whose level_number
        # is CLOSEST to (but not exceeding) the user's ceiling.
        # This means: find the shallowest level in their dept they can access.
        # For Priya (VIEWER, L10, ortho) → HL-10-ORTHO-W (L10, ortho)
        # For Vikram (HOD, L4, ortho)    → HL-05-ORTHO   (L5, ortho) — deepest ortho level <= ceiling
        # We want the level in their dept with the highest level_number <= ceiling.

        dept_levels = [
            l for l in all_levels
            if l.get("department") == user_dept and l["level_number"] <= user_ceiling
        ]

        if dept_levels:
            # Pick the one with the highest level_number (deepest in tree) within ceiling
            entry_level = max(dept_levels, key=lambda x: x["level_number"])

        # Fallback: any level in dept
        if not entry_level:
            dept_levels_any = [l for l in all_levels if l.get("department") == user_dept]
            if dept_levels_any:
                entry_level = min(dept_levels_any, key=lambda x: x["level_number"])

        # Final fallback: root
        if not entry_level:
            for level in sorted(all_levels, key=lambda x: x["level_number"]):
                if level["level_number"] == 1:
                    entry_level = level
                    break

    entry_level_id = entry_level["id"] if entry_level else None

    # ── 4. BFS Traversal ──────────────────────────────────────
    t = time.perf_counter()

    # BFS runs for ALL roles including ADMIN
    reachable_levels = get_reachable_nodes(entry_level_id, db)
    reachable_level_ids = list(reachable_levels.keys())

    if role == "ADMIN":
        # ADMIN fetches all nodes directly
        nodes_resp = db.table("knowledge_nodes").select("*").execute()
        bfs_nodes = nodes_resp.data or []
    else:
        nodes_resp = db.table("knowledge_nodes").select("*")\
            .in_("hierarchy_level_id", reachable_level_ids).execute()
        bfs_nodes = nodes_resp.data or []

    timings["bfs_ms"] = round((time.perf_counter() - t) * 1000, 2)
    after_bfs = len(bfs_nodes)

    # ── 5. Zone 2 Injection (conditional) ─────────────────────
    t = time.perf_counter()
    if zone2:
        zone2_nodes = inject_zone2_nodes(db)
        bfs_ids = {n["id"] for n in bfs_nodes}
        for n in zone2_nodes:
            if n["id"] not in bfs_ids:
                bfs_nodes.append(n)
                bfs_ids.add(n["id"])
    after_zone2 = len(bfs_nodes)
    timings["zone2_inject_ms"] = round((time.perf_counter() - t) * 1000, 2)

    # ── 6. Five Sequential Checks ──────────────────────────────
    org_id = user.get("org_id", "supra")
    user_clearance = user.get("compliance_clearance") or []

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

    # ── 7. Candidate Set Assembly ──────────────────────────────
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
            "id": node["id"],
            "type": node.get("type"),
            "title": node.get("title"),
            "content": node.get("content"),
            "importance": node.get("importance"),
            "zone": node.get("zone"),
            "hierarchy_level_id": level_id,
            "department": node.get("department"),
            "distance_from_entry": distance,
            "compression_hint": compression_hint,
        })

    candidate_set.sort(key=lambda x: x.get("importance") or 0, reverse=True)

    return {
        "user": user_id,
        "user_name": user.get("name"),
        "role": role,
        "ceiling_level": user_ceiling,
        "entry_point": entry_level_id,
        "zone2_enabled": zone2,
        "pipeline_timing": timings,
        "funnel": {
            "total_nodes": total_node_count,
            "after_bfs": after_bfs,
            "after_zone2": after_zone2,
            "after_check1": after_check1,
            "after_check2": after_check2,
            "after_check3": after_check3,
            "after_check4": after_check4,
            "after_check5": after_check5,
        },
        "candidate_set": candidate_set,
    }