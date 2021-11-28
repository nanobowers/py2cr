"""module which finds tests from the test directory and converts them to
the unittest framework classes."""
from typing import List, Tuple
import os
import glob
import unittest
import itertools
from testtools import env_tests
from testtools import known_to_fail
from testtools import util

def create_cases() -> Tuple[unittest.TestSuite, unittest.TestSuite] :
    """Helper function to find all tests in the test folders
    and wrapping them into the correct test class"""

    test_cases = unittest.TestSuite()
    test_cases.addTest(
        unittest.TestLoader().loadTestsFromTestCase(
            env_tests.EnviromentTest
            )
        )

    failing_test_cases = unittest.TestSuite()

    test_paths = glob.glob("tests/test_*.py")
    test_paths.sort()
    for test_path in test_paths:
        test_cases.addTest(
            unittest.TestLoader().loadTestsFromTestCase(
                util.compile_python_file_test(test_path, os.path.basename(test_path))
                )
            )


    # Use all of the tests/*/*.py files to add
    # all of the transpiler feature tests.

    test_paths = glob.glob("tests/*/*.py")
    test_paths.sort()
    for test_path in test_paths:
        test_path_fix = test_path.replace("\\","/")
        if test_path_fix not in known_to_fail.KNOWN_TO_FAIL:
            test_cases.addTest(
                unittest.TestLoader().loadTestsFromTestCase(
                    util.compile_and_run_file_test(
                        test_path,
                        os.path.basename(test_path)
                        )
                    )
                )
        else:
            failing_test_cases.addTest(
                unittest.TestLoader().loadTestsFromTestCase(
                    util.compile_and_run_file_failing_test(
                        test_path,
                        os.path.basename(test_path)
                        )
                    )
                )
    return test_cases, failing_test_cases

NOT_KNOWN_TO_FAIL, KNOWN_TO_FAIL = create_cases()
ALL = unittest.TestSuite((NOT_KNOWN_TO_FAIL, KNOWN_TO_FAIL))

print(f"INFO: Found {ALL.countTestCases()} testcases.")

def get_tests(names : List[str]) -> unittest.TestSuite:
    """filters out all tests that don't exist in names and
    adds them to a new test suite"""
    def flatten(itr):
        """tries to flatten out a suite to the individual tests"""
        try:
            return itertools.chain.from_iterable(flatten(item) for item in iter)
        except TypeError:
            return itertools.chain(*itr)

    return_suite = unittest.TestSuite()
    return_suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(
            env_tests.EnviromentTest
            )
        )
    for suite in flatten(iter(ALL)):
        test_name = str(suite._tests[0])
        if any(True for name in names if name in test_name):
            return_suite.addTest(suite)
    return return_suite

def load_tests(_loader, standard_tests : unittest.TestSuite, _search_pattern) -> unittest.TestSuite:
    """function called by the unittest framework to find tests in a module"""
    suite = standard_tests
    suite.addTests(ALL)
    return suite
