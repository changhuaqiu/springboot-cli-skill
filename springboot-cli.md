# Spring Boot REST API to CLI Generator

## Description

Generate a production-ready CLI wrapper for Spring Boot REST APIs using OpenAPI/Swagger documentation. The CLI enables AI agents to interact with your Spring Boot services through structured command-line interfaces.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--openapi-url` | string | No | `http://localhost:8080/v3/api-docs` | URL to OpenAPI/Swagger JSON endpoint |
| `--openapi-file` | string | No | - | Path to local OpenAPI JSON/YAML file |
| `--server-base-url` | string | No | `http://localhost:8080` | Base URL for API calls |
| `--output-dir` | string | No | `./cli-harness` | Output directory for generated CLI |
| `--package-name` | string | No | `cli-anything-{app-name}` | Python package name |
| `--cli-name` | string | No | `cli-anything-myapp` | CLI command name |
| `--auth-type` | string | No | `none` | Auth type: none, bearer, api-key, basic |
| `--include-tags` | string | No | - | Comma-separated tag filters |
| `--generate-tests` | bool | No | true | Generate test files |

## Usage

```bash
# Generate CLI from running Spring Boot app
/skill springboot-cli --openapi-url http://localhost:8080/v3/api-docs \
    --cli-name cli-anything-myapp

# Generate from local OpenAPI file
/skill springboot-cli --openapi-file ./openapi.json \
    --cli-name cli-anything-product-api

# With authentication
/skill springboot-cli --openapi-url https://api.example.com/v3/api-docs \
    --server-base-url https://api.example.com \
    --auth-type bearer \
    --cli-name cli-anything-api
```

## Generated CLI Features

- ✅ **Click-based CLI** with --help auto-discovery
- ✅ **JSON output mode** (--json flag) for AI consumption
- ✅ **Interactive REPL** for multi-command sessions
- ✅ **Authentication support** (Bearer token, API key, Basic)
- ✅ **Error handling** with structured responses
- ✅ **Configuration file** for persistent settings
- ✅ **Comprehensive tests** (unit + E2E)
- ✅ **setup.py** for pip installation

## CLI Usage Examples

```bash
# Install the generated CLI
cd cli-harness && pip install -e .

# Basic usage
cli-anything-myapp user get --id 123

# JSON output for AI
cli-anything-myapp --json user list --page 1 --size 10

# Interactive REPL
cli-anything-myapp
myapp> user create --name "Alice" --email "alice@example.com"
myapp> user get --id 123
myapp> exit
```

## Implementation

The skill performs the following steps:

1. **Fetch/Parse OpenAPI Spec** - Load from URL or local file
2. **Analyze Endpoints** - Extract operations, parameters, schemas
3. **Generate CLI Structure** - Create Click commands for each operation
4. **Generate HTTP Client** - Wrapper for requests with auth
5. **Generate REPL** - Interactive session management
6. **Generate Tests** - Unit and E2E test suites
7. **Generate setup.py** - For pip installation

---

## SKILL IMPLEMENTATION

