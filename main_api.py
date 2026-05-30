from fastapi import FastAPI
from backend.traversal import get_reachable_nodes
from backend.data_manager import get_content_for_nodes
from backend.permission_compiler import compile_permissions
from backend.db_config import db

app = FastAPI()

@app.get("/dashboard/{user_id}/{node_id}")
async def get_dashboard(user_id: str, node_id: str):
    # Reuse your existing logic!
    allowed, message = compile_permissions(user_id, node_id, db)
    if not allowed:
        return {"status": "denied", "message": message}
    
    reachable = get_reachable_nodes(node_id, db)
    content = get_content_for_nodes(reachable, db)
    
    return {
        "status": "granted",
        "authorized_nodes": reachable,
        "content": content
    }