from collections import deque


def get_reachable_nodes(entry_level_id: str, supabase_client) -> dict:
    """
    Original BFS — kept for fallback/testing.
    Makes ONE DB call to load all levels, then pure Python BFS.
    Returns {hierarchy_level_id: distance_from_entry}
    """
    if not entry_level_id:
        return {}

    response = supabase_client.table("hierarchy_levels")\
        .select("id, parent_ids").execute()
    level_map = {
        row["id"]: row.get("parent_ids") or []
        for row in response.data
    }

    visited = {}
    queue = deque([(entry_level_id, 0)])

    while queue:
        current_id, distance = queue.popleft()
        if current_id in visited:
            continue
        visited[current_id] = distance
        for parent_id in level_map.get(current_id, []):
            if parent_id not in visited:
                queue.append((parent_id, distance + 1))

    return visited


def get_reachable_nodes_cached(entry_level_id: str, adjacency: dict) -> dict:
    """
    Cached BFS — ZERO DB calls.
    adjacency = {level_id: [parent_id, ...]} built once at startup.
    Returns {hierarchy_level_id: distance_from_entry}
    """
    if not entry_level_id:
        return {}

    visited = {}
    queue = deque([(entry_level_id, 0)])

    while queue:
        current_id, distance = queue.popleft()
        if current_id in visited:
            continue
        visited[current_id] = distance
        for parent_id in adjacency.get(current_id, []):
            if parent_id not in visited:
                queue.append((parent_id, distance + 1))

    return visited


def inject_zone2_nodes(supabase_client) -> list:
    """
    Original Zone 2 fetch — kept for fallback/testing.
    zone=2 is integer in seed data.
    """
    response = supabase_client.table("knowledge_nodes")\
        .select("*")\
        .eq("zone", 2)\
        .execute()
    return response.data or []


def inject_zone2_nodes_cached(global_nodes_cache: list) -> list:
    """
    Cached Zone 2 — ZERO DB calls.
    Returns pre-filtered global nodes list from startup cache.
    """
    return global_nodes_cache