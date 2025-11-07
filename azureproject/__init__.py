import os

def load_config():
    """Load configuration based on environment"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        from . import production
        return production
    else:
        from . import development
        return development
