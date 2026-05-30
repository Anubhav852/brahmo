def compile_permissions(user, hierarchy_levels):
    """
    Builds O(1) lookup hashmap compiled ONCE per session.
    
    Input:  user record + all hierarchy levels
    Output: {hierarchy_level_id: True/False} — can this user read this level?
    
    Rule:
    - ADMIN: can read everything
    - HOD/EDITOR/QUALITY: can read levels where level_number >= user ceiling_level
    - VIEWER: can read levels where level_number >= user ceiling_level
    """
    role = user.get("role", "VIEWER")
    ceiling = user.get("ceiling_level", 15)
    
    permission_map = {}
    
    for level in hierarchy_levels:
        level_id = level["id"]
        level_number = level.get("level_number", 15)
        
        if role == "ADMIN":
            permission_map[level_id] = True
        else:
            # User can read this level if level_number >= their ceiling
            # (higher number = lower in hierarchy = less sensitive)
            permission_map[level_id] = level_number >= ceiling
    
    return permission_map