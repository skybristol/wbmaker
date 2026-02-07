# Contributing to WBMaker

Thank you for your interest in contributing to WBMaker! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/wbmaker.git
   cd wbmaker
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

## Development Workflow

### Running Tests

Run the full test suite:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=wbmaker --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

### Code Quality Tools

We use several tools to maintain code quality:

#### Black (Code Formatting)
```bash
# Check formatting
poetry run black --check wbmaker/ tests/

# Auto-format code
poetry run black wbmaker/ tests/
```

#### Ruff (Linting)
```bash
# Check for issues
poetry run ruff check wbmaker/ tests/

# Auto-fix issues
poetry run ruff check wbmaker/ tests/ --fix
```

#### MyPy (Type Checking)
```bash
poetry run mypy wbmaker/
```

### Before Committing

Always run these commands before committing:

```bash
# Format code
poetry run black wbmaker/ tests/

# Fix linting issues
poetry run ruff check wbmaker/ tests/ --fix

# Run tests
poetry run pytest
```

## Git Workflow

### Branching Strategy

- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all CI checks pass

## Coding Standards

### Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use Black for formatting (100 character line length)
- Use type hints where appropriate
- Write docstrings for classes and functions

### Documentation

- Add docstrings to all public classes and methods
- Update README.md if adding user-facing features
- Add inline comments for complex logic

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Organize tests in classes by functionality

Example test structure:
```python
class TestFeatureName:
    """Test suite for feature X."""
    
    @pytest.fixture
    def mock_dependency(self):
        """Create mock dependency."""
        return MagicMock()
    
    def test_feature_behavior(self, mock_dependency):
        """Test that feature does X when Y."""
        # Arrange
        # Act
        # Assert
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/tracebacks

### Feature Requests

When requesting features, please include:
- Use case description
- Proposed solution or API
- Why it would be valuable
- Any alternative solutions considered

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. GitHub Actions automatically publishes to PyPI

## Questions?

- Open an issue for questions
- Check existing issues and discussions first
- Be respectful and constructive

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

Thank you for contributing to WBMaker! 🎉
