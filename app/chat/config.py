from app.environment import get_env_var

APP_URL = get_env_var("APP_URL", "localhost:8000")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
QDRANT_API_KEY = get_env_var("QDRANT_API_KEY")
QDRANT_API_URL = get_env_var("QDRANT_API_URL")
