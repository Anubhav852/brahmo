from datetime import datetime, timezone

def check_isolation(node, org_id):
    """Check 1: Node must belong to same org"""
    return node.get("org_id") == org_id

def check_compliance(node, user_compliance_clearance):
    """Check 2: MNPI-tagged nodes excluded if user has no clearance"""
    node_tags = node.get("compliance_tags") or []
    for tag in node_tags:
        if tag not in user_compliance_clearance:
            return False
    return True

def check_permission(node, permission_map):
    """Check 3: Node's hierarchy level must be >= user's ceiling level"""
    level_id = node.get("hierarchy_level_id")
    return permission_map.get(level_id, False)

def check_temporal(node):
    """Check 4: Exclude superseded and expired nodes"""
    if node.get("status") == "SUPERSEDED":
        return False
    valid_until = node.get("valid_until")
    if valid_until:
        expiry = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
        if expiry < datetime.now(timezone.utc):
            return False
    return True

def check_derivability(node):
    """Check 5: Exclude nodes with derivability_score >= 0.7"""
    score = node.get("derivability_score", 0)
    return float(score) < 0.7