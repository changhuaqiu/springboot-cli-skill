# CLI Design Best Practices

## Core Principles

### 1. Structured Output for AI

Always provide structured JSON output via `--json` flag:

```python
@click.option('--json', 'json_output', is_flag=True)
def command(..., json_output):
    if json_output:
        output = json.dumps(data, indent=2)
    else:
        output = human_readable_format(data)
    click.echo(output)
```

### 2. Self-Describing

Every command should have `--help`:

```python
@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def command(verbose):
    """One-sentence description.

    Additional description paragraph.
    """
    pass
```

### 3. Consistent Error Handling

```python
def handle_error(error):
    click.echo(f"Error: {error}", err=True)
    raise click.exceptions.Exit(1)
```

### 4. Type Safety

Use Click's type conversion:

```python
@click.option('--count', type=int, default=1)
@click.option('--verbose/--quiet', default=False)
```

## Command Organization

### Group Related Commands

```python
@click.group()
def main():
    pass

@main.group()
def users():
    """User management commands."""
    pass

@users.command()
def list():
    """List all users."""
    pass
```

### Naming Conventions

- Use verbs: `get`, `list`, `create`, `update`, `delete`
- Use kebab-case: `get-user`, `list-users`
- Be specific: `get-user-by-id` vs `get`

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [The Twelve-Factor App: CLI](https://12factor.net/)
