def compile_permissions(user, hierarchy_levels):
    """
    O(1) lookup: {level_id: can_read}
    
    Rule: User can read a level if:
    - They are ADMIN (read all), OR
    - The level is in their own department (BFS already scoped reach), OR
    - The level has no department (cross-org) AND level_number >= ceiling, OR
    - The level_number >= their ceiling
    """
    role = user.get("role", "VIEWER")
    ceiling = user.get("ceiling_level", 15)
    user_dept = user.get("department")

    permission_map = {}

    for level in hierarchy_levels:
        level_id = level["id"]
        level_number = level.get("level_number", 15)
        level_dept = level.get("department")

        if role == "ADMIN":
            permission_map[level_id] = True

        elif role == "HOD":
            # HOD sees all levels in their department + cross-org at ceiling+
            if level_dept == user_dept or level_dept is None:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number >= ceiling

        elif role in ("EDITOR", "QUALITY"):
            if level_dept == user_dept or level_dept is None:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number >= ceiling

        else:
            # VIEWER: own department levels always readable (BFS scoped reach)
            # Other departments: only at ceiling or below
            if level_dept == user_dept:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number >= ceiling

    return permission_map