from supabase import Client, create_client

from env import SUPABASE_KEY, SUPABASE_URL


supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
