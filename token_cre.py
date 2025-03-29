import secrets

# Generate a random secret key
secret_key = secrets.token_hex(32)
print(f"Your JWT secret key: {secret_key}")
