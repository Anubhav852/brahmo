# backend/filters.py

def check_dept_match(user_id, node_id, db):
    # Logic: Fetch user department and node department from DB
    # Return True if they match
    return True 

def check_temporal_validity(node_id, db):
    # Logic: Check if the node's 'expiry_date' is still valid
    return True

def check_compliance(user_id, node_id, db):
    # Logic: Check if node has 'MNPI' flag that user isn't cleared for
    return True

def is_highly_derivable(node_id, db):
    # Logic: Check if the node content is 'General Knowledge' (to filter out noise)
    return False

def check_user_constraints(user_id, node_id, db):
    # Logic: Any specific user-level blocking rules
    return True