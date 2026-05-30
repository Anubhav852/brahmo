import os
import time
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes, get_children_of_node
from backend.permission_compiler import compile_user_permissions # Updated import
from backend.data_manager import get_content_for_nodes
from backend.logger import log_access
from backend.filters import (
    check_dept_match, check_temporal_validity, 
    check_compliance, is_highly_derivable, check_user_constraints
)

load_dotenv()

db = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def process_dashboard_request(user_id, entry_node):
    start_time = time.perf_counter()

    # 1. O(1) Permission Compilation (Run once!)
    # This hashmap {node_id: access_level} allows O(1) checks for all subsequent filters
    permission_map = compile_user_permissions(user_id, db)
    
    if not permission_map:
        log_access(user_id, entry_node, "READ_DENIED", db)
        return {"status": "denied", "message": "No permissions found for user."}

    # 2. BFS Traversal
    initial_nodes = get_reachable_nodes(entry_node, db)
    
    # 3. Sequential 5-Check Filter Pipeline
    # We pass the permission_map into relevant filters instead of querying DB
    current_pool = initial_nodes
    stats = {"initial": len(initial_nodes)}

    # Step 1: Dept Isolation
    current_pool = [n for n in current_pool if check_dept_match(user_id, n, db)]
    stats["after_dept"] = len(current_pool)

    # Step 2: Compliance/MNPI (Using the compiled map for O(1) check)
    current_pool = [n for n in current_pool if n in permission_map]
    stats["after_compliance"] = len(current_pool)
    
    # Step 3: Temporal Validity
    current_pool = [n for n in current_pool if check_temporal_validity(n, db)]
    stats["after_temporal"] = len(current_pool)
    
    # Step 4: Derivability
    current_pool = [n for n in current_pool if not is_highly_derivable(n, db)]
    stats["after_derivability"] = len(current_pool)
    
    # Step 5: User Constraints
    current_pool = [n for n in current_pool if check_user_constraints(user_id, n, db)]
    stats["final"] = len(current_pool)

    duration = (time.perf_counter() - start_time) * 1000

    # 4. Final Content Fetch
    content = get_content_for_nodes(current_pool, db)
    children = get_children_of_node(entry_node, db)

    log_access(user_id, entry_node, "READ_SUCCESS", db)

    return {
        "status": "granted",
        "funnel_stats": stats,
        "pipeline_ms": round(duration, 2),
        "content": content,
        "authorized_nodes": children,
        "current_node": entry_node
    }