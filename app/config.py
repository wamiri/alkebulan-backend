from app.environment import get_env_var

DATABASE_URL = get_env_var("DATABASE_URL")
TMP_FILES_DIR = get_env_var("TMP_FILES_DIR")
