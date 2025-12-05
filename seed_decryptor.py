import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os

# Load student private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Load encrypted seed
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

# Base64 decode
encrypted_seed_bytes = base64.b64decode(encrypted_seed_b64)

# Decrypt using RSA/OAEP SHA-256
decrypted_bytes = private_key.decrypt(
    encrypted_seed_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Convert bytes to string (hex seed)
decrypted_seed = decrypted_bytes.decode("utf-8")

# Validate it is exactly 64 hex characters
if len(decrypted_seed) != 64 or not all(c in "0123456789abcdef" for c in decrypted_seed):
    raise ValueError("Decrypted seed is invalid!")

# Save to persistent storage (Docker volume)
os.makedirs("data", exist_ok=True)
with open("data/seed.txt", "w") as f:
    f.write(decrypted_seed)

print("✅ Decrypted seed saved to data\\seed.txt")
