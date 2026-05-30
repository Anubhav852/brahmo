import os
import time
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes, get_children_of_node
from backend.permission_compiler import compile_permissions
from backend.data_manager import get_content_for_nodes
from backend.logger import log_access
# Import your filter functions here
from backend.filters import (
    check_dept_match, check_temporal_validity, 
    check_compliance, is_highly_derivable, check_user_constraints
)

# Load environment variables
load_dotenv()

# Initialize Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
db = create_client(url, key) if url and key else None

def process_dashboard_request(user_id, entry_node):
    if db is None:
        return {"status": "error", "message": "Database not initialized"}

    # Start timing for the assessment requirement
    start_time = time.perf_counter()

    # 1. Permission check
    allowed, message = compile_permissions(user_id, entry_node, db)
    if not allowed:
        log_access(user_id, entry_node, "READ_DENIED", db)
        return {"status": "denied", "message": message}

    # 2. Get initial node pool via BFS
    initial_nodes = get_reachable_nodes(entry_node, db)
    
    # 3. Sequential 5-Check Filter Pipeline
    current_pool = initial_nodes
    stats = {"initial": len(initial_nodes)}

    # Check 1: Department Isolation
    current_pool = [n for n in current_pool if check_dept_match(user_id, n, db)]
    stats["after_dept"] = len(current_pool)

    # Check 2: Temporal Validity
    current_pool = [n for n in current_pool if check_temporal_validity(n, db)]
    stats["after_temporal"] = len(current_pool)

    # Check 3: Compliance/MNPI
    current_pool = [n for n in current_pool if check_compliance(user_id, n, db)]
    stats["after_compliance"] = len(current_pool)
    
    # Check 4: Derivability
    current_pool = [n for n in current_pool if not is_highly_derivable(n, db)]
    stats["after_derivability"] = len(current_pool)
    
    # Check 5: User-level constraints
    current_pool = [n for n in current_pool if check_user_constraints(user_id, n, db)]
    stats["final"] = len(current_pool)

    # Calculate duration
    duration = (time.perf_counter() - start_time) * 1000 # in milliseconds

    # 4. Fetch final content
    content = get_content_for_nodes(current_pool, db)
    children = get_children_of_node(entry_node, db)

    # 5. Log success
    log_access(user_id, entry_node, "READ_SUCCESS", db)

    return {
        "status": "granted",
        "funnel_stats": stats,
        "pipeline_ms": round(duration, 2),
        "content": content,
        "authorized_nodes": children,
        "current_node": entry_node
    }