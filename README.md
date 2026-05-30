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
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # add your Supabase URL and KEY
uvicorn main:app --reload --port 8000
```

### Database Setup:

1. Create a Supabase project at supabase.com
2. Go to SQL Editor
3. Run supabase/schema.sql
4. Run supabase/seed.sql
5. Verify: SELECT COUNT(*) FROM knowledge_nodes → 50
6. Verify: SELECT COUNT(*) FROM users → 7

### Frontend Setup
```bash
cd brahmo-frontend
npm install
npm start
# Opens at http://localhost:3000
```

---

## What This Builds

A Rules Engine pipeline that:
1. Traverses a Directed Acyclic Graph (DAG) of knowledge nodes upward from a user's entry point
2. Injects globally-relevant Zone 2 nodes (drug safety constraints, hospital-wide policies)
3. Applies 5 sequential checks to filter down to a candidate set of 15-40 nodes
4. All deterministically — ZERO LLM involvement

### The Pipeline:

User opens session (role: VIEWER, ceiling: L10, dept: Ortho Ward)
→ Permission Compiler (O(1) lookup for all 15 levels)
→ Entry Point Resolver (maps dept to DAG leaf node)
→ BFS Traversal (walks UP the DAG via parent edges)
→ Zone 2 Injection (global safety nodes added)
→ 5 Sequential Checks:
Check 1: Isolation    (org_id match)
Check 2: Compliance   (MNPI/clearance tags)
Check 3: Permission   (hierarchy ceiling)
Check 4: Temporal     (not expired/superseded)
Check 5: Derivability (score < 0.7)
→ Candidate Set (annotated nodes with metadata)

### Different Users, Different Results

| User | Role | Ceiling | Final Nodes |
|------|------|---------|-------------|
| Nurse Priya | VIEWER | L10 | ~16 |
| Dr. Vikram | HOD | L4 | ~18 |
| Admin Suresh | ADMIN | L1 | ~42 |

---

## Project Structure

```
brahmo/
├── main.py                    # FastAPI app + full pipeline
├── main_api.py                # API entry point
├── permission_compiler.py     # O(1) permission hashmap
├── traversal.py               # BFS + Zone 2 injection
├── requirements.txt
├── .env.example
├── README.md
├── architecture.md
├── data_sources.md
├── backend/
│   ├── filters.py             # 5 sequential checks
│   ├── traversal.py
│   └── permission_compiler.py
├── brahmo-frontend/
│   └── src/
│       └── App.js             # React dashboard
├── supabase/
│   ├── schema.sql             # Database schema
│   └── seed.sql               # 50 nodes + 7 users
└── docs/
    └── architecture.md        # Deep dive architecture
```

---

## Demo Scenarios

1. **Nurse Priya** — VIEWER, L10, Ortho → 16 nodes (Ortho + global safety only)
2. **Dr. Vikram** — HOD, L4, Ortho → 18 nodes (sees more dept decisions)
3. **Admin Suresh** — ADMIN, L1 → 42 nodes (full hospital access)
4. **Zone 2 Toggle** — Uncheck to remove global drug safety nodes (16 → 8)
5. **Silent exclusion** — Unauthorized nodes absent, no error messages

---

## Key Design Decisions

- **ZERO LLM** in the pipeline — all filtering is deterministic
- **Sequential checks** — output of check N is input to check N+1
- **O(1) permission lookup** — compiled once per session, not per node
- **Silent exclusion** — unauthorized nodes simply absent, no 403s
- **Zone 2 injection** — after BFS, before checks, so global nodes still filtered

