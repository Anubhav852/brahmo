# backend/traversal.py

def get_reachable_nodes(entry_node_id, supabase_client):
    """
    Performs a Breadth-First Search (BFS) to traverse the DAG 
    upward from the user's hierarchy level to find all 'parent' nodes.
    """
    visited = set()
    queue = [entry_node_id]
    
    while queue:
        current_id = queue.pop(0)
        
        if current_id not in visited:
            visited.add(current_id)
            
            # Fetch parents of the current hierarchy level
            # This looks at the hierarchy_levels table
            response = supabase_client.table('hierarchy_levels')\
                .select('parent_ids')\
                .eq('id', current_id)\
                .execute()
            
            for row in response.data:
                parents = row.get('parent_ids', [])
                for parent_id in parents:
                    if parent_id not in visited:
                        queue.append(parent_id)
    
    return list(visited)