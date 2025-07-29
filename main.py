import os
import logging
import time

from config import Config
from query_public_ip import QueryPublicIp
from api_wrapper import NextDNSAPIWrapper

CONFIG_PATH = '/config.json'
LOG_LEVEL_ENV = os.getenv('LOG_LEVEL', 'INFO').upper()
VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

log = logging.getLogger('main')

if LOG_LEVEL_ENV in VALID_LOG_LEVELS:
    logging_level = getattr(logging, LOG_LEVEL_ENV)
else:
    logging_level = logging.INFO # Default to INFO if environment variable is invalid
    log.warning(f"Invalid LOG_LEVEL '{LOG_LEVEL_ENV}' provided. Defaulting to INFO.")

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging_level,
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

log.info(f'Starting NextDNS Rewrite Updater...')

config_wrapper = Config(CONFIG_PATH)
query = QueryPublicIp()
config = config_wrapper.get_config()

log.info(f'NextDNS Rewrite Updater initialized.')

def main_loop():
    current_ip = query.query_public_ip()

    for account in config.get('accounts', []):
        api_token = account.get('apiToken', '')
        profiles = account.get('profiles', [])
        wrapper = NextDNSAPIWrapper(api_token)

        for profile in profiles:
            profile_id = profile.get('profileId', '')
            config_rewrites = profile.get('rewrites', [])
            current_rewrites = wrapper.get_rewrites(profile_id)

            for config_rewrite in config_rewrites:
                config_name = config_rewrite.get('name', None)
                current_name = None
                current_content = None
                current_id = None

                if not config_name:
                    log.error(f'Invalid rewrite rule: \'{config_rewrite}\'. Skipping current rule...')
                    continue

                for current_rewrite in current_rewrites:
                    name = current_rewrite.get('name', None)
                    content = current_rewrite.get('content', None)
                    id = current_rewrite.get('id', None)

                    if name == config_name:
                        current_name = name
                        current_content = content
                        current_id = id
                        break

                if not current_name:
                    log.info(f'Rewrite rule \'{config_name}\' in profile \'{profile_id}\' is not set. Setting a new one...')
                    wrapper.set_rewrite(profile_id, config_name, current_ip)

                elif current_content != current_ip:
                    log.info(f'Updating rewrite rule \'{config_name}\' in profile \'{profile_id}\' with new IP \'{current_ip}\'...')
                    wrapper.delete_rewrite(profile_id, current_id)
                    wrapper.set_rewrite(profile_id, config_name, current_ip)

                else:
                    log.debug(f'Skipping rewrite rule \'{config_name}\' in profile \'{profile_id}\' since it has same IP address...')


def main():
    interval_seconds = config.get('checkInterval', 60)
    log.info(f'Checking status every {interval_seconds} seconds...')
    log.info(f'{len(config.get('accounts', []))} NextDNS accounts detected.')

    while True:
        try:
            main_loop()
        except Exception as e:
            log.error(f'Error occured: {e}')

        time.sleep(interval_seconds)

if __name__ == '__main__':
    main()