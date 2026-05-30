RESTRICTED_TAGS = {"MNPI", "CONFIDENTIAL", "PHI", "LEGAL_HOLD"}


def compile_permissions(user, hierarchy_levels):
    """
    O(1) lookup: {level_id: can_read}

    The DAG goes from root (L1) DOWN to leaf nodes (L10, L12).
    Lower level_number = higher in tree = more privileged.
    Higher level_number = deeper in tree = more specific/restricted.

    "ceiling_level" = the DEEPEST level a user can see.
    Priya ceiling=10 → can read L1, L3, L5, L8, L10 (anything <= 10).
                        Cannot read L12 patient-level nodes.
    Vikram (HOD) ceiling=4 → can read L1, L3 only for cross-dept.
                              But reads ALL ortho levels (his own dept).
    Admin Suresh ceiling=1 → reads everything.

    Rule: can_read = level_number <= user.ceiling_level
    Exception: HOD/EDITOR/QUALITY read ALL levels in their own department.
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
            # ADMIN reads everything
            permission_map[level_id] = True

        elif role == "HOD":
            # HOD reads all levels in own dept
            # + shared/global levels (no dept) within ceiling
            # + other depts only within ceiling
            if level_dept == user_dept:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number <= ceiling

        elif role in ("EDITOR", "QUALITY"):
            # Same as HOD for read permissions
            if level_dept == user_dept:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number <= ceiling

        elif role == "AUDITOR":
            permission_map[level_id] = level_number <= ceiling

        else:
            # VIEWER: ceiling-gated for ALL levels including own dept
            # Priya (VIEWER, L10, Ortho) can read L1-L10, not L12 patient nodes
            permission_map[level_id] = level_number <= ceiling

    return permission_map