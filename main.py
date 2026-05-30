import os
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes, get_children_of_node
from backend.permission_compiler import compile_permissions
from backend.data_manager import get_content_for_nodes
from backend.logger import log_access

# Load environment variables
load_dotenv()

# Initialize Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
db = create_client(url, key) if url and key else None

def process_dashboard_request(user_id, entry_node):
    """
    Core logic: Checks permissions, fetches content, logs access, 
    and gathers navigation options.
    Returns a dictionary ready to be converted to JSON.
    """
    if db is None:
        return {"status": "error", "message": "Database not initialized"}

    # 1. Check permission
    allowed, message = compile_permissions(user_id, entry_node, db)
    
    if not allowed:
        log_access(user_id, entry_node, "READ_DENIED", db)
        return {"status": "denied", "message": message}

    # 2. Get data
    reachable_nodes = get_reachable_nodes(entry_node, db)
    content = get_content_for_nodes(reachable_nodes, db)
    children = get_children_of_node(entry_node, db)

    # 3. Log access
    for node_id in reachable_nodes:
        log_access(user_id, node_id, "READ_SUCCESS", db)

    # 4. Return structured data
    return {
        "status": "granted",
        "content": content,
        "authorized_nodes": children,
        "current_node": entry_node
    }

# Main execution block for local testing
if __name__ == "__main__":
    result = process_dashboard_request('U-PRIYA', 'N-03')
    print(result)