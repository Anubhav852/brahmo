from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users")
async def get_users():
    """Returns all 7 users for the frontend dropdown"""
    from main import db
    resp = db.table("users").select("id, name, role, department, ceiling_level").execute()
    return resp.data or []

@app.get("/pipeline/{user_id}")
async def run_pipeline_endpoint(user_id: str):
    """Runs the full pipeline for a given user"""
    return run_pipeline(user_id)