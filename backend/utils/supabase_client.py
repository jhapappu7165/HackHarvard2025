from supabase import create_client, Client
from config import Config
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton pattern for Supabase client"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            try:
                cls._client = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        return cls._instance
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            self._client.table('energy_buildings').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False