# main.py
from supabase import create_client
import os
from backend.traversal import get_reachable_nodes
from backend.permission_compiler import compile_permissions

# Initialize your Supabase client
url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_SERVICE_ROLE_KEY"
db = create_client(url, key)

def check_access(user_id, entry_node):
    # Get all nodes the user can technically reach via hierarchy
    reachable = get_reachable_nodes(entry_node, db)
    
    # Check if a specific node is in the reachable list and allowed
    # (Simplified example)
    allowed, message = compile_permissions(user_id, entry_node, db)
    
    print(f"User {user_id} -> Node {entry_node}: {message}")

# Example: Check if Nurse Priya can see a specific node
# check_access('U-PRIYA', 'N-03')
