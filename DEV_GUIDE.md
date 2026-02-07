# Quick Development Reference

## One-Time Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Daily Development

### Before Starting Work
```bash
# Pull latest changes
git pull origin main

# Update dependencies if needed
poetry install
```

### While Developing
```bash
# Run tests (quick feedback)
make test

# Run tests with coverage
make coverage

# Format code
make format

# Check for issues
make lint
```

### Before Committing
```bash
# Run everything
make check
```

### Committing Changes
```bash
git add .
git commit -m "Brief description of changes"
git push origin your-branch-name
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `make help` | Show all available commands |
| `make install` | Install/update dependencies |
| `make test` | Run tests |
| `make coverage` | Generate coverage report |
| `make format` | Auto-format code |
| `make lint` | Check code quality |
| `make check` | Run format + lint + test |
| `make clean` | Remove build artifacts |
| `make build` | Build package |

## Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=wbmaker

# Specific file
poetry run pytest tests/test_wb.py

# Specific test
poetry run pytest tests/test_wb.py::TestWBInitialization::test_init_without_credentials

# Verbose output
poetry run pytest -v

# Show print statements
poetry run pytest -s
```

## Code Quality

```bash
# Format code (automatic)
poetry run black wbmaker/ tests/

# Check formatting without changing
poetry run black --check wbmaker/ tests/

# Lint code
poetry run ruff check wbmaker/ tests/

# Auto-fix linting issues
poetry run ruff check wbmaker/ tests/ --fix

# Type check
poetry run mypy wbmaker/
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/feature-name

# Make changes, then...
git add .
git commit -m "Description"

# Push to your fork
git push origin feature/feature-name

# Open PR on GitHub
```

## Troubleshooting

### Poetry issues
```bash
# Clear cache and reinstall
rm -rf .venv
poetry install

# Update poetry itself
poetry self update
```

### Test failures
```bash
# Run with verbose output to see details
poetry run pytest -vv

# Run with print statements visible
poetry run pytest -s

# Run single failing test for faster debugging
poetry run pytest tests/test_wb.py::failing_test_name -v
```

### Import errors
```bash
# Reinstall package in dev mode
poetry install

# Check you're in the right venv
poetry env info
```

## Files You'll Edit Most

| File | Purpose |
|------|---------|
| `wbmaker/wb.py` | Main WB class |
| `wbmaker/item.py` | Item class |
| `tests/test_wb.py` | WB tests |
| `tests/test_item.py` | Item tests |
| `README.md` | User documentation |
| `pyproject.toml` | Dependencies & config |

## Need Help?

- Check `PROJECT_IMPROVEMENTS.md` for detailed explanations
- Check `CONTRIBUTING.md` for contribution guidelines
- Run `make help` for available commands
- Check [Poetry docs](https://python-poetry.org/docs/)
- Check [pytest docs](https://docs.pytest.org/)

## Pro Tips

1. **Use `make check` before committing** - catches issues early
2. **Write tests as you code** - easier than writing them later
3. **Run specific tests while debugging** - faster feedback
4. **Use `poetry run` for all commands** - ensures right environment
5. **Commit small, focused changes** - easier to review and debug
