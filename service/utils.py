import yaml


def read_config(config_path: str) -> dict:
    with open(config_path, "r") as file:
        cfg = yaml.load(file, Loader=yaml.SafeLoader)
        return cfg