```python
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
import requests

# Configuration from skill parameters
OPENAPI_URL = "{{openapi_url}}"
OPENAPI_FILE = "{{openapi_file}}"
SERVER_BASE_URL = "{{server_base_url}}"
OUTPUT_DIR = "{{output_dir}}"
PACKAGE_NAME = "{{package_name}}"
CLI_NAME = "{{cli_name}}"
AUTH_TYPE = "{{auth_type}}"
INCLUDE_TAGS = "{{include_tags}}"
GENERATE_TESTS = "{{generate_tests}}"

def fetch_openapi_spec() -> Dict[str, Any]:
    """Fetch OpenAPI spec from URL or load from file."""
    if OPENAPI_FILE:
        with open(OPENAPI_FILE, 'r') as f:
            if OPENAPI_FILE.endswith('.yaml') or OPENAPI_FILE.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
            return json.load(f)
    else:
        response = requests.get(OPENAPI_URL)
        response.raise_for_status()
        return response.json()

def normalize_name(name: str) -> str:
    """Convert operationId to CLI-friendly name."""
    # Replace camelCase with snake-case
    name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name)
    return name.lower().replace('_', '-')

def get_app_name(spec: Dict[str, Any]) -> str:
    """Extract app name from OpenAPI spec."""
    title = spec.get('info', {}).get('title', 'MyApp')
    return re.sub(r'[^a-zA-Z0-9-]', '-', title).lower()

def generate_http_client(auth_type: str) -> str:
    """Generate HTTP client module."""
    auth_imports = ""
    auth_init = ""
    auth_headers = ""

    if auth_type == 'bearer':
        auth_imports = "\nimport jwt\nfrom datetime import datetime, timedelta"
        auth_init = """        self.auth_token = os.getenv('API_AUTH_TOKEN', '')
        self.token_expiry = None"""
        auth_headers = """        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'"""
    elif auth_type == 'api-key':
        auth_init = """        self.api_key = os.getenv('API_KEY', '')"""
        auth_headers = """        if self.api_key:
            headers['X-API-Key'] = self.api_key"""
    elif auth_type == 'basic':
        auth_imports = "\nfrom requests.auth import HTTPBasicAuth"
        auth_init = """        self.username = os.getenv('API_USERNAME', '')
        self.password = os.getenv('API_PASSWORD', '')"""
        auth_headers = """        if self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)"""

    return f'''\"\"\"HTTP Client for {CLI_NAME}\"\"\"
import os
from typing import Dict, Any, Optional{auth_imports}
import requests


class HTTPClient:
    \"\"\"HTTP client for API calls with authentication support.\"\"\"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('API_BASE_URL', '{SERVER_BASE_URL}'){auth_init}
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

def generate_cli_command(
    operation_id: str,
    path: str,
    method: str,
    summary: str,
    parameters: List[Dict[str, Any]],
    request_body: Optional[Dict[str, Any]],
    tags: List[str]
) -> str:
    """Generate a single CLI command."""
    cmd_name = normalize_name(operation_id)
    tag = tags[0] if tags else 'default'

    # Build parameter declarations
    params_decls = []
    params_dict = []
    query_params = []

    for param in parameters:
        param_name = param['name']
        param_type = param.get('schema', {}).get('type', 'string')
        required = param.get('required', False)
        default = param.get('schema', {}).get('default', '')
        description = param.get('description', '')
        location = param.get('in', 'query')  # path, query, header

        if location == 'path':
            params_decls.append(f'    {param_name}: str = None')
            params_dict.append(f'        if {param_name} is None:')
            params_dict.append(f'            raise click.ClickException("--{param_name} is required for path parameter")')
        else:  # query
            if default:
                params_decls.append(
                    f"    {param_name}: {param_type} = None"
                )
            elif required:
                params_decls.append(f"    {param_name}: {param_type}")
                query_params.append(f"'{param_name}': {param_name},")
            else:
                params_decls.append(
                    f"    {param_name}: {param_type} = None"
                )
                if not required:
                    query_params.append(f"'{param_name}': {param_name},")

    # Build request body parameters
    if request_body:
        schema = request_body.get('content', {}).get('application/json', {}).get('schema', {})
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get('type', 'string')
                prop_required = prop_name in schema.get('required', [])
                if prop_required:
                    params_decls.append(f"    {prop_name}: {prop_type}")
                else:
                    params_decls.append(f"    {prop_name}: {prop_type} = None")

    # Build function call
    function_body = []

    # Build path parameters
    path_template = path
    for param in parameters:
        if param.get('in') == 'path':
            param_name = param['name']
            path_template = path_template.replace(f'{{{param_name}}}', f'{{{param_name}}}')

    # Build query parameters
    if query_params:
        function_body.append(f"        query_params = {{' '.join(query_params)}}")

    # Build request body
    if request_body:
        schema = request_body.get('content', {}).get('application/json', {}).get('schema', {})
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            function_body.append("        body_data = {")
            for prop_name, prop_def in properties.items():
                function_body.append(f"            '{prop_name}': {prop_name},")
            function_body.append("        }")

    # Build the method call
    method_lower = method.lower()
    if method_lower in ['post', 'put', 'patch']:
        if request_body:
            function_body.append(f"        response = client.{method_lower}('{path_template}', json_data=body_data)")
        else:
            function_body.append(f"        response = client.{method_lower}('{path_template}')")
    elif query_params:
        function_body.append(f"        response = client.{method_lower}('{path_template}', params=query_params)")
    else:
        function_body.append(f"        response = client.{method_lower}('{path_template}')")

    return f'''@{tag}.command(name='{cmd_name}', help='{summary or cmd_name}')
{', '.join(params_decls)}
def {operation_id.replace('-', '_')}_cmd({', '.join(['ctx', 'json_mode'] + [p.split(':')[0] for p in params_decls])}):
    \"\"\"{summary or cmd_name}\"\"\"
    client = ctx.obj['client']
{chr(10).join(function_body)}

    if response.get('success'):
        if json_mode:
            click.echo(json.dumps(response['data'], indent=2))
        else:
            click.echo(json.dumps(response['data'], indent=2, default=str))
    else:
        click.echo(f"Error: {{response.get('error')}}", err=True)
        raise click.exceptions.Exit(1)
'''

def generate_cli_module(spec: Dict[str, Any]) -> str:
    """Generate the main CLI module."""
    app_name = get_app_name(spec)

    # Extract tags and group operations
    tags = set()
    operations_by_tag: Dict[str, List[Dict[str, Any]]] = {}

    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method.upper() not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                continue

            operation_tags = operation.get('tags', ['default'])
            if INCLUDE_TAGS:
                include_list = [t.strip() for t in INCLUDE_TAGS.split(',')]
                if not any(tag in include_list for tag in operation_tags):
                    continue

            for tag in operation_tags:
                tags.add(tag)
                if tag not in operations_by_tag:
                    operations_by_tag[tag] = []

                operations_by_tag[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'operationId': operation.get('operationId', f"{method}_{path.replace('/', '_')}"),
                    'summary': operation.get('summary', ''),
                    'parameters': operation.get('parameters', []),
                    'requestBody': operation.get('requestBody'),
                    'tags': operation_tags,
                })

    # Generate tag groups
    tag_groups = []
    for tag in sorted(tags):
        operations = operations_by_tag.get(tag, [])
        tag_groups.append(f'''{tag} = click.Group(name='{tag}', help='{tag} operations')''')

    # Generate commands for each tag
    command_generations = []
    for tag, operations in operations_by_tag.items():
        command_generations.append(f"\n# {tag} commands")
        for op in operations:
            command_generations.append(
                generate_cli_command(
                    op['operationId'],
                    op['path'],
                    op['method'],
                    op['summary'],
                    op['parameters'],
                    op['requestBody'],
                    op['tags']
                )
            )

    return f'''\"\"\"{CLI_NAME} - CLI for {app_name} Spring Boot API\"\"\"
import json
import os
from typing import Optional

import click

from .http_client import HTTPClient


# Global JSON mode flag
json_mode = False


class Config:
    \"\"\"Configuration context.\"\"\"
    def __init__(self):
        self.client = HTTPClient()


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.version_option(version='1.0.0')
@click.option('--config', type=click.Path(), help='Path to config file')
@click.option('--base-url', type=str, help='API base URL')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON for AI consumption')
@pass_config
def cli(config: Config, config: Optional[str], base_url: Optional[str], json_output: bool):
    \"\"\"{CLI_NAME} - CLI wrapper for {app_name} API.

    Use --json flag to get structured output for AI agents.
    Enter bare command to start interactive REPL mode.
    \"\"\"
    global json_mode
    json_mode = json_output

    if base_url:
        config.client = HTTPClient(base_url)
    elif config and os.path.exists(config):
        # Load config file
        with open(config) as f:
            import yaml
            cfg = yaml.safe_load(f)
            if 'base_url' in cfg:
                config.client = HTTPClient(cfg['base_url'])


{chr(10).join(tag_groups)}

{chr(10).join(command_generations)}

# Add tag groups to main CLI
{chr(10).join([f'cli.add_command({tag})' for tag in sorted(tags)])}


def main():
    \"\"\"Entry point.\"\"\"
    if len(os.sys.argv) == 1:
        # No arguments - enter REPL mode
        start_repl()
    else:
        cli()


def start_repl():
    \"\"\"Start interactive REPL mode.\"\"\"
    from .repl import ReplSkin
    repl = ReplShell(cli, cli_name='{CLI_NAME}')
    repl.cmdloop()


if __name__ == '__main__':
    main()
'''

def generate_repl_module() -> str:
    """Generate REPL shell module."""
    return f'''\"\"\"Interactive REPL shell for {CLI_NAME}.\"\"\"
import cmd
import shlex
from typing import Dict, Any

import click


class ReplShell(cmd.Cmd):
    \"\"\"Interactive REPL shell for CLI commands.\"\"\"

    def __init__(self, cli_group, cli_name: str):
        super().__init__()
        self.cli_group = cli_group
        self.cli_name = cli_name
        self.prompt = f'{{cli_name}}> '
        self.intro = self._get_banner()

    def _get_banner(self) -> str:
        \"\"\"Get REPL banner.\"\"\"
        return f'''
╔══════════════════════════════════════════╗
║       {{self.cli_name}} v1.0.0          ║
║     CLI for Spring Boot API              ║
╚══════════════════════════════════════════╝

Type 'help' for available commands or 'exit' to quit.
'''

    def default(self, line: str):
        \"\"\"Execute CLI command.\"\"\"
        try:
            # Parse and execute the command
            args = shlex.split(line)
            if args:
                # Inject into Click CLI
                import sys
                old_argv = sys.argv
                try:
                    sys.argv = [self.cli_name] + args
                    self.cli_group.main(standalone_mode=False)
                except click.exceptions.Exit as e:
                    if e.exit_code != 0:
                        click.echo(f"Command failed with exit code: {{e.exit_code}}", err=True)
                except SystemExit:
                    pass
                finally:
                    sys.argv = old_argv
        except Exception as e:
            click.echo(f"Error: {{str(e)}}", err=True)

    def do_exit(self, arg: str):
        \"\"\"Exit the REPL.\"\"\"
        click.echo("Goodbye! 👋")
        return True

    def do_clear(self, arg: str):
        \"\"\"Clear the screen.\"\"\"
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

    def emptyline(self):
        \"\"\"Do nothing on empty line.\"\"\"
        pass
'''

def generate_config_module() -> str:
    """Generate configuration module."""
    return f'''\"\"\"Configuration management for {CLI_NAME}.\"\"\"
import os
from pathlib import Path
from typing import Dict, Any

import yaml


DEFAULT_CONFIG = {{
    'base_url': '{SERVER_BASE_URL}',
    'timeout': 30,
}}


def get_config_dir() -> Path:
    \"\"\"Get the config directory.\"\"\"
    home = Path.home()
    config_dir = home / '.{CLI_NAME}'
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    \"\"\"Get the config file path.\"\"\"
    return get_config_dir() / 'config.yaml'


def load_config() -> Dict[str, Any]:
    \"\"\"Load configuration from file.\"\"\"
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    \"\"\"Save configuration to file.\"\"\"
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def init_config() -> None:
    \"\"\"Initialize default configuration.\"\"\"
    config_dir = get_config_dir()
    config_path = get_config_path()

    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        print(f"Config initialized at: {{config_path}}")
    else:
        print("Config already exists at: {{config_path}}")
'''

def generate_tests(spec: Dict[str, Any]) -> str:
    """Generate test module."""
    app_name = get_app_name(spec)

    return f'''\"\"\"Tests for {CLI_NAME}.\"\"\"
import json
import os
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests
from click.testing import CliRunner

from cli_anything_{app_name}.cli import cli
from cli_anything_{app_name}.http_client import HTTPClient


# Fixtures
@pytest.fixture
def mock_client():
    \"\"\"Mock HTTP client.\"\"\"
    client = Mock(spec=HTTPClient)
    client.base_url = 'http://test-api'
    client.timeout = 30
    return client


@pytest.fixture
def runner():
    \"\"\"Click CLI runner.\"\"\"
    return CliRunner()


# Unit Tests
class TestHTTPClient:
    \"\"\"Tests for HTTPClient.\"\"\"

    @patch('cli_anything_{app_name}.http_client.requests.Session.request')
    def test_get_request_success(self, mock_request):
        \"\"\"Test successful GET request.\"\"\"
        mock_response = Mock()
        mock_response.json.return_value = {{'status': 'ok'}}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = HTTPClient(base_url='http://test-api')
        result = client.get('/test')

        assert result['success'] is True
        assert result['data'] == {{'status': 'ok'}}

    @patch('cli_anything_{app_name}.http_client.requests.Session.request')
    def test_post_request_success(self, mock_request):
        \"\"\"Test successful POST request.\"\"\"
        mock_response = Mock()
        mock_response.json.return_value = {{'id': 1}}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = HTTPClient(base_url='http://test-api')
        result = client.post('/test', json_data={{'name': 'test'}})

        assert result['success'] is True
        assert result['data'] == {{'id': 1}}

    @patch('cli_anything_{app_name}.http_client.requests.Session.request')
    def test_http_error_handling(self, mock_request):
        \"\"\"Test HTTP error handling.\"\"\"
        mock_response = Mock()
        mock_response.text = 'Not Found'
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        mock_request.side_effect = requests.exceptions.HTTPError(response=mock_response)

        client = HTTPClient(base_url='http://test-api')
        result = client.get('/not-found')

        assert result['success'] is False
        assert '404' in result['error']

    @patch('cli_anything_{app_name}.http_client.requests.Session.request')
    def test_timeout_handling(self, mock_request):
        \"\"\"Test timeout handling.\"\"\"
        mock_request.side_effect = requests.exceptions.Timeout()

        client = HTTPClient(base_url='http://test-api')
        result = client.get('/slow-endpoint')

        assert result['success'] is False
        assert 'Request failed' in result['error']


# Integration Tests (require running API)
@pytest.mark.integration
class TestCLIIntegration:
    \"\"\"Integration tests for CLI (requires API running).\"\"\"

    base_url = os.getenv('TEST_API_URL', 'http://localhost:8080')

    @patch('cli_anything_{app_name}.cli.HTTPClient')
    def test_help_command(self, mock_http_client_class):
        \"\"\"Test help command.\"\"\"
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert '{CLI_NAME}' in result.output

    @patch('cli_anything_{app_name}.cli.HTTPClient')
    def test_json_output(self, mock_http_client_class):
        \"\"\"Test JSON output mode.\"\"\"
        mock_client = Mock()
        mock_client.get.return_value = {{
            'success': True,
            'data': {{'status': 'ok'}}
        }}
        mock_http_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(cli, ['--json', 'health', 'check'])

        assert result.exit_code == 0
        # Verify JSON can be parsed
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


# E2E Tests (require actual API)
@pytest.mark.e2e
class TestE2E:
    \"\"\"End-to-end tests.\"\"\"

    @pytest.fixture(autouse=True)
    def setup(self):
        \"\"\"Check if API is available.\"\"\"
        base_url = os.getenv('TEST_API_URL', 'http://localhost:8080')
        try:
            response = requests.get(f'{{base_url}}/actuator/health', timeout=5)
            if response.status_code != 200:
                pytest.skip("API not available")
        except Exception:
            pytest.skip("API not available")

    def test_api_health_check(self):
        \"\"\"Test API health check.\"\"\"
        base_url = os.getenv('TEST_API_URL', 'http://localhost:8080')
        response = requests.get(f'{{base_url}}/actuator/health', timeout=5)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''

def generate_setup_py(spec: Dict[str, Any]) -> str:
    """Generate setup.py for pip installation."""
    app_name = get_app_name(spec)
    package_name_safe = app_name.replace('-', '_')

    return f'''\"\"\"Setup configuration for {CLI_NAME}.\"\"\"
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='{CLI_NAME}',
    version='1.0.0',
    description='CLI wrapper for {app_name} Spring Boot API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='CLI-Anything',
    python_requires='>=3.8',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
    ],
    extras_require={{
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
        ],
    }},
    entry_points={{
        'console_scripts': [
            '{CLI_NAME}=cli_anything_{package_name_safe}.cli:main',
        ],
    }},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
'''

def generate_readme(spec: Dict[str, Any]) -> str:
    """Generate README.md."""
    app_name = get_app_name(spec)

    # Collect available commands
    commands = []
    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                operation_id = operation.get('operationId', '')
                summary = operation.get('summary', '')
                if operation_id:
                    commands.append(f"- `{operation_id}`: {summary}")

    return f'''# {CLI_NAME}

CLI wrapper for {app_name} Spring Boot API. Generated by CLI-Anything Spring Boot skill.

## Installation

```bash
cd cli-harness
pip install -e .
```

## Configuration

Create a config file at `~/.{CLI_NAME}/config.yaml`:

```yaml
base_url: http://localhost:8080
timeout: 30
```

Or set environment variables:

```bash
export API_BASE_URL=http://localhost:8080
export API_TIMEOUT=30
```

## Usage

### Basic Commands

```bash
# Show help
{CLI_NAME} --help

