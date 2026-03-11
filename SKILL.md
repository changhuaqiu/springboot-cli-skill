---
name: springboot-cli
description: Generate a production-ready CLI wrapper for Spring Boot REST APIs using OpenAPI/Swagger documentation. This skill should be used when users want to create a command-line interface that enables AI agents to interact with Spring Boot services through structured commands.
---

# Spring Boot REST API to CLI Generator

## About This Skill

This skill transforms Spring Boot REST APIs into AI-agent-friendly CLI tools. It automates the generation of Click-based Python CLI wrappers that provide structured command-line interfaces for any Spring Boot application with OpenAPI/Swagger documentation.

## When to Use This Skill

Use this skill when:
- User wants to generate a CLI wrapper for a Spring Boot REST API
- User needs AI agents to interact with Spring Boot services via command line
- User has OpenAPI/Swagger documentation available (via URL or local file)
- User needs structured JSON output for AI consumption
- User wants to automate API testing or CI/CD operations

## Skill Workflow

### Step 1: Gather Required Parameters

Prompt the user for the following information:

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

### Step 2: Fetch or Parse OpenAPI Specification

**If `--openapi-url` is provided:**
1. Make HTTP GET request to the URL using `requests` library
2. Validate response is valid JSON
3. Store specification for processing

**If `--openapi-file` is provided:**
1. Read the local file
2. Parse JSON or YAML format using `json` or `yaml` library
3. Validate structure contains required OpenAPI fields

### Step 3: Analyze the OpenAPI Specification

Extract the following from the specification:
- API title (for naming purposes)
- Available endpoints (paths and HTTP methods)
- Operation IDs for command naming
- Parameters (path, query, header) with types and requirements
- Request body schemas
- Response schemas
- Tags for grouping commands

### Step 4: Generate CLI Directory Structure

Create the following directory structure in the output directory:

```
cli-harness/
├── cli_anything_{app_name}/
│   ├── __init__.py
│   ├── cli.py              # Main CLI using Click
│   ├── http_client.py       # HTTP client with auth support
│   ├── repl.py             # Interactive REPL shell
│   ├── config.py           # Configuration management
│   └── tests/
│       ├── __init__.py
│       └── test_cli.py     # Unit and E2E tests
├── setup.py               # For pip installation
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

### Step 5: Generate HTTP Client Module

Use the `generate_http_client.py` script from `scripts/` directory to generate `http_client.py`:

```bash
python3 scripts/generate_http_client.py --auth-type <auth_type>
```

The generated client must:
- Use `requests` library for HTTP calls
- Support authentication (Bearer token, API Key, Basic)
- Handle errors with structured JSON responses
- Support configurable timeout
- Provide methods: `get()`, `post()`, `put()`, `patch()`, `delete()`

### Step 6: Generate CLI Module

Generate `cli.py` using Click framework:
- Use `@click.group()` for main CLI
- Create command groups based on API tags
- Generate individual commands for each operation
- Add `--json` flag for structured AI output
- Add `--config` option for config file path
- Add `--base-url` option for overriding API URL

### Step 7: Generate REPL Module

Create an interactive shell using Python's `cmd.Cmd`:
- Display banner with CLI name and version
- Support tab completion for commands
- Maintain connection context across commands
- Support `exit`, `help`, `clear` commands
- Delegate unknown commands to Click CLI

### Step 8: Generate Configuration Module

Create configuration management that:
- Provides default configuration with API base URL and timeout
- Supports loading from `~/.{cli-name}/config.yaml`
- Supports environment variables (`API_BASE_URL`, `API_TIMEOUT`, auth vars)
- Initializes config on first run

### Step 9: Generate Tests

Generate comprehensive test suite using pytest:
- Unit tests for HTTPClient methods
- Integration tests for CLI commands
- E2E tests that require running API
- Mark integration/E2E tests with appropriate markers

### Step 10: Generate setup.py and Documentation

Create Python package that:
- Uses Click for CLI framework
- Declares dependencies (click, requests, pyyaml)
- Defines console script entry point
- Includes development dependencies (pytest, black, pytest-cov)

Generate README.md with:
- Installation instructions
- Configuration guide
- Usage examples
- List of available commands
- Testing instructions

## Generated CLI Usage

After generation, the CLI can be used as follows:

```bash
# Install the generated CLI
cd cli-harness && pip install -e .

