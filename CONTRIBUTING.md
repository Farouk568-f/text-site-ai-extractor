# 🤝 Contributing to Text Site AI Extractor

Thank you for your interest in contributing to Text Site AI Extractor! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a new branch for your feature
4. **Make** your changes
5. **Test** your changes
6. **Commit** and **push** to your fork
7. **Create** a Pull Request

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Flask, BeautifulSoup, and text processing

## 🛠️ Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/text-site-ai-extractor.git
cd text-site-ai-extractor
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development dependencies
```

### 4. Run Tests
```bash
python -m pytest tests/
```

## 📝 Code Style

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused

### Example
```python
def extract_text_from_url(url: str, min_length: int = 100) -> dict:
    """
    Extract text from a single URL with advanced filtering.
    
    Args:
        url (str): The URL to extract text from
        min_length (int): Minimum text length required
        
    Returns:
        dict: Extraction result with status and content
    """
    # Your code here
    pass
```

### Commit Messages
Use conventional commit format:
```
type(scope): description

feat(api): add new endpoint for bulk extraction
fix(filter): resolve duplicate content detection issue
docs(readme): update installation instructions
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_extractor.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests
- Create test files in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when possible

### Example Test
```python
def test_extract_text_success():
    """Test successful text extraction."""
    url = "https://example.com/article"
    result = extract_text_from_url(url, min_length=100)
    
    assert result["status"] == "success"
    assert result["text_length"] > 100
    assert "text" in result
```

## 🔧 Development Workflow

### 1. Feature Development
```bash
git checkout -b feature/new-feature-name
# Make your changes
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature-name
```

### 2. Bug Fixes
```bash
git checkout -b fix/bug-description
# Fix the bug
git add .
git commit -m "fix: resolve bug description"
git push origin fix/bug-description
```

### 3. Documentation Updates
```bash
git checkout -b docs/update-description
# Update documentation
git add .
git commit -m "docs: update description"
git push origin docs/update-description
```

## 📚 Documentation

### Code Documentation
- All functions and classes must have docstrings
- Use Google or NumPy docstring format
- Include examples for complex functions

### API Documentation
- Update README.md for new features
- Document all API endpoints
- Provide usage examples

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Step-by-step instructions
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, dependencies
6. **Screenshots**: If applicable

## 💡 Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature is needed
3. **Implementation Ideas**: Any thoughts on how to implement
4. **Priority**: High, Medium, or Low

## 🔒 Security

- Never commit sensitive information (API keys, passwords)
- Report security vulnerabilities privately
- Follow secure coding practices
- Validate all user inputs

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No sensitive information is included

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Wiki**: For detailed documentation

## 🎯 Contribution Areas

### High Priority
- [ ] Improve duplicate detection algorithm
- [ ] Add support for more languages
- [ ] Enhance content filtering
- [ ] Performance optimizations

### Medium Priority
- [ ] Add web interface
- [ ] Implement caching
- [ ] Add rate limiting
- [ ] Improve error handling

### Low Priority
- [ ] Add more test cases
- [ ] Code refactoring
- [ ] Documentation improvements
- [ ] CI/CD setup

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Text Site AI Extractor! 🚀
