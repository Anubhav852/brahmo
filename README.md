# BRAHMO Rules Engine
## BFS Traversal + 5-Check Filter Pipeline — ZERO LLM

Deterministic Rules Engine Pipeline for secure clinical knowledge retrieval and context filtering. Built using FastAPI, Supabase, React, and PostgreSQL with DAG traversal, hierarchical permission enforcement, BFS-based filtering, and zero LLM involvement.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js v18+
- Supabase account (free tier)

### Backend Setup
```bash
git clone https://github.com/Anubhav852/brahmo
cd brahmo
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env         # add your Supabase URL and KEY
uvicorn main:app --reload --port 8000
```

### Database Setup
1. Create a Supabase project at supabase.com
2. Go to SQL Editor
3. Run `supabase/schema.sql`
4. Run `supabase/seed.sql`
5. Verify: `SELECT COUNT(*) FROM knowledge_nodes` → 50
6. Verify: `SELECT COUNT(*) FROM users` → 7

### Frontend Setup
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

---

## What This Builds

A Rules Engine pipeline that:
1. Traverses a Directed Acyclic Graph (DAG) of knowledge nodes upward from a user's entry point
2. Injects globally-relevant Zone 2 nodes (drug safety constraints, hospital-wide policies)
3. Applies 5 sequential checks to filter down to a candidate set of 12-42 nodes
4. All deterministically — ZERO LLM involvement

### The Pipeline

User opens session (role: VIEWER, ceiling: L10, dept: Ortho Ward)
→ Permission Compiler     — O(1) lookup compiled once from cache
→ Entry Point Resolver    — maps dept to DAG leaf node
→ BFS Traversal           — walks UP the DAG via parent_ids (pure Python, zero DB)
→ Zone 2 Injection        — global safety nodes added after BFS
→ 5 Sequential Checks:
Check 1: Isolation    — org_id match
Check 2: Compliance   — MNPI/clearance tags
Check 3: Permission   — hierarchy ceiling
Check 4: Temporal     — not expired/superseded
Check 5: Derivability — score < 0.7
→ Candidate Set           — annotated nodes with metadata

### Performance

All DB fetches happen ONCE at server startup in parallel. Zero DB calls during requests.

| User | Role | Ceiling | Final Nodes | Pipeline Time |
|---|---|---|---|---|
| Nurse Priya | VIEWER | L10 | 16 | 0.32ms |
| Dr. Vikram | HOD | L4 | 12 | 0.13ms |
| Admin Suresh | ADMIN | L1 | 42 | 0.34ms |

**Total pipeline time: <1ms** (spec target: <500ms)

### Different Users, Different Results

The same graph, same 50 nodes, completely different candidate sets based on who is asking:

- **Priya** sees only Ortho + global safety nodes. Zero Cardiology, zero Paeds, zero MNPI nodes.
- **Vikram** sees Ortho dept decisions Priya cannot (lower ceiling). Still no MNPI+CONFIDENTIAL.
- **Suresh** sees all departments including MNPI/CONFIDENTIAL nodes (N-A01, N-A02, N-O11, N-O12, N-C04).

---

## Project Structure
```
brahmo/
├── main.py                     # FastAPI app + full pipeline + startup cache
├── main_api.py                 # Re-exports app (legacy shim)
├── permission_compiler.py      # O(1) permission hashmap
├── traversal.py                # BFS entry (original)
├── requirements.txt
├── .env.example
├── README.md
├── architecture.md             # BFS strategy + filter ordering rationale
├── data_sources.md             # Clinical data sources
├── backend/
│   ├── filters.py              # 5 sequential checks
│   ├── traversal.py            # BFS cached + original
│   └── permission_compiler.py
├── frontend/
│   └── src/
│       └── App.js              # React dashboard + funnel visualisation
├── supabase/
│   ├── schema.sql              # Database schema
│   └── seed.sql                # 50 nodes + 7 users
└── docs/
└── architecture.md
```

---

## Demo Scenarios

1. **Nurse Priya** — VIEWER, L10, Ortho → 16 nodes, Ortho + global safety only
2. **Dr. Vikram** — HOD, L4, Ortho → 12 nodes, sees dept-level decisions Priya cannot
3. **Admin Suresh** — ADMIN, L1 → 42 nodes, full hospital access including MNPI
4. **Zone 2 Toggle** — disable to remove global drug safety nodes and watch count drop
5. **Silent exclusion** — unauthorized nodes absent, no error messages, no 403s

---

## Key Design Decisions

- **ZERO LLM** — all filtering is deterministic, binary, rule-based
- **Startup cache** — all tables fetched once in parallel at boot, zero DB calls per request
- **Sequential checks** — output of check N is input to check N+1 (compliance before permission)
- **O(1) permission lookup** — compiled once per session into a hashmap, not per node
- **Silent exclusion** — unauthorized nodes simply absent, never a 403 or access denied
- **Zone 2 injection** — after BFS, before checks, so global nodes still go through all 5 filters
- **Pure Python BFS** — adjacency map built from parent_ids at startup, traversal is in-memory

## Security Model

- MNPI-tagged nodes invisible to users without compliance clearance
- Department isolation enforced at BFS level — Priya's traversal never reaches Cardiology
- Permission ceiling enforced at Check 3 — HOD decisions invisible to VIEWER
- Compliance check runs before permission check — excluded nodes never reach permission stage
- No indication of hidden nodes — silent exclusion throughout