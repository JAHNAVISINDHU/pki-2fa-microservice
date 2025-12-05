import pyotp
import base64
import time

# Load hex seed
with open("data/seed.txt", "r") as f:
    hex_seed = f.read().strip()

# Convert hex to bytes
seed_bytes = bytes.fromhex(hex_seed)

# Convert to base32 (required for TOTP)
base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

# Create TOTP object
totp = pyotp.TOTP(base32_seed, digits=6, interval=30)  # SHA-1 by default

# Generate current TOTP code
current_code = totp.now()

# Calculate seconds remaining in current period
time_remaining = totp.interval - (int(time.time()) % totp.interval)

print(f"Current TOTP code: {current_code}")
print(f"Valid for: {time_remaining} seconds")
