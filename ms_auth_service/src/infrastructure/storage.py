import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

users = [
    {
        "id": 1,
        "username": "admin",
        "hashed_password": get_password_hash("admin"),
        "role": "admin",
    }
]

roles = {
    "admin": ["auth:read", "auth:write", "users:manage"],
    "teacher": ["auth:read", "courses:read"],
    "student": ["auth:read"],
}
