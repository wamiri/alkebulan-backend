from app.environment import get_env_var

APP_URL = get_env_var("APP_URL", "localhost:8000")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
QDRANT_API_KEY = get_env_var("QDRANT_API_KEY")
QDRANT_API_URL = get_env_var("QDRANT_API_URL")
AWS_ACCESS_KEY_ID = get_env_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_var("AWS_SECRET_ACCESS_KEY")
AWS_OPENSEARCH_HOST = get_env_var("AWS_OPENSEARCH_HOST")
AWS_OPENSEARCH_REGION = get_env_var("AWS_OPENSEARCH_REGION")
