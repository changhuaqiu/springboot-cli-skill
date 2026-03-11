#!/usr/bin/env python3
"""
Generate HTTP client module for Spring Boot CLI.
Usage: python3 generate_http_client.py --auth-type <type> --output <path>
"""
import argparse


def generate_http_client(auth_type: str = "none") -> str:
    """Generate HTTP client code based on authentication type."""

    auth_imports = ""
    auth_init = ""
    auth_headers = ""

    if auth_type == 'bearer':
        auth_imports = "\nimport os"
        auth_init = """        self.auth_token = os.getenv('API_AUTH_TOKEN', '')
        self.token_expiry = None"""
        auth_headers = """        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'"""
    elif auth_type == 'api-key':
        auth_imports = "\nimport os"
        auth_init = """        self.api_key = os.getenv('API_KEY', '')"""
        auth_headers = """        if self.api_key:
            headers['X-API-Key'] = self.api_key"""
    elif auth_type == 'basic':
        auth_imports = "\nimport os\nfrom requests.auth import HTTPBasicAuth"
        auth_init = """        self.username = os.getenv('API_USERNAME', '')
        self.password = os.getenv('API_PASSWORD', '')"""
        auth_headers = """        auth = None
        if self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)"""

    return f'''\"\"\"HTTP Client for API calls with authentication support.\"\"\"
import os
from typing import Dict, Any, Optional{auth_imports}
import requests


class HTTPClient:
    \"\"\"HTTP client for API calls with authentication support.\"\"\"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('API_BASE_URL', 'http://localhost:8080')
{auth_init}
        self.session = requests.Session()
        self.timeout = int(os.getenv('API_TIMEOUT', '30'))

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        \"\"\"Make an HTTP request to the API.\"\"\"
        url = f\"{{self.base_url}}{{path}}\"
        headers = headers or {{}}
        headers['Content-Type'] = 'application/json'{auth_headers}

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return {{'success': True, 'data': response.json()}}
        except requests.exceptions.HTTPError as e:
            return {{
                'success': False,
                'error': f'HTTP {{e.response.status_code}}: {{e.response.text}}',
                'status_code': e.response.status_code
            }}
        except requests.exceptions.RequestException as e:
            return {{
                'success': False,
                'error': f'Request failed: {{str(e)}}'
            }}

    def get(self, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.request('GET', path, params=params)

    def post(self, path: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.request('POST', path, json_data=json_data)

    def put(self, path: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.request('PUT', path, json_data=json_data)

    def patch(self, path: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.request('PATCH', path, json_data=json_data)

    def delete(self, path: str) -> Dict[str, Any]:
        return self.request('DELETE', path)
'''


def main():
    parser = argparse.ArgumentParser(description='Generate HTTP client module')
    parser.add_argument('--auth-type', choices=['none', 'bearer', 'api-key', 'basic'],
                        default='none', help='Authentication type')
    parser.add_argument('--output', default='http_client.py',
                        help='Output file path')
    args = parser.parse_args()

    code = generate_http_client(args.auth_type)
    with open(args.output, 'w') as f:
        f.write(code)

    print(f"Generated HTTP client with auth type: {args.auth_type}")
    print(f"Output: {args.output}")


if __name__ == '__main__':
    main()
