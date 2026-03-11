#!/usr/bin/env python3
"""
Generate CLI module from OpenAPI specification.
Usage: python3 generate_cli.py --openapi <spec> --output <path>
"""
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def normalize_name(name: str) -> str:
    """Convert operationId to CLI-friendly name."""
    # Replace camelCase with snake-case
    name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name)
    return name.lower().replace('_', '-')


def get_app_name(spec: Dict[str, Any]) -> str:
    """Extract app name from OpenAPI spec."""
    title = spec.get('info', {}).get('title', 'MyApp')
    return re.sub(r'[^a-zA-Z0-9-]', '-', title).lower()


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
    query_params = []

    for param in parameters:
        param_name = param['name']
        param_type = param.get('schema', {}).get('type', 'string')
        required = param.get('required', False)
        location = param.get('in', 'query')  # path, query, header

        if location == 'path':
            params_decls.append(f'    {param_name}: str = None')
        else:  # query
            if required:
                params_decls.append(f"    {param_name}: {param_type}")
                query_params.append(f"'{param_name}': {param_name},")
            else:
                params_decls.append(f"    {param_name}: {param_type} = None")
                query_params.append(f"'{param_name}': {param_name},")

    # Build request body parameters
    body_params = []
    if request_body:
        schema = request_body.get('content', {}).get('application/json', {}).get('schema', {})
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get('type', 'string')
                prop_required = prop_name in schema.get('required', [])
                if prop_required:
                    params_decls.append(f"    {prop_name}: {prop_type}")
                    body_params.append(f"            '{prop_name}': {prop_name},")
                else:
                    params_decls.append(f"    {prop_name}: {prop_type} = None")
                    body_params.append(f"            '{prop_name}': {prop_name},")

    # Build function body
    function_body = []
    path_template = path

    # Build path parameters
    for param in parameters:
        if param.get('in') == 'path':
            param_name = param['name']
            path_template = path_template.replace(f'{{{param_name}}}', f'{{{param_name}}}')

    # Build query parameters
    if query_params:
        function_body.append(f"        query_params = {{' '.join(query_params)}}")

    # Build request body
    if body_params:
        function_body.append("        body_data = {")
        function_body.extend(body_params)
        function_body.append("        }")

    # Build the method call
    method_lower = method.lower()
    if method_lower in ['post', 'put', 'patch']:
        if body_params:
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

    return f'''\"\"\"CLI wrapper for {app_name} API\"\"\"
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
    \"\"\"CLI wrapper for {app_name} API.

    Use --json flag to get structured output for AI agents.
    \"\"\"
    global json_mode
    json_mode = json_output

    if base_url:
        config.client = HTTPClient(base_url)


{chr(10).join(tag_groups)}

{chr(10).join(command_generations)}

# Add tag groups to main CLI
{chr(10).join([f'cli.add_command({tag})' for tag in sorted(tags)])}


def main():
    \"\"\"Entry point.\"\"\"
    cli()


if __name__ == '__main__':
    main()
'''


def main():
    parser = argparse.ArgumentParser(description='Generate CLI module from OpenAPI')
    parser.add_argument('--openapi', required=True,
                        help='Path to OpenAPI JSON file')
    parser.add_argument('--output', default='cli.py',
                        help='Output file path')
    args = parser.parse_args()

    with open(args.openapi) as f:
        spec = json.load(f)

    code = generate_cli_module(spec)
    with open(args.output, 'w') as f:
        f.write(code)

    print(f"Generated CLI module")
    print(f"Output: {args.output}")


if __name__ == '__main__':
    main()
