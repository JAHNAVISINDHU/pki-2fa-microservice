#!/usr/bin/env python3
import pyotp
import base64
import datetime
import os

SEED_FILE = "/data/seed.txt"

def read_seed():
    if not os.path.exists(SEED_FILE):
        return None
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

def generate_totp(seed_hex):
    # Convert hex string to bytes
    seed_bytes = bytes.fromhex(seed_hex)
    # Encode bytes to base32 string
    seed_base32 = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(seed_base32)
    return totp.now()

def main():
    seed = read_seed()
    if not seed:
        print(f"{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S} - No seed found.")
        return
    code = generate_totp(seed)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
