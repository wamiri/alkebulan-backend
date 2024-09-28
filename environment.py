import os


class Environment:
    def __init__(self, env_vars: list[str]) -> None:
        for env_var in env_vars:
            super().__setattr__(env_var, self.get_env_var(env_var))

    def get_env_var(self, env_var: str) -> str:
        if os.getenv(env_var) is None:
            raise ValueError(f"Environment variable '{env_var}' is not set.")

        return os.environ[env_var]
