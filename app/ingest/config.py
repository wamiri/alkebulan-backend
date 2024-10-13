from app.environment import get_env_var

OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
TMP_FILES_DIR = get_env_var("TMP_FILES_DIR")
UNSTRUCTURED_SERVER_URL = get_env_var("UNSTRUCTURED_SERVER_URL")