# List available commands for a group
{CLI_NAME} <tag-name> --help

# Execute a command
{CLI_NAME} <command-group> <command> [options]
```

### JSON Output (for AI Agents)

```bash
{CLI_NAME} --json <command-group> <command> [options]
```

### Interactive REPL Mode

```bash
{CLI_NAME}
```

## Available Commands

{chr(10).join(commands[:20]) if commands else 'No commands documented'}

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=cli_anything_{app_name.replace("-", "_")} --cov-report=html

# Format code
black .
```

## License

MIT License
'''

def generate_all_files(spec: Dict[str, Any], output_dir: str) -> None:
    """Generate all CLI files."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    app_name = get_app_name(spec)
    package_name_safe = app_name.replace('-', '_')
    package_dir = output_path / 'cli_anything' / package_name_safe
    package_dir.mkdir(exist_ok=True, parents=True)

    # Create __init__.py
    (package_dir / '__init__.py').write_text(f'"""cli_anything_{package_name_safe} package"""')

    # Create http_client.py
    (package_dir / 'http_client.py').write_text(generate_http_client(AUTH_TYPE))

    # Create cli.py
    (package_dir / 'cli.py').write_text(generate_cli_module(spec))

    # Create repl.py
    (package_dir / 'repl.py').write_text(generate_repl_module())

    # Create config.py
    (package_dir / 'config.py').write_text(generate_config_module())

    # Create tests directory
    tests_dir = package_dir / 'tests'
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / '__init__.py').write_text('"""Tests"""')
    (tests_dir / 'test_cli.py').write_text(generate_tests(spec))

    # Create setup.py
    (output_path / 'setup.py').write_text(generate_setup_py(spec))

    # Create README.md
    (output_path / 'README.md').write_text(generate_readme(spec))

    # Create pyproject.toml
    (output_path / 'pyproject.toml').write_text('''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "cli-anything-app"
