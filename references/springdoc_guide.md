# SpringDoc OpenAPI Integration Guide

## Quick Start

Add SpringDoc dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

## Configuration

### Default Endpoints

| Endpoint | Description |
|-----------|-------------|
| `/v3/api-docs` | OpenAPI JSON specification |
| `/swagger-ui.html` | Swagger UI interface |
| `/swagger-ui-custom.html` | Customizable Swagger UI |

### Configuration Properties

```yaml
# application.yml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
  show-actuator: true
```

## API Documentation Best Practices

### 1. Add Operation IDs

```java
@GetMapping("/users/{{id}}")
@Operation(
    summary = "Get user by ID",
    operationId = "getUserById",
    tags = {"Users"}
)
public User getUser(@PathVariable Long id) {
    // ...
}
```

### 2. Document Parameters

```java
@GetMapping("/users")
@Operation(summary = "List users")
public Page<User> listUsers(
    @Parameter(description = "Page number (0-indexed)")
    @RequestParam(defaultValue = "0") int page,

    @Parameter(description = "Page size")
    @RequestParam(defaultValue = "10") int size
) {
    // ...
}
```

### 3. Document Request Body

```java
@PostMapping("/users")
@Operation(summary = "Create user")
public User createUser(
    @RequestBody
    @io.swagger.v3.oas.annotations.parameters.RequestBody(
        description = "User to create",
        required = true
    )
    @Valid CreateUserRequest request
) {
    // ...
}
```

## References

- [Official SpringDoc Documentation](https://springdoc.org/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
