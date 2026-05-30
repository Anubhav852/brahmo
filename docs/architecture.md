# BRAHMO Pipeline Architecture

## Overview
The BRAHMO Rules Engine is a deterministic, zero-LLM pipeline that filters a clinical knowledge graph down to a personalized candidate set for each user session. Every decision is binary — pass/fail. No LLM is involved at any stage.

---

## 1. Permission Compiler

Runs ONCE at session start. Compiles user permissions into an O(1) hashmap.

```python
# Input: user record + all 15 hierarchy levels
# Output: {level_id: {can_read: bool}}
permission_map = compile_permissions(user, all_levels)
```

**Why O(1) matters:** With 500+ nodes after BFS, checking each node's permission against the DB would be 500 queries (N+1 problem). Compiling once into a dictionary means each check is a single dictionary lookup — microseconds instead of milliseconds.

---

## 2. Entry Point Resolver

Maps the user's department to their DAG leaf node (starting position for BFS).

- Nurse Priya (Ortho Ward, L10) → `HL-10-ORTHO-W`
- Dr. Vikram (Ortho Dept, L4) → `HL-05-ORTHO`
- Admin Suresh (L1) → root hospital node

Fallback chain: exact match → closest level in dept → any level in dept → root.

---

## 3. BFS Traversal (upward through DAG)

Starts at entry point, walks UP via parent edges. Uses a visited set to prevent re-processing multi-parent nodes.

```python
queue = deque([entry_level_id])
visited = {entry_level_id: 0}  # level_id: distance
while queue:
    current = queue.popleft()
    for parent_id in get_parents(current):
        if parent_id not in visited:
            visited[parent_id] = visited[current] + 1
            queue.append(parent_id)
```

**Multi-parent handling:** If node A has parents B and C, it's processed once (visited set). Distance is set on first encounter.

**Cycle prevention:** Visited set ensures nodes are never re-queued. Even if a cycle exists in the data, the BFS won't infinite-loop.

**ADMIN shortcut:** ADMIN users start at root and reach all nodes — BFS is skipped, all nodes fetched directly.

---

## 4. Zone 2 Injection

After BFS, before the 5 checks. Injects all GLOBAL-zone nodes (drug safety constraints, hospital-wide policies) regardless of traversal path.

**Why after BFS?** Zone 2 nodes must still pass all 5 checks — an expired global node should still be excluded. Injecting before checks ensures this.

**Why not in BFS?** Global nodes are not part of any department's hierarchy — they'd never be reached by upward traversal from a leaf.

---

## 5. Five Sequential Checks

Each check takes the previous check's output as input. Sequential is mandatory — not parallel.

| Check | Logic | Why Sequential |
|-------|-------|----------------|
| 1. Isolation | `org_id == user.org_id` | Multi-tenant safety — foreign org nodes excluded first |
| 2. Compliance | `NOT (node.tags ∩ user.blocked_tags)` | MNPI nodes excluded before permission check |
| 3. Permission | `node.level >= user.ceiling` | Uses O(1) permission_map |
| 4. Temporal | `status != SUPERSEDED AND valid_until > NOW()` | Expired nodes excluded |
| 5. Derivability | `derivability_score < 0.7` | General knowledge excluded |

**Why sequential not parallel?** A compliance-excluded node (Check 2) should never reach the permission check (Check 3). Running in parallel would waste computation on already-excluded nodes and could cause security issues if checks interfere.

---

## 6. Candidate Set Assembly

Surviving nodes annotated with:
- `distance_from_entry` — from BFS distance map
- `compression_hint` — FULL (dist 0-1), COMPRESSED (dist 2), CONSTRAINT_ONLY (dist 3+)
- `type`, `importance`, `zone` — from node metadata

Output is a JSON array sorted by importance descending.

---

## Performance

| Stage | Current | Production Target |
|-------|---------|------------------|
| Permission compile | ~200ms | <15ms (cache levels) |
| BFS traversal | ~400ms | <50ms (batch query) |
| Zone 2 inject | ~200ms | <10ms (cached globals) |
| 5 checks | <1ms | <200ms |
| **Total** | **~800ms** | **<500ms** |

Current latency is dominated by Supabase round trips. Production optimization: batch all level queries into one call, cache Zone 2 nodes in memory, use connection pooling.

---

## Security Model

- **Silent exclusion** — unauthorized nodes simply absent, no HTTP 403
- **Permission before retrieval** — BFS fetches only reachable level IDs first, then nodes
- **ZERO LLM** — no AI model can hallucinate a permission decision
- **Compliance enforced at Check 2** — MNPI nodes never reach permission check