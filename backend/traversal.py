from collections import deque

def get_reachable_nodes(entry_level_id, supabase_client):
    """
    BFS upward through hierarchy_levels DAG.
    Returns dict: {hierarchy_level_id: distance_from_entry}
    """
    visited = {}   # {level_id: distance}
    queue = deque()
    queue.append((entry_level_id, 0))

    # First load ALL hierarchy levels into memory (one DB call)
    response = supabase_client.table("hierarchy_levels").select("id, parent_ids").execute()
    level_map = {row["id"]: row.get("parent_ids") or [] for row in response.data}

    while queue:
        current_id, distance = queue.popleft()
        if current_id in visited:
            continue
        visited[current_id] = distance

        # Walk UP to parents
        for parent_id in level_map.get(current_id, []):
            if parent_id not in visited:
                queue.append((parent_id, distance + 1))

    return visited  # {level_id: distance}


def inject_zone2_nodes(supabase_client):
    """
    Fetch all Zone 2 (GLOBAL) nodes — injected after BFS, before 5 checks.
    Returns list of node dicts.
    """
    response = supabase_client.table("knowledge_nodes")\
        .select("*")\
        .eq("zone", 2)\
        .execute()
    return response.data or []