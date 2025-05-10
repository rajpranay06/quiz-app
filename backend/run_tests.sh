#!/bin/bash
echo "Running simple test to verify pytest..."
python -m pytest base/test_simple.py -v

echo
echo "Running all tests..."
export DJANGO_SETTINGS_MODULE=backend.settings
python -m pytest base/tests.py -v

echo
echo "If tests are still not running, try:"
echo "pip install -e ."
echo "python -m pytest" 