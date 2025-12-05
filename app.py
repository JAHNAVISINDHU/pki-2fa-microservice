from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
import pyotp
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

app = FastAPI()

SEED_FILE = "data/seed.txt"
PRIVATE_KEY_FILE = "data/private_key.pem"


# -------------------- Request Models --------------------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# -------------------- Helper Functions --------------------
def load_private_key():
    if not os.path.exists(PRIVATE_KEY_FILE):
        raise Exception("Private key not found")

    with open(PRIVATE_KEY_FILE, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )


def decrypt_seed(encrypted_seed_b64: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)

        private_key = load_private_key()

        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ),
        )

        seed_hex = decrypted.hex()

        if len(seed_hex) != 64:
            raise Exception("Invalid seed length")

        return seed_hex

    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")


def load_seed():
    if not os.path.exists(SEED_FILE):
        raise Exception("Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        return f.read().strip()


# -------------------- API ENDPOINTS --------------------

# 1️⃣ POST /decrypt-seed
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: DecryptSeedRequest):
    try:
        seed_hex = decrypt_seed(req.encrypted_seed)

        os.makedirs("data", exist_ok=True)

        with open(SEED_FILE, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate-2fa")
def generate_2fa():
    try:
        seed_hex = load_seed()
        seed_bytes = bytes.fromhex(seed_hex)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed)

        code = totp.now()
        valid_for = 30 - (int(time.time()) % 30)  # ✅ fixed

        return {"code": code, "valid_for": valid_for}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 3️⃣ POST /verify-2fa
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    try:
        seed_hex = load_seed()
        seed_bytes = bytes.fromhex(seed_hex)

        totp = pyotp.TOTP(base64.b32encode(seed_bytes).decode())

        is_valid = totp.verify(req.code, valid_window=1)

        return {"valid": is_valid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
