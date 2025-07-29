import logging
import os
import sys
import json
import requests

log = logging.getLogger(__name__)

class QueryPublicIp:
    def __init__(self):
        debug_str = os.getenv('DEBUG', 'false')
        debug = True if debug_str.lower() == 'true' else False

        self.debug = debug

    def query_public_ip(self):
        ipv4 = self._fetch_ip_from_api('https://api4.ipify.org?format=json')
        ipv6 = self._fetch_ip_from_api('https://api6.ipify.org?format=json')

        if ipv6:
            return ipv6
        elif ipv4:
            return ipv4
        else:
            return None

    def _fetch_ip_from_api(self, api_url: str) -> str | None:
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()

            # Check if the response content is empty before trying to parse JSON
            if not response.text:
                return None

            data = response.json()
            return data.get('ip') # Use .get() to safely access 'ip' key, returns None if not found

        except (requests.exceptions.RequestException, json.JSONDecodeError, TypeError) as e:
            # Catch common request-related errors, JSON parsing errors, and TypeError if .json() fails on non-JSON
            # For future-proofing
            if self.debug:
                error_detail = getattr(e, 'msg', str(e))
                log.error(f'Error fetching ip from \'{api_url}\': {e} - {error_detail}', file=sys.stderr)
            return None

        except Exception as e:
            if self.debug:
                error_detail = getattr(e, 'msg', str(e))
                log.error(f'Error fetching ip from \'{api_url}\': {e} - {error_detail}', file=sys.stderr)
            return None