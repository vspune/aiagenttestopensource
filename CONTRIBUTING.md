# Contributing to Weather Agent API

Thank you for your interest in contributing! This document outlines how to contribute to the project.

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/demoopensource.git
   cd demoopensource
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test markers
pytest -m smoke           # Fast smoke tests
pytest -m integration     # Full integration tests
pytest -m security        # Security tests

# Generate HTML report
pytest --html=reports/report.html --self-contained-html

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Standards

- **Python Version:** 3.9+
- **Style Guide:** Follow PEP 8
- **Type Hints:** Encouraged for public functions
- **Docstrings:** Use Google-style docstrings

Example:
```python
def get_weather(city: str) -> dict:
    """
    Fetch current weather for a city.
    
    Args:
        city (str): City name (e.g., "London")
    
    Returns:
        dict: Weather data with temperature, humidity, etc.
    
    Raises:
        ValueError: If city not found
        requests.RequestException: If API call fails
    """
```

### Security Guidelines

- ❌ **DO NOT** hard-code API keys or credentials
- ✅ Use environment variables for secrets (see `.env.example`)
- ✅ Validate all user inputs
- ✅ Review [SECURITY.md](SECURITY.md) before submitting PR
- ❌ **DO NOT** print credentials or sensitive data in logs

### Git Workflow

1. **Make your changes**
   ```bash
   # Edit files...
   git add .
   git commit -m "Add feature: brief description"
   ```

2. **Keep commits clean**
   - One logical change per commit
   - Write descriptive commit messages
   - Reference issues when applicable: `Fixes #123`

3. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Submit Pull Request**
   - Fill out PR template
   - Reference related issues
   - Ensure tests pass

## Adding New Features

### Adding a New Tool

1. **Define the tool function** in `src/tools.py`:
```python
def my_new_tool(param1: str, param2: int) -> dict:
    """
    Brief description.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        dict: Result data
    """
    # Implementation
    return {"result": "data"}
```

2. **Add to TOOL_SCHEMAS** for the agent to discover it:
```python
TOOL_SCHEMAS = [
    {...},
    {
        "type": "function",
        "function": {
            "name": "my_new_tool",
            "description": "What this tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "..."},
                    "param2": {"type": "integer", "description": "..."}
                },
                "required": ["param1", "param2"]
            }
        }
    }
]
```

3. **Add to TOOL_REGISTRY**:
```python
TOOL_REGISTRY = {
    "my_new_tool": my_new_tool,
    ...
}
```

4. **Write tests** in `tests/test_answerrel.py` or new test file:
```python
def test_my_new_tool():
    result = my_new_tool("test", 42)
    assert result is not None
    assert "result" in result
```

### Adding New Tests

Create test files following pattern: `test_<feature>.py`

```python
import pytest
from src.agent import WeatherAgent
from src.tools import my_new_tool

@pytest.mark.unit
def test_my_new_tool_basic(agent):
    """Test basic functionality."""
    result = agent.chat("Use my new tool...")
    assert result["response"] is not None

@pytest.mark.integration
def test_my_new_tool_with_agent(agent):
    """Test integration with agent."""
    # Your test code
    pass
```

**Test markers:**
- `@pytest.mark.unit` — Self-contained tests
- `@pytest.mark.integration` — Full flow tests
- `@pytest.mark.security` — Security/jailbreak tests
- `@pytest.mark.slow` — Long-running tests
- `@pytest.mark.smoke` — Quick smoke tests

## Documentation

### Updating README

If your changes affect usage:
1. Update [README.md](README.md) with examples
2. Update docstrings in code
3. Run tests to verify examples work

### Documenting APIs

Document all public functions:
```python
def my_function(arg1: str) -> dict:
    """
    One-line summary.
    
    Longer description if needed. Can span multiple lines.
    
    Args:
        arg1: Description of argument
    
    Returns:
        dict: Description of return value
        
    Raises:
        ValueError: When validation fails
    
    Example:
        >>> result = my_function("test")
        >>> print(result["key"])
    """
```

## Reporting Issues

### Bug Reports

Include:
- Python version and OS
- OLLAMA model being used
- Minimal reproduction steps
- Expected vs actual behavior
- Error messages/stack traces

Template:
```
**Environment:**
- Python: 3.11
- OLLAMA model: qwen2.5:7b
- OS: Windows

**Bug Description:**
Brief description of the issue

**Steps to Reproduce:**
1. ...
2. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Error Logs:**
[Paste error output]
```

### Feature Requests

Include:
- Use case/motivation
- Proposed solution
- Alternatives considered

Template:
```
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution:**
How should it work?

**Alternatives:**
Other solutions considered

**Additional context:**
Any other info
```

## PR Review Process

1. **Automated Checks**
   - Tests must pass ✅
   - No security issues detected ✅

2. **Code Review**
   - Check code style & quality
   - Verify tests are present
   - Review security implications
   - Check documentation

3. **Approval & Merge**
   - PR approved by maintainer
   - Branch merged to main
   - Contributor credited in release notes

## Release Process

Maintainers will:
1. Update version in [src/api.py](src/api.py)
2. Create GitHub release with changelog
3. Tag commit with semantic version (v1.2.3)

## Getting Help

- 💬 Check existing [GitHub Issues](https://github.com/yourusername/demoopensource/issues)
- 📖 Read [README.md](README.md) and [SECURITY.md](SECURITY.md)
- 🐛 Open a new issue for bugs
- 💡 Open a discussion for questions

## Code of Conduct

Be respectful, inclusive, and constructive. We value:
- 🤝 Respectful communication
- 🎯 Focus on the problem, not the person
- 📚 Learning and growth mindset
- 🔒 Confidentiality of security issues

---

**Thank you for contributing! 🙏**
