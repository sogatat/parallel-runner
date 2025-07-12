# Testing Guide

This document provides comprehensive guidance for testing the parallel-runner project.

## Test Directory Structure

```
tests/
├── __init__.py
├── test_parallel_runner.py      # Main functionality tests
├── test_integration.py          # Integration tests (practical scenarios)
├── test_development_tools.py    # Development support & debug tools
└── run_tests.py                 # Test execution script
```

## Running Tests

### 1. Basic Test Execution

```bash
# Run all tests
python tests/run_tests.py all

# Or using standard pytest
pytest tests/

# Or using unittest
python -m unittest discover tests/
```

### 2. Purpose-Specific Tests

```bash
# Smoke test (basic functionality check)
python tests/run_tests.py smoke

# Performance benchmark
python tests/run_tests.py benchmark

# Tests with coverage
python tests/run_tests.py coverage

# Specific test class
python tests/run_tests.py specific --test test_parallel_runner.TestParallelRunner

# Specific test method
python tests/run_tests.py specific --test test_parallel_runner.TestParallelRunner.test_simple_function_execution
```

### 3. Development Support Tools

```bash
# Run development test suite
python tests/test_development_tools.py dev

# Tests with detailed debug information
python tests/run_tests.py all --verbose 3

# Stop on first failure
python tests/run_tests.py all --failfast
```

## Test Categories

### Unit Tests (`test_parallel_runner.py`)
- Core functionality testing
- Individual method validation
- Error handling verification
- Edge case coverage

### Integration Tests (`test_integration.py`)
- Real-world usage scenarios
- End-to-end workflow validation
- Cross-component interaction testing
- Performance under realistic conditions

### Development Tools (`test_development_tools.py`)
- Development workflow support
- Debug utilities
- Code quality checks
- Development environment validation

## Makefile Commands

For convenient development workflow:

```makefile
# Basic tests
make test

# Smoke tests
make smoke

# Benchmark tests
make benchmark

# Coverage reports
make coverage

# Code formatting
make format

# Linting
make lint

# Development installation
make dev-install

# Cleanup
make clean

# Full development check
make check

# Package building
make build
```

## Development Scripts

### Unix/Linux/macOS (`dev.sh`)

```bash
# Setup development environment
./dev.sh setup

# Run all tests
./dev.sh test

# Quick validation (smoke test + format + lint)
./dev.sh quick

# Format code
./dev.sh format

# Run linter
./dev.sh lint

# Coverage report
./dev.sh coverage

# Performance benchmark
./dev.sh benchmark

# Clean temporary files
./dev.sh clean

# Build package
./dev.sh build

# Full development check
./dev.sh check
```

### Windows (`dev.bat`)

```batch
# Setup development environment
dev.bat setup

# Run all tests
dev.bat test

# Quick validation
dev.bat quick

# Format code
dev.bat format

# Clean temporary files
dev.bat clean
```

## Test Configuration

### Prerequisites

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or manually install test dependencies
pip install pytest pytest-cov black flake8
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Unix/Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate.bat

# Install in development mode
pip install -e ".[dev]"
```

## Running Specific Test Types

### Smoke Tests
Quick validation of core functionality:
```bash
python tests/run_tests.py smoke
```

### Performance Benchmarks
Measure execution performance:
```bash
python tests/run_tests.py benchmark
```

### Coverage Analysis
Generate test coverage reports:
```bash
python tests/run_tests.py coverage
```

### Verbose Testing
Detailed output for debugging:
```bash
python tests/run_tests.py all --verbose 3
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: python tests/run_tests.py all
    - name: Upload coverage
      run: python tests/run_tests.py coverage
```

## Best Practices

### Writing Tests
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error conditions
- Keep tests independent and isolated
- Use appropriate assertions

### Test Organization
- Group related tests in the same file
- Use setUp/tearDown methods for common setup
- Utilize test fixtures for reusable test data
- Follow the Arrange-Act-Assert pattern

### Performance Testing
- Include performance benchmarks for critical paths
- Set reasonable performance thresholds
- Monitor performance regression over time
- Test with various data sizes and scenarios

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure the package is installed in development mode
   pip install -e .
   ```

2. **Test Discovery Issues**
   ```bash
   # Ensure __init__.py files exist in test directories
   touch tests/__init__.py
   ```

3. **Coverage Not Working**
   ```bash
   # Install coverage dependencies
   pip install pytest-cov
   ```

### Debug Mode
For detailed debugging information:
```bash
python tests/run_tests.py all --verbose 3 --failfast
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate documentation
3. Ensure tests pass in all supported Python versions
4. Update this README if adding new test categories
5. Run the full test suite before submitting

## Test Results Interpretation

- **PASSED**: Test executed successfully
- **FAILED**: Test failed with assertion error
- **ERROR**: Test failed with unexpected error
- **SKIPPED**: Test was skipped (intentionally)

For detailed output, use verbose mode or check the generated reports in the `coverage_html/` directory when running coverage tests.
