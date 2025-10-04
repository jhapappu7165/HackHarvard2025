import os

class Config:
    # Supabase Configuration
    SUPABASE_URL = "https://xewxswcnymeeyrykvrnz.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhld3hzd2NueW1lZXlyeWt2cm56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NjQwNDIsImV4cCI6MjA3NTE0MDA0Mn0.JzwDe6D7MtgP75QbUlwoMsFIaG3WlcSdPL1wxI9t2Hk"
    
    # Data Generation Settings
    NUM_BUILDINGS = 15
    NUM_MONTHS = 24  # 2 years of data
    
    # Energy Types
    FUEL_TYPES = ['electricity', 'natural_gas', 'oil', 'propane']
    
    # Building Categories
    BUILDING_CATEGORIES = ['School', 'Library', 'Administration', 'Public Works', 'Public Safety']