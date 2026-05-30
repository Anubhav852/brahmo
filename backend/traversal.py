def get_reachable_nodes(entry_node_id, supabase_client):
    """
    Performs BFS to traverse the DAG upward to find all ancestors.
    Optimized to handle parent-child relationships efficiently.
    """
    visited = set()
    queue = [entry_node_id]
    
    while queue:
        current_id = queue.pop(0)
        
        if current_id not in visited:
            visited.add(current_id)
            
            try:
                # Fetch only the parent_id for the current node
                # Note: Adjust 'parent_id' column name if your schema uses an array
                response = supabase_client.table('nodes')\
                    .select('parent_id')\
                    .eq('id', current_id)\
                    .execute()
                
                # Check for valid data
                if response.data:
                    for row in response.data:
                        # Handle case where parent_id might be None for root nodes
                        p_id = row.get('parent_id')
                        if p_id and p_id not in visited:
                            queue.append(p_id)
            
            except Exception as e:
                print(f"Error traversing DAG at node {current_id}: {e}")
                continue
    
    return list(visited)

def get_children_of_node(parent_node_id, supabase_client):
    """
    Retrieves all direct children for a node.
    """
    try:
        response = supabase_client.table('nodes')\
            .select('id')\
            .eq('parent_id', parent_node_id)\
            .execute()
            
        return [row['id'] for row in response.data] if response.data else []
    except Exception as e:
        print(f"Error fetching children for parent {parent_node_id}: {e}")
        return []