from src import mongodb


role_table = mongodb.mongo.get_collection('role')


def add_default_role():
    roles = [
        {"role": "admin"},
        {"role": "manager"},
        {"role": "premium_user"},
        {"role": "auth_user"},
    ]
    for role in roles:
        if not role_table.find_one(role):
            role_table.insert_one(role)
