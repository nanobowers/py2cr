#!/usr/bin/env python

import optparse
import testtools.runner
import testtools.util
import testtools.tests

try:
    import yaml
except:
    raise "Cannot find pyyaml, install and re-try"

try:
    import numpy
except:
    raise "Cannot find numpy, install and re-try"

try:
    import six
except:
    raise "Cannot find six, install and re-try"


def main():
    option_parser = optparse.OptionParser(
        usage="%prog [options] [filenames]",
        description="py2cr unittests script."
        )
    option_parser.add_option(
        "-a",
        "--run-all",
        action="store_true",
        dest="run_all",
        default=False,
        help="run all tests (including the known-to-fail)"
        )
    option_parser.add_option(
        "-x",
        "--no-error",
        action="store_true",
        dest="no_error",
        default=False,
        help="ignores error( don't display them after tests)"
        )
    option_parser.add_option(
        "--fail-only",
        action="store_true",
        dest="fail_only",
        default=False,
        help="run failing known-to-fail tests only"
        )
    options, args = option_parser.parse_args()
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
        print
        print("errors:")
        print("  (use -x to skip this part)")
        for test, error in results.errors:
            print
            print("*", str(test), "*")
            print(error)
    if results.errors or results.failures:
        exit(1)

if __name__ == "__main__":
  main()