version = "1.0.0"
requires-python = ">=3.8"
''')

    # Create requirements.txt
    (output_path / 'requirements.txt').write_text('''click>=8.0.0
requests>=2.28.0
pyyaml>=6.0
''')

    # Create requirements-dev.txt
    (output_path / 'requirements-dev.txt').write_text('''click>=8.0.0
requests>=2.28.0
pyyaml>=6.0
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
''')

# Main execution
def main():
    spec = fetch_openapi_spec()
    generate_all_files(spec, OUTPUT_DIR)

    print(f"✅ CLI generated successfully!")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"📦 Package name: {CLI_NAME}")
    print(f"\nNext steps:")
    print(f"  cd {OUTPUT_DIR}")
    print(f"  pip install -e .")
    print(f"  {CLI_NAME} --help")
    print(f"\n⚠️  Don't forget to:")
    print(f"  1. Set your API_BASE_URL in ~/.{CLI_NAME}/config.yaml")
    print(f"  2. Configure authentication if needed")
    print(f"  3. Run tests: pytest")

if __name__ == '__main__':
    main()
```

---

## Examples

### Generate from running Spring Boot app

```bash
/skill springboot-cli --openapi-url http://localhost:8080/v3/api-docs \
    --cli-name cli-anything-user-api
```

### Generate with API Key authentication

```bash
/skill springboot-cli --openapi-url https://api.example.com/v3/api-docs \
    --server-base-url https://api.example.com \
    --auth-type api-key \
    --cli-name cli-anything-api
```

### Generate specific tag groups only

```bash
/skill springboot-cli --openapi-url http://localhost:8080/v3/api-docs \
    --include-tags "users,products,orders" \
    --cli-name cli-anything-shop-api
```

---

## Notes

- Requires Spring Boot 3.x with SpringDoc OpenAPI
- Generated CLI uses Click and requests libraries
- Supports Python 3.8+
- JSON output mode (--json) is optimized for AI agent consumption
- REPL mode provides interactive multi-command sessions
