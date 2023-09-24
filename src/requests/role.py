from src.mongodb import ROLE_TABLE

role = ROLE_TABLE.find_one({'role': 'auth_user'})
role_auth_id = str(role['_id']) if role else ROLE_TABLE.find_one({'role': 'auth_user'})

role_admin = ROLE_TABLE.find_one({'role': 'admin'})
role_admin_id = str(role_admin['_id']) if role_admin else ROLE_TABLE.find_one({'role': 'admin'})


def add_default_role():
    roles = [
        {"role": "admin"},
        {"role": "manager"},
        {"role": "premium_user"},
        {"role": "auth_user"},
    ]
    for role in roles:
        if not ROLE_TABLE.find_one(role):
            ROLE_TABLE.insert_one(role)
