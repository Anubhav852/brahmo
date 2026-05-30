def get_reachable_nodes(entry_node_id, supabase_client):
    """
    Performs a Breadth-First Search (BFS) to traverse the DAG 
    upward from the entry node to find all ancestor nodes.
    """
    visited = set()
    queue = [entry_node_id]
    
    while queue:
        current_id = queue.pop(0)
        
        if current_id not in visited:
            visited.add(current_id)
            
            try:
                # Fetch the parent of the current node
                response = supabase_client.table('nodes')\
                    .select('parent_id')\
                    .eq('id', current_id)\
                    .execute()
                
                if response.data:
                    for row in response.data:
                        parent_id = row.get('parent_id')
                        if parent_id and parent_id not in visited:
                            queue.append(parent_id)
                            
            except Exception as e:
                print(f"Error fetching parent for node {current_id}: {e}")
                continue
    
    return list(visited)

def get_children_of_node(parent_node_id, supabase_client):
    """
    Finds all direct children of a specific node by searching
    where the current node's ID is the parent_id.
    """
    try:
        response = supabase_client.table('nodes')\
            .select('id')\
            .eq('parent_id', parent_node_id)\
            .execute()
        
        # Return a list of child IDs
        return [row['id'] for row in response.data]
    except Exception as e:
        print(f"Error fetching children for node {parent_node_id}: {e}")
        return []