import sys
from app.core.security import get_password_hash

if len(sys.argv) != 2:
    print("Usage: python scripts/hash_passwords.py <password>")
    sys.exit(1)

password = sys.argv[1]
hashed = get_password_hash(password)
print(f"Hashed: {hashed}")