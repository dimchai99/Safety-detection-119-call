import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("SUPABASE_DB_URL not set")

DEVICE_SHARED_SECRET = os.getenv("DEVICE_HMAC_SECRET", "device-shared-secret")
PORT = int(os.getenv("PORT", 5000))
