import logging
from typing import Tuple, Any

import requests

log = logging.getLogger(__name__)

class NextDNSAPIWrapper:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            'X-Api-Key': self.api_token
        }

    def _handle_server_response(self, response: dict) -> Tuple[str, Any]:
        data = response.get('data')

        if data is None:
            errors = response.get('errors', [])

            if len(errors) == 0:
                log.error('Unknown server error occured.')
                return 'error', None

            first_error = errors[0]
            error_code = first_error.get('code') # Get the error code
            log.error(f"Server returned error: Code={error_code}, Details={first_error}") # Log full error
            return 'error', error_code

        else:
            return 'success', data

    def get_rewrites(self, profile_id: str):
        url = f'https://api.nextdns.io/profiles/{profile_id}/rewrites'
        response = requests.get(
            url=url,
            headers=self.headers
        ).json()

        result, data = self._handle_server_response(response)
        if result == 'error':
            if data is None:
                return False
            elif data == 'notFound':
                raise ValueError(f'Profile ID \'{profile_id}\' not found.')
            else:
                log.error(f'Server returned unhandled error: {data}')
                return False

        return data

    def set_rewrite(self, profile_id: str, name: str, content: str):
        log.debug(f'Creating rewrite rule \'{name}\' with content \'{content}\' in profile \'{profile_id}\'...')

        url = f'https://api.nextdns.io/profiles/{profile_id}/rewrites'
        body = {
            'name': name,
            'content': content
        }
        response = requests.post(
            url=url,
            headers=self.headers,
            json=body
        ).json()

        result, data = self._handle_server_response(response)
        if result == 'error':
            if data is None:
                return False
            elif data == 'notFound':
                raise ValueError(f'Profile ID \'{profile_id}\' not found.')
            else:
                log.error(f'Server returned unhandled error: {data}')
                return False

        response_name = data.get('name', None)
        if response_name == name:
            log.debug(f'Successfully create rewrite rule \'{name}\' with content \'{content}\' in profile \'{profile_id}\'.')
            return True
        else:
            log.error(f'Failed to create rewrite rule \'{name}\' with content \'{content}\' in profile \'{profile_id}\'.')
            return True

    def delete_rewrite(self, profile_id: str, rule_id: str):
        log.debug(f'Removing rewrite rule \'{rule_id}\' in profile \'{profile_id}\'.')

        url = f'https://api.nextdns.io/profiles/{profile_id}/rewrites/{rule_id}'
        response = requests.delete(
            url=url,
            headers=self.headers
        )

        if response.status_code == 204:
            log.debug(f'Successfully removed rewrite rule \'{rule_id}\' in profile \'{profile_id}\'.')
            return True
        else:
            log.error(f'Failed to remove rewrite rule \'{rule_id}\' in profile \'{profile_id}\'.')
            return False