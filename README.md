# py2cr.py

A code translator using AST from Python to Crystal. This is basically a
NodeVisitor with Crystal output. See ast documentation
(<https://docs.python.org/3/library/ast.html>) for more information.

## Installation

Execute the following:
```
pip install py2cr
```
or
```
git clone git://github.com/nanobowers/py2cr.git
```

## Versions

- Python 3.5 .. 3.9
- Crystal 1.1 ..

## Dependencies

### Python

    pip install six 
    pip install pyyaml 
    pip install numpy   # probably not really needed since

### Crystal

    * currently none *

## Methodology

In addition to walking and writing the AST tree and writing a Crystal
syntax output, this tool either: 
- Monkey-patches some common Crystal stdlib Structs/Classes in order to emulate the Python equivalent.
- Calls equivalent Crystal methods to the Python equivalent
- Calls wrapped Crystal methods that provide Python equivalent functionality

## Usage

Generally, `py2cr.py somefile.py > somefile.cr`

There is a Crystal shim/wrapper library in `lib/py2cr` that is also referenced in the generated script.  You may need to copy that as needed, though eventually it may be appropriate to convert it to a shard if that is more appropriate.

*TODO: need better explanation of this...*

## Tests
```
$ ./run_tests.py
```
Will run all tests that are supposed to work. If any test fails, its
a bug.  (Currently there are a lot of failing tests!!)
```
$ ./run_tests.py -a
```
Will run all tests including those that are known to fail (currently).
It should be understandable from the output.
```
$ ./run_tests.py -x or $ ./run_tests.py --no-error
```
Will run tests but ignore if an error is raised by the test. This is not
affecting the error generated by the test files in the tests directory.

For additional information on flags, run:
```
./run_tests.py -h
```

### Writing new tests
Adding tests for most new or existing functionality involves adding additional python files at `tests/<subdirectory/<testname>.py`.

The test-runner scripts will automatically run py2cr to produce a Crystal script, then run both the Python and Crystal scripts, then compare stdout/stderr and check return codes.

For special test-cases, it is possible to provide a configuration YAML file on a per test basis named `tests/<subdirectory>/<testname>.config.yaml` which overrides defaults for testing.  The following keys/values are supported:

```
min_python_version: [int, int] # minimum major/minor version
max_python_version: [int, int] # maximum major/minor version
expected_exit_status: int      # exit status for py/cr test script
argument_list: [str, ... str]  # list of strings as extra args for argv
```

## Typing

Some amount of typing support in Python is translated to Crystal.  There is still more work to do regarding initializing empty data-types on the Crystal side where the compiler cannot infer the type from a bare `[]` or `{}`

## To-do

This is incomplete and many of the tests brought forward from py2rb do not pass.  Some of them may never pass as-is due to significant language / compilation differences (even moreso than Python vs. Ruby)

To some extent, it will always be incomplete.  The goal is to cover common cases and reduce the additional work to minimum-viable-program.

## Contribute

Free to submit an issue.   This is very much a work in progress, contributions or constructive feedback is welcome.

If you'd like to hack on `py2cr`, start by forking the repo on GitHub:

https://github.com/nanobowers/py2cr

## Contributing

The best way to get your changes merged back into core is as follows:

1. Fork it (<https://github.com/nanobowers/py2cr/fork>)
2. Create a thoughtfully named topic branch to contain your change (`git checkout -b my-new-feature`)
3. Hack away
4. Add tests and make sure everything still passes by running `crystal spec`
5. If you are adding new functionality, document it in the README
8. If necessary, rebase your commits into logical chunks, without errors
9. Commit your changes (`git commit -am 'Add some feature'`)
10. Push to the branch (`git push origin my-new-feature`)
11. Create a new Pull Request

## License

MIT, see the LICENSE file for exact details.
