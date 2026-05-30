# backend/permission_compiler.py

def compile_permissions(user_id, node_id, db):
    """
    Checks if a user is permitted to access a specific node
    based on their ceiling level and compliance clearance.
    """
    # 1. Fetch user details
    user = db.table('users').select('*').eq('id', user_id).single().execute().data
    
    # 2. Fetch the node's hierarchy level
    node = db.table('knowledge_nodes').select('hierarchy_level_id').eq('id', node_id).single().execute().data
    level_info = db.table('hierarchy_levels').select('level_number').eq('id', node['hierarchy_level_id']).single().execute().data
    
    # 3. Check access logic
    # Rule: If user's ceiling_level >= node's level_number, access is granted
    if user['ceiling_level'] >= level_info['level_number']:
        return True, "Access Granted"
    
    return False, "Access Denied: Insufficient Clearance"