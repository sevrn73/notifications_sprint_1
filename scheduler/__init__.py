import logging.config
import os
from pathlib import Path

import yaml


# добавление конфигурации логгера
base_path = Path(__file__).resolve().parent.parent
conf_path = os.path.join(base_path, "logconf.yaml")

with open(conf_path, "r") as f:
    log_cfg = yaml.safe_load(f.read())

logging.config.dictConfig(log_cfg)
