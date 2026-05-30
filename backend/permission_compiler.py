def compile_permissions(user_id, node_id, supabase_client):
    """
    Checks user permissions for a specific node.
    """
    try:
        # 1. Fetch the node to verify it exists
        # NOTE: Updated to table 'nodes' to match your schema
        response = supabase_client.table('nodes')\
            .select('id')\
            .eq('id', node_id)\
            .execute()
        
        if not response.data:
            return False, f"Error: Node {node_id} does not exist in the 'nodes' table."

        # 2. Check if the user has an explicit permission record
        perm_response = supabase_client.table('user_permissions')\
            .select('access_level')\
            .eq('user_id', user_id)\
            .eq('node_id', node_id)\
            .execute()

        if not perm_response.data:
            return False, f"Access Denied: No permission record found for user {user_id} on {node_id}."

        return True, "Access Granted."

    except Exception as e:
        return False, f"Database Error: {str(e)}"