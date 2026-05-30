from datetime import datetime

def check_dept_match(user_id, node_id, db):
    # Fetch user's department
    user = db.table("users").select("department").eq("id", user_id).single().execute()
    # Fetch node's department
    node = db.table("nodes").select("department").eq("id", node_id).single().execute()
    
    return user.data["department"] == node.data["department"]

def check_temporal_validity(node_id, db):
    # Fetch node expiry date
    node = db.table("nodes").select("expiry_date").eq("id", node_id).single().execute()
    expiry_date = node.data["expiry_date"] # Expecting ISO format string
    
    return datetime.fromisoformat(expiry_date) > datetime.now()

def check_compliance(user_id, node_id, db):
    # Fetch user clearance and node MNPI status
    user = db.table("users").select("clearance_level").eq("id", user_id).single().execute()
    node = db.table("nodes").select("is_mnpi").eq("id", node_id).single().execute()
    
    # If node is MNPI, user clearance must be 'high'
    if node.data["is_mnpi"]:
        return user.data["clearance_level"] == "high"
    return True

def is_highly_derivable(node_id, db):
    # Check if node is marked as general knowledge (too basic/derivable)
    node = db.table("nodes").select("category").eq("id", node_id).single().execute()
    return node.data["category"] == "general_knowledge"

def check_user_constraints(user_id, node_id, db):
    # Custom rule: Check if node is on user's specific blocklist
    blocklist = db.table("user_constraints").select("blocked_node_id").eq("user_id", user_id).execute()
    blocked_ids = [row["blocked_node_id"] for row in blocklist.data]
    
    return node_id not in blocked_ids