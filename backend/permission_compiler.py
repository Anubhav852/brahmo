# RESTRICTED_TAGS are the compliance tags that gate access.
# Nodes with no tags, or tags like "ortho"/"medicine", are unrestricted.
RESTRICTED_TAGS = {"MNPI", "CONFIDENTIAL", "PHI", "LEGAL_HOLD"}


def compile_permissions(user, hierarchy_levels):
    """
    O(1) lookup: {level_id: can_read}

    Permission rule (from spec):
    - ADMIN: reads everything
    - HOD: reads all levels in own dept + shared/global levels (no dept), ceiling-gated for other depts
    - EDITOR / QUALITY: same as HOD
    - VIEWER: ceiling-gated for ALL levels including own dept
      (Priya at L10 cannot see L4 Ortho HOD decisions)

    "ceiling_level" means: user can read nodes whose hierarchy_level_number >= their ceiling.
    Lower number = higher in tree = more privileged.
    Priya ceiling=10  can read L10, L11, L12, L13, L14, L15 only.
    Vikram (HOD) ceiling=4  can read L4 and below in his dept.
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
            # HOD reads all levels in own dept (they manage the whole dept)
            # + shared/global levels (no department set)
            # + other depts only if at or below ceiling
            if level_dept == user_dept or level_dept is None:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number >= ceiling

        elif role in ("EDITOR", "QUALITY"):
            # Same as HOD for read permissions
            if level_dept == user_dept or level_dept is None:
                permission_map[level_id] = True
            else:
                permission_map[level_id] = level_number >= ceiling

        elif role == "AUDITOR":
            # AUDITOR reads everything (for compliance review) but ceiling-gated
            permission_map[level_id] = level_number >= ceiling

        else:
            # VIEWER: strictly ceiling-gated for ALL levels, including own dept
            # Priya (VIEWER, L10, Ortho) cannot see L4 Ortho HOD decisions
            permission_map[level_id] = level_number >= ceiling

    return permission_map