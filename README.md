# Brahmo: Hierarchical Access Control System

A secure, DAG-based access control system for managing hierarchical data permissions with audit logging and REST API capabilities.

## Features
- **Hierarchical Traversal:** Upward (ancestors) and Downward (sub-tree) navigation.
- **Security:** Logic-based permission compilation to prevent unauthorized access.
- **Audit Logging:** Every access attempt is logged for compliance.
- **REST API:** Fully functional FastAPI endpoints.

## Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set your `SUPABASE_URL` and `SUPABASE_KEY` in a `.env` file.
4. Run the API: `uvicorn main_api:app --reload`.