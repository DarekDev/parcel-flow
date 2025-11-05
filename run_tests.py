#!/usr/bin/env python3
"""
Test runner for ParcelFlow.

Run all tests with:
    python run_tests.py

Run specific test modules:
    python run_tests.py test_parcel
    python run_tests.py test_workflow_engine

Run with verbose output:
    python run_tests.py -v
"""

import sys
import unittest

def run_tests(test_pattern=None, verbosity=2):
    """Run the test suite."""
    # Discover and run tests
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Run specific test module
        suite = loader.loadTestsFromName(f"tests.{test_pattern}")
    else:
        # Run all tests
        suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Parse command line arguments
    verbosity = 2
    test_pattern = None
    
    for arg in sys.argv[1:]:
        if arg == '-v' or arg == '--verbose':
            verbosity = 2
        elif arg == '-q' or arg == '--quiet':
            verbosity = 0
        elif not arg.startswith('-'):
            test_pattern = arg
    
    sys.exit(run_tests(test_pattern, verbosity))