# Basic usage
cli-anything-myapp user get --id 123

# JSON output for AI consumption
cli-anything-myapp --json user list --page 1 --size 10

# Interactive REPL mode
cli-anything-myapp
myapp> user create --name "Alice" --email "alice@example.com"
myapp> user get --id 123
myapp> exit
```

## Spring Boot Application Requirements

The Spring Boot application should follow these practices:

### Required

- Provide OpenAPI 3.0 documentation (typically at `/v3/api-docs`)
- Use standard HTTP status codes
- Return JSON responses
- Provide consistent error response format

### Recommended

- RESTful API design principles
- Idempotent operations for GET/DELETE/PUT methods
- Standardized pagination (`page`/`size` or `offset`/limit`)
- Consistent naming conventions (snake_case or camelCase)

### Required Dependencies

Add to Spring Boot project:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

## Common Use Cases

1. **API Testing and Development**
   - Quickly test endpoints without writing curl commands
   - Save and reuse common API calls
   - Prototype API interactions

2. **CI/CD Pipelines**
   - Automate deployment and health checks
   - Run smoke tests after deployment
   - Integrate with build tools

3. **AI Agent Integration**
   - Enable Claude or other AI agents to control services
   - Provide structured JSON output for automated processing
   - Support agent-native interactions

4. **Operations and Monitoring**
   - Check service health and metrics
   - Query logs and status information
   - Automate operational tasks

## Troubleshooting

### Issue: Cannot fetch OpenAPI specification

**Solutions:**
- Verify Spring Boot application is running
- Check correct OpenAPI endpoint URL (default: `/v3/api-docs`)
- Ensure endpoint is accessible (no authentication required for spec)
- Check network connectivity

### Issue: Generated CLI fails with authentication errors

**Solutions:**
- Verify auth type matches API requirements
- Set appropriate environment variables or config file values
- Check that tokens/keys are valid and not expired
- For Bearer auth: Set `API_AUTH_TOKEN` environment variable
- For API Key: Set `API_KEY` environment variable
- For Basic auth: Set `API_USERNAME` and `API_PASSWORD`

### Issue: Tests fail because API is not available

**Solutions:**
- Run unit tests only: `pytest -m "not integration"`
- Start the API before running integration tests
- Set `TEST_API_URL` environment variable
- Use TestContainers for automated testing

### Issue: Generated commands don't match API

**Solutions:**
- Verify OpenAPI specification is complete
- Check operation IDs are properly defined
- Ensure tag grouping is correct
- Re-run skill generation after updating OpenAPI spec

## Bundled Resources

### Scripts (`scripts/`)

This skill includes the following executable scripts:

#### `generate_http_client.py`

Generates the HTTP client module based on authentication type.

**Usage:**
```bash
python3 scripts/generate_http_client.py --auth-type <type> --output <path>
```

**Parameters:**
- `--auth-type`: Authentication type (none, bearer, api-key, basic)
- `--output`: Output file path (default: `http_client.py`)

### References (`references/`)

Reference documentation for further reading:

- `springdoc_guide.md` - SpringDoc OpenAPI integration guide
- `click_documentation.md` - Click framework reference
- `cli_best_practices.md` - CLI design best practices

## Validation

Before distributing the generated CLI, ensure:

1. All OpenAPI endpoints have corresponding CLI commands
2. Authentication is properly configured
3. Tests pass with `pytest`
4. CLI can be installed with `pip install -e .`
5. Help documentation is complete and accurate

## References

External resources referenced in this skill:

- [SpringDoc OpenAPI Documentation](https://springdoc.org/)
- [Click Framework Documentation](https://click.palletsprojects.com/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
