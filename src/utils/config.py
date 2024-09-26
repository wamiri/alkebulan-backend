import os

from dotenv import load_dotenv

load_dotenv()


def get_env_var(env_var: str) -> str:
    if os.getenv(env_var) is None:
        raise ValueError(f"Environment variable '{env_var}' is not set.")

    return os.environ[env_var]
