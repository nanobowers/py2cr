#!/usr/bin/env python

""" Runs test for py2cr """
import sys
import argparse
import testtools.runner
import testtools.util
import testtools.tests

try:
    import yaml
except ModuleNotFoundError as ex:
    raise ModuleNotFoundError("Cannot find pyyaml, install and re-try") from ex

try:
    import numpy
except ModuleNotFoundError as ex:
    raise ModuleNotFoundError("Cannot find numpy, install and re-try") from ex

try:
    import six
except ModuleNotFoundError as ex:
    raise ModuleNotFoundError("Cannot find six, install and re-try") from ex

def main():
    """ Main test runner CLI """
    option_parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [filenames]",
        description="py2cr unittests script."
        )
    option_parser.add_argument(
        "-a",
        "--run-all",
        action="store_true",
        dest="run_all",
        default=False,
        help="run all tests (including the known-to-fail)"
        )
    option_parser.add_argument(
        "-x",
        "--no-error",
        action="store_true",
        dest="no_error",
        default=False,
        help="ignores error( don't display them after tests)"
        )
    option_parser.add_argument(
        "--fail-only",
        action="store_true",
        dest="fail_only",
        default=False,
        help="run failing known-to-fail tests only"
        )
    options, args = option_parser.parse_known_args()
    runner = testtools.runner.Py2RbTestRunner(verbosity=2)
    results = None
    if options.run_all:
        results = runner.run(testtools.tests.ALL)
    elif options.fail_only:
        results = runner.run(testtools.tests.KNOWN_TO_FAIL)
    elif args:
        results = runner.run(testtools.tests.get_tests(args))
    else:
        results = runner.run(testtools.tests.NOT_KNOWN_TO_FAIL)
    if not options.no_error and results.errors:
        print()
        print("errors:")
        print("  (use -x to skip this part)")
        for test, error in results.errors:
            print()
            print("*", str(test), "*")
            print(error)
    if results.errors or results.failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
