def log_access(user_id, node_id, action, supabase_client):
    """
    Records an access event into the audit_logs table.
    """
    try:
        supabase_client.table('audit_logs').insert({
            "user_id": user_id,
            "node_id": node_id,
            "action": action
        }).execute()
    except Exception as e:
        print(f"Warning: Failed to log access: {e}")