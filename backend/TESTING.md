# Quiz App Testing Guide

This document provides instructions on how to run the tests for the Quiz App.

## Setup

The project uses pytest and pytest-django for testing. These packages are already included in the requirements.txt file.

## Running the Tests

To run all the tests, navigate to the backend directory and run:

```bash
cd backend
python -m pytest
```

If you're encountering issues with test discovery, try:

```bash
cd backend
python -m pytest base/tests.py -v
```

Or run a specific test file directly:

```bash
cd backend
python -m pytest base/test_simple.py -v
```

## Debugging Test Discovery Issues

If pytest is not finding your tests, try these steps:

1. Verify you're in the correct directory (you should be in the `backend` directory)
2. Make sure Django settings are properly configured:

```bash
cd backend
export DJANGO_SETTINGS_MODULE=backend.settings  # For Linux/Mac
# OR
set DJANGO_SETTINGS_MODULE=backend.settings     # For Windows
python -m pytest base/tests.py -v
```

3. Install the project in development mode:

```bash
cd backend
pip install -e .
python -m pytest
```

## Test Coverage

To generate a test coverage report, first install the pytest-cov package:

```bash
pip install pytest-cov
```

Then run:

```bash
cd backend
python -m pytest --cov=base
```

For a more detailed coverage report:

```bash
cd backend
python -m pytest --cov=base --cov-report=html
```

This will generate an HTML report in the `htmlcov` directory.

## Test Structure

The tests are organized as follows:

1. **Simple Tests**: Basic tests to verify pytest is working correctly
2. **API Tests**: Tests for all the REST API endpoints

Each test uses fixtures to set up test data, and pytest's `@pytest.mark.django_db` decorator to handle the database connections.

## Continuous Integration

The tests can be integrated into a CI/CD pipeline to run automatically on each commit or pull request. Add the following command to your CI configuration:

```bash
cd backend
python -m pytest
```

## Test Data

The tests use fixtures to create:
- Test users
- Test quizzes
- Test questions with options
- Test quiz attempts

This ensures consistent test data across all test functions. 