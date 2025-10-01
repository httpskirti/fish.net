"""
Configuration settings for FishNet Marine Biodiversity Platform
"""
import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # Use Supabase PostgreSQL as primary database  
    # URL encode the password: * becomes %2A, \ becomes %5C
    SUPABASE_DB_URL = f"postgresql://postgres:TxZaUr%5C%2Aki3AZvX9@db.ehduimetxekjnsafoupw.supabase.co:5432/postgres"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or SUPABASE_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'geojson'}
    
    # AI/ML API Keys
    GEMINI_API_KEY = 'AIzaSyBqrpEqa8dcN-LGm74cPdwyTjGrvn8sv0Y'
    
    # Supabase settings
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://ehduimetxekjnsafoupw.supabase.co'
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZHVpbWV0eGVram5zYWZvdXB3Iiwicm9sZSI6ImFub24iLCJpXCI6InVwYW1hdHVyZXZhbHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MjEwNzgsImV4cCI6MjA3NDI5NzA3OH0.DhowGooRASMJcg1VefFd831RlHDx-hP5XFsZ8gedZK8'
    
    # Image settings
    SPECIES_IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'images', 'species')
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.SPECIES_IMAGES_FOLDER, exist_ok=True)