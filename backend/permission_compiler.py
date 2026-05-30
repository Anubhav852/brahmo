def compile_user_permissions(user_id, supabase_client):
    """
    Builds an O(1) lookup hashmap for all user permissions.
    Call this ONCE at the start of your request.
    """
    try:
        response = supabase_client.table('user_permissions')\
            .select('node_id, access_level')\
            .eq('user_id', user_id)\
            .execute()
        
        # Hashmap: {node_id: access_level}
        return {item['node_id']: item['access_level'] for item in response.data}
    except Exception as e:
        print(f"Error compiling permissions: {e}")
        return {}

def check_permission(node_id, permission_map):
    # O(1) lookup
    return node_id in permission_map