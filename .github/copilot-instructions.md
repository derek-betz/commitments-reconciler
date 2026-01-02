# Copilot Instructions for Commitments Reconciler

## Project Overview

This repository contains integration tests and utilities for the commitments reconciliation prototype. The project generates and processes Excel and Word documents for commitments reconciliation workflows using deterministic factories rather than storing binary Office documents in version control.

## Language and Runtime

- **Primary Language**: Python
- **Minimum Version**: Python 3.12 or higher
- **Package Manager**: pip

## Key Dependencies

- `openpyxl` - Excel file reading/writing (.xlsx format)
- `python-docx` - Word document processing (.docx format)
- `pytest` - Testing framework

## Project Structure

- `commitments_reconciler/` - Main package containing:
  - `factories.py` - Factory functions for generating test documents
  - `io.py` - I/O utilities for document processing
- `tests/` - Test suite using pytest
  - `conftest.py` - Shared test configuration
  - `test_commitments_io.py` - Tests for I/O functionality
- `scripts/` - Utility scripts:
  - `run_tests.py` - Test runner with auto-installation of dependencies
  - `generate_examples.py` - Generates example documents
  - `bootstrap.ps1` - Windows setup script
- `examples/` - Generated example documents (git-ignored)

## Development Workflow

### Installation

Install the package in development mode with test dependencies (from repository root):

```bash
pip install -e .[test]
```

### Linting

This project uses Ruff for linting and code style enforcement. Configuration is in `pyproject.toml`.

Run linting from repository root:

```bash
python -m ruff check .
```

Ruff is configured with:
- Line length: 100 characters
- Target: Python 3.12
- Selected rules: pycodestyle, pyflakes, isort, pyupgrade, flake8-bugbear, flake8-comprehensions, flake8-simplify

### Testing

Run tests using the convenience script (auto-installs dependencies if needed, from repository root):

```bash
python scripts/run_tests.py -q
```

Or run pytest directly:

```bash
python -m pytest -q
```

All tests use runtime factories to generate test documents, so no additional setup is required.

### Generating Examples

Generate sample documents in the `examples/` directory (run from repository root):

```bash
python scripts/generate_examples.py
```

This creates `sample_commitments.xlsx` and `sample_env_doc.docx` in the `examples/` directory using the same factories as the tests.

## Code Style Guidelines

- Follow PEP 8 conventions as enforced by Ruff
- Use type hints where appropriate (Python 3.12+ syntax)
- Keep functions focused and testable
- Use descriptive variable names
- Prefer factory functions over storing binary test fixtures

## Testing Best Practices

- Use deterministic factories to generate test data
- Avoid checking in binary Office documents
- Test files should be self-contained and use conftest.py for shared fixtures
- Keep tests fast and focused on specific functionality

## Important Notes

- The `examples/` directory is git-ignored to prevent binary files from being committed
- All document generation should go through the factory functions in `commitments_reconciler/factories.py`
- Tests should never rely on pre-existing files; always generate data at runtime
- This project prioritizes plug-and-play usability and production-ready quality

## CI/CD

The project uses GitHub Actions for CI:
- Runs on Python 3.12
- Executes Ruff linting checks
- Runs the full pytest suite

All PRs should pass linting and tests before merging.
