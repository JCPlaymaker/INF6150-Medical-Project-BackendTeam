import toml
from pathlib import Path


class Config:
    def __init__(self, config_file: str = "config.toml"):
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file '{config_file}'"
                                    " not found.")

        config_data = toml.load(config_path)
        self.test_data = config_data.get("test_data", {})

    def get_test_data_paths(self):
        return self.test_data
