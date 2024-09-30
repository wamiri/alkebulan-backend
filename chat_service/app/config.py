import os

from dotenv import load_dotenv

load_dotenv()


def get_env_var(env_var: str, default: str | None = None) -> str:
    if os.getenv(env_var) is None:
        if default is None:
            raise ValueError(f"Environment variable '{env_var}' is not set.")

        return default

    return os.environ[env_var]


APP_URL = get_env_var("APP_URL", "localhost:8000")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
QDRANT_API_KEY = get_env_var("QDRANT_API_KEY")
QDRANT_API_URL = get_env_var("QDRANT_API_URL")
