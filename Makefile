.PHONY: help install run test clean lint format docs

# Default target
help:
	@echo "🚀 Text Site AI Extractor - Available Commands:"
	@echo ""
	@echo "📦 Setup:"
	@echo "  install     Install dependencies"
	@echo "  setup       Setup development environment"
	@echo ""
	@echo "🚀 Run:"
	@echo "  run         Run the API server"
	@echo "  dev         Run in development mode"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo ""
	@echo "🔧 Development:"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black"
	@echo "  clean       Clean temporary files"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs        Generate documentation"
	@echo ""
	@echo "📦 Package:"
	@echo "  build       Build package"
	@echo "  publish     Publish to PyPI"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Setup development environment
setup: install
	@echo "🔧 Setting up development environment..."
	pip install -e .
	pip install pytest pytest-cov black flake8 mypy

# Run the API server
run:
	@echo "🚀 Starting API server..."
	python article_api.py

# Run in development mode
dev:
	@echo "🔧 Starting API server in development mode..."
	FLASK_ENV=development python article_api.py

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

# Run linting checks
lint:
	@echo "🔍 Running linting checks..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code with black
format:
	@echo "🎨 Formatting code with black..."
	black . --line-length=127

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.log" -delete

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation is available in README.md and README_IMPROVED.md"

# Build package
build:
	@echo "📦 Building package..."
	python setup.py sdist bdist_wheel

# Publish to PyPI (requires authentication)
publish:
	@echo "🚀 Publishing to PyPI..."
	twine upload dist/*

# Install development dependencies
install-dev: install
	@echo "🔧 Installing development dependencies..."
	pip install pytest pytest-cov black flake8 mypy twine

# Check code quality
quality: lint format
	@echo "✅ Code quality checks completed"

# Full development setup
dev-setup: install-dev setup
	@echo "🎉 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Run 'make run' to start the API"
	@echo "2. Run 'make test' to run tests"
	@echo "3. Run 'make quality' to check code quality"

# Quick start
quick-start: install run
	@echo "🚀 Quick start completed!"

# Show project info
info:
	@echo "📋 Project Information:"
	@echo "Name: Text Site AI Extractor"
	@echo "Version: 1.0.0"
	@echo "Description: Advanced Arabic text extraction API"
	@echo "Author: Farouk568-f"
	@echo "License: MIT"
	@echo "Python: 3.8+"
	@echo ""
	@echo "🌐 Repository: https://github.com/Farouk568-f/text-site-ai-extractor"
	@echo "📚 Documentation: README.md"
	@echo "🤝 Contributing: CONTRIBUTING.md"
