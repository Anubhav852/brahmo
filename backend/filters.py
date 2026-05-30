from datetime import datetime, timezone

# Only these tags require explicit user clearance.
# Generic department tags like "ortho" or "medicine" are NOT compliance gates.
RESTRICTED_TAGS = {"MNPI", "CONFIDENTIAL", "PHI", "LEGAL_HOLD"}


def check_isolation(node, org_id):
    """Check 1: Node must belong to same org."""
    return node.get("org_id") == org_id


def check_compliance(node, user_compliance_clearance):
    """
    Check 2: Exclude nodes that have a RESTRICTED tag the user lacks clearance for.

    Only MNPI, CONFIDENTIAL, PHI, LEGAL_HOLD are compliance gates.
    Generic tags like 'ortho' or 'medicine' are not — they are department labels
    and should never block access.

    A node with zero restricted tags always passes.
    A node tagged MNPI passes only if user has MNPI in their compliance_clearance.
    """
    node_tags = set(node.get("compliance_tags") or [])
    restricted_on_node = node_tags & RESTRICTED_TAGS  # only the gating tags
    user_clearance = set(user_compliance_clearance or [])

    # If node has no restricted tags, it passes unconditionally
    if not restricted_on_node:
        return True

    # User must have clearance for every restricted tag on this node
    return restricted_on_node.issubset(user_clearance)


def check_permission(node, permission_map):
    """
    Check 3: Node's hierarchy level must be within user's ceiling.

    Zone 2 (GLOBAL) nodes are NOT exempt — they still go through permission check.
    A GLOBAL drug safety node above Priya's ceiling should still be excluded.
    The permission_map (compiled once at session start) handles this via O(1) lookup.
    """
    level_id = node.get("hierarchy_level_id")
    return permission_map.get(level_id, False)


def check_temporal(node):
    """Check 4: Exclude superseded and expired nodes."""
    if node.get("status") == "SUPERSEDED":
        return False
    valid_until = node.get("valid_until")
    if valid_until:
        expiry = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
        if expiry < datetime.now(timezone.utc):
            return False
    return True


def check_derivability(node):
    """Check 5: Exclude nodes the AI can already derive from general knowledge."""
    score = node.get("derivability_score", 0)
    return float(score) < 0.7