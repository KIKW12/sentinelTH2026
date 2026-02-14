import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

if not url or "your_supabase_url" in url:
    print("Warning: SUPABASE_URL not set properly in .env")

if not key or "your_supabase_service_key" in key:
    print("Warning: SUPABASE_SERVICE_KEY not set properly in .env")

supabase: Client = create_client(url, key)
