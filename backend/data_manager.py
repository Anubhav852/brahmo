def get_content_for_nodes(node_ids, supabase_client):
    """
    Fetches content for a list of node IDs.
    """
    if not node_ids:
        return []

    # Efficiently fetch all content matching the authorized IDs
    response = supabase_client.table('node_content')\
        .select('title, body, node_id')\
        .in_('node_id', node_ids)\
        .execute()
        
    return response.data