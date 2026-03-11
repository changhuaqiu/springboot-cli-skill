# Spring Boot CLI Skill

A Claude Code skill that generates production-ready CLI wrappers for Spring Boot REST APIs using OpenAPI/Swagger documentation.

## Overview

This skill transforms Spring Boot REST APIs into AI-agent-friendly CLI tools. It automates the generation of Click-based Python CLI wrappers that provide structured command-line interfaces for any Spring Boot application with OpenAPI/Swagger documentation.

## Features

- ✅ **Automatic CLI Generation** - Generate complete CLI from OpenAPI spec
- ✅ **Multiple Authentication Support** - Bearer token, API Key, Basic auth
- ✅ **JSON Output Mode** - Structured output for AI consumption
- ✅ **Interactive REPL** - Multi-command sessions
- ✅ **Comprehensive Tests** - Unit, integration, and E2E tests
- ✅ **pip Installable** - Easy distribution and installation

## Installation

### Option 1: Clone Repository

```bash
git clone https://github.com/changhuaqiu/springboot-cli-skill.git ~/.claude/skills/springboot-cli
```

### Option 2: Download Skill File Only

```bash
curl -o ~/.claude/skills/springboot-cli.md \
  https://github.com/changhuaqiu/springboot-cli-skill/raw/main/SKILL.md
```

### Option 3: Add as Claude Code Marketplace

If using Claude Code with marketplace support:

```bash
/plugin marketplace add changhuaqiu/springboot-cli-skill
/plugin install springboot-cli
```

## Usage

### Prerequisites

1. **Spring Boot Application** with OpenAPI/Swagger documentation
2. **Python 3.8+** for generated CLI
3. **SpringDoc OpenAPI** dependency in your Spring Boot project

Add SpringDoc to your `pom.xml`:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

### Basic Usage

When using Claude Code, simply describe what you need:

```
Generate a CLI for my Spring Boot API at http://localhost:8080
```

Claude will automatically:
1. Fetch the OpenAPI specification from your running application
2. Analyze all available endpoints
3. Generate a complete CLI package
4. Create test files and documentation

### Advanced Usage Examples

#### From Running Application

```
Generate a CLI for my Spring Boot app at http://localhost:8080/v3/api-docs
```

#### From Local OpenAPI File

```
Create a CLI from my openapi.json file
```

#### With Authentication

```
Generate a CLI for https://api.example.com with Bearer token authentication
```

#### Filter by Tags

```
Generate a CLI with only user and product endpoints
```

## Generated CLI Structure

The skill generates a complete Python package:

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

## Using the Generated CLI

### Installation

```bash
cd cli-harness
pip install -e .
```

### Configuration

Create a config file at `~/.{cli-name}/config.yaml`:

```yaml
base_url: http://localhost:8080
timeout: 30
```

Or use environment variables:

```bash
export API_BASE_URL=http://localhost:8080
export API_TIMEOUT=30
```

### Basic Commands

```bash
# Show help
cli-anything-myapp --help

# List available commands for a group
cli-anything-myapp users --help

# Execute a command
cli-anything-myapp users get --id 123

# Create a resource
cli-anything-myapp users create \
  --name "Alice" \
  --email "alice@example.com"
```

### JSON Output (for AI Agents)

```bash
cli-anything-myapp --json users list --page 1 --size 10
```

Output:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Alice",
      "email": "alice@example.com"
    }
  ]
}
```

### Interactive REPL Mode

```bash
cli-anything-myapp
```

```
╔══════════════════════════════════════════╗
║       cli-anything-myapp v1.0.0          ║
║     CLI for Spring Boot API                   ║
╚══════════════════════════════════════════╝

myapp> users create --name "Alice" --email "alice@example.com"
✓ User created: id=123

myapp> users get --id 123
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com"
}

myapp> exit
Goodbye! 👋
```

## Authentication

### Bearer Token

```bash
export API_AUTH_TOKEN=your-jwt-token
cli-anything-myapp users list
```

### API Key

```bash
export API_KEY=your-api-key
cli-anything-myapp users list
```

### Basic Auth

```bash
export API_USERNAME=your-username
export API_PASSWORD=your-password
cli-anything-myapp users list
```

## Testing

### Run All Tests

```bash
cd cli-harness
pytest
```

### Run Unit Tests Only

```bash
pytest -m "not integration"
```

### Run with Coverage

```bash
pytest --cov=cli_anything_app --cov-report=html
```

## Spring Boot Requirements

Your Spring Boot application should follow these best practices:

### Required

- ✅ Provide OpenAPI 3.0 documentation at `/v3/api-docs`
- ✅ Use standard HTTP status codes
- ✅ Return JSON responses
- ✅ Provide consistent error response format

### Recommended

- 📌 RESTful API design principles
- 📌 Idempotent operations for GET/DELETE/PUT methods
- 📌 Standardized pagination (`page`/`size` or `offset`/limit`)
- 📌 Consistent naming conventions

### Example Controller with OpenAPI Documentation

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    @Operation(
        summary = "Get user by ID",
        operationId = "getUserById",
        tags = {"Users"}
    )
    public User getUser(
        @PathVariable Long id,
        @Parameter(description = "User ID")
        @PathVariable Long userId
    ) {
        return userService.findById(userId);
    }

    @PostMapping
    @Operation(
        summary = "Create user",
        operationId = "createUser",
        tags = {"Users"}
    )
    public User createUser(
        @RequestBody
        @Valid CreateUserRequest request
    ) {
        return userService.create(request);
    }
}
```

## Use Cases

### 1. API Testing and Development

Quickly test endpoints without writing curl commands:

```bash
cli-anything-myapp products list
cli-anything-myapp orders create --product-id 1 --quantity 2
```

### 2. CI/CD Pipelines

Automate deployment and health checks:

```bash
# Check API health
cli-anything-myapp health check

# Run smoke tests
pytest tests/test_cli.py
```

### 3. AI Agent Integration

Enable AI agents to control your services:

```bash
# AI can execute this command
cli-anything-myapp --json users list

# And process the JSON response
```

### 4. Operations and Monitoring

Automate operational tasks:

```bash
# Check service metrics
cli-anything-myapp metrics get --name jvm.memory.used

# Query logs
cli-anything-myapp logs tail --lines 100
```

## Troubleshooting

### Cannot fetch OpenAPI specification

**Solutions:**
- Verify Spring Boot application is running
- Check the OpenAPI endpoint URL (default: `/v3/api-docs`)
- Ensure endpoint is accessible without authentication
- Check network connectivity

### Generated CLI fails with authentication errors

**Solutions:**
- Verify auth type matches API requirements
- Set appropriate environment variables
- Check that tokens/keys are valid and not expired

### Tests fail because API is not available

**Solutions:**
- Run unit tests only: `pytest -m "not integration"`
- Start the API before running integration tests
- Set `TEST_API_URL` environment variable

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use and modify as needed.

## Links

- [Claude Code Skills Documentation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [SpringDoc OpenAPI Documentation](https://springdoc.org/)
- [Click Framework Documentation](https://click.palletsprojects.com/)
- [Python Requests Library](https://requests.readthedocs.io/)

## Star History

If you find this skill helpful, please give it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=changhuaqiu/springboot-cli-skill&type=Date)](https://star-history.com/#changhuaqiu/springboot-cli-skill&Date)
