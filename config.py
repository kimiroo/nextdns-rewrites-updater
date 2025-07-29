import logging
import json

DEFAULT_CONFIG_PATH = '/config.json'

log = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path: str = None):
        if not config_path:
            config_path = DEFAULT_CONFIG_PATH

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_json = json.load(f)

        except Exception as e:
            log.critical(f'Failed to load config: {e}')
            exit(1)

    def get_config(self):
        return self.config_json