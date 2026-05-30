import os
from dotenv import load_dotenv
from supabase import create_client
from backend.traversal import get_reachable_nodes, get_children_of_node
from backend.permission_compiler import compile_permissions
from backend.data_manager import get_content_for_nodes
from backend.logger import log_access
from backend.db_config import db

# Load environment variables from the .env file in the root
load_dotenv()

# Initialize your Supabase client using environment variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in the .env file.")
    db = None
else:
    db = create_client(url, key)
    print("Successfully initialized Supabase client!")

def get_user_dashboard(user_id, entry_node):
    """
    1. Checks if the user has access.
    2. If allowed, retrieves and prints all authorized content.
    3. Logs all access attempts to the audit system.
    4. Displays immediate child nodes for the entry node.
    """
    if db is None:
        print("Cannot proceed: Supabase client not initialized.")
        return

    # Check permission first
    allowed, message = compile_permissions(user_id, entry_node, db)
    print(f"Access Check: {message}")

    if allowed:
        # Get all reachable nodes (upward/ancestors)
        reachable_nodes = get_reachable_nodes(entry_node, db)
        
        # Fetch the actual content for those nodes
        content = get_content_for_nodes(reachable_nodes, db)
        
        # Log successful access for every node reached
        for node_id in reachable_nodes:
            log_access(user_id, node_id, "READ_SUCCESS", db)
        
        print(f"User {user_id} has access to {len(content)} pieces of content:")
        for item in content:
            print(f" - [{item['node_id']}] {item['title']}: {item['body']}")
        
        # --- NEW: Display child hierarchy (downward) ---
        children = get_children_of_node(entry_node, db)
        if children:
            print(f"Sub-nodes under {entry_node}: {', '.join(children)}")
        else:
            print(f"No sub-nodes found under {entry_node}.")
    else:
        # Log failed access attempt
        log_access(user_id, entry_node, "READ_DENIED", db)
        print(f"Access denied for user {user_id}.")

# Main execution block
if __name__ == "__main__":
    # Test the dashboard retrieval
    get_user_dashboard('U-PRIYA', 'N-03')