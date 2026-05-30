# BRAHMO Rules Engine — Architecture Notes

## Pipeline Overview

The Rules Engine is a deterministic, zero-LLM pipeline that filters 50 knowledge
nodes down to a candidate set of 15-28 nodes specific to the requesting user.
Every decision is binary — include or exclude. No LLM is involved at any stage.

## Data Flow

User selects session
→ Permission Compiler (runs ONCE, O(1) lookup)
→ Entry Point Resolver (maps dept to DAG leaf node)
→ BFS Traversal (walks UP the DAG via parent_ids)
→ Zone 2 Injection (global nodes added after BFS)
→ 5 Sequential Checks (each output feeds next input)
→ Candidate Set output (annotated JSON)

## Key Components

### 1. Permission Compiler
Compiles user permissions ONCE at session start into a hashmap:
`{hierarchy_level_id: True/False}`
This gives O(1) lookup for all 500+ permission checks instead of N+1 DB queries.

### 2. Entry Point Resolver
Maps user's department and ceiling_level to their DAG leaf node.
Nurse Priya (Ortho, L10) → HL-10-ORTHO-W
Admin Suresh (Admin, L1) → HL-01 (root)

### 3. BFS Traversal
Starts at entry point, walks UPWARD through hierarchy_levels via parent_ids.
Uses a visited set to prevent re-processing multi-parent nodes.
Returns {level_id: distance_from_entry} for every reachable level.

### 4. Zone 2 Injection
After BFS, all zone=2 (GLOBAL) nodes are injected into the pool.
These are hospital-wide safety constraints that apply to every user.
They still go through all 5 checks — some may be excluded by compliance or derivability.
Position: AFTER BFS, BEFORE the 5 checks. This is intentional.

### 5. Five Sequential Checks

Each check takes the OUTPUT of the previous check as input.
Sequential, not parallel — Check 3 cannot run until Check 2 has excluded its nodes.

| Check | Rule | Why Sequential |
|-------|------|----------------|
| 1. Isolation | org_id must match | Multi-tenant safety first |
| 2. Compliance | No MNPI tags unless user has clearance | Compliance before permission |
| 3. Permission | hierarchy_level >= user ceiling | After compliance, more expensive |
| 4. Temporal | Not superseded, not expired | After permission narrows pool |
| 5. Derivability | score < 0.7 | Last — removes general knowledge |

## Why Checks Are Sequential, Not Parallel

A compliance-excluded node should never reach the permission check.
A permission-excluded node should never reach the temporal check.
Each check narrows the pool, making the next check faster and more meaningful.
Running in parallel would mean processing nodes that should have been eliminated earlier.

## Performance

- Permission compile: ~12ms (one DB call, O(1) lookups after)
- BFS traversal: ~45ms (one DB call for all levels)
- Zone 2 injection: ~8ms (one DB call)
- Five checks: ~30ms total (in-memory, no DB queries)
- Total: <100ms for 50 nodes (scales to <500ms for 842 nodes)

## Security Model

- Silent exclusion: unauthorized nodes are absent, not denied
- No HTTP 403 or "access denied" messages
- Permission check happens before data retrieval (no GAP 5 violation)
- ZERO LLM in the pipeline — all decisions are deterministic