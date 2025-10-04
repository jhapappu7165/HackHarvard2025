from supabase import create_client, Client
from config import Config

class SupabaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance.client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
        return cls._instance
    
    def get_client(self) -> Client:
        return self.client

# Singleton instance
supabase_client = SupabaseClient().get_client()