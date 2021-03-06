"""
Module that defines Tool functions and test runners/result for use with
the unittest library.
"""
from typing import Optional, Any, Type
import sys
import unittest
import os
import posixpath
import yaml

def get_posix_path(path : str) -> str:
    """translates path to a posix path"""
    heads = []
    tail = path
    while tail != '':
        tail, head = os.path.split(tail)
        heads.append(head)
    return posixpath.join(*heads[::-1])

def run_crystal_with_stdlib(file_path : str, file_name : Optional[str] = None) -> Type[Any]:
    """Creates a test that runs a crystal file with the stdlib."""
    file_name = file_name if file_name else file_path

    class TestCrystalStdLib(unittest.TestCase):
        """Tests crystal code with the stdlib"""
        templ = {
            "cr_path": file_path,
            "cr_unix_path": get_posix_path(file_path),
            "cr_out_path": file_path + ".out",
            "cr_error": file_path + ".err",
            "name": file_name,
        }
        def reportProgres(self) -> None:
            """Should be overloaded by the test result class."""

        def runTest(self) -> None:
            """The actual test goes here."""
            cmd = (
                  'crystal "py2cr/builtins/module.cr" '
                  ' "%(cr_path)s" > "%(cr_out_path)s" 2> "%(cr_error)s"'
                  )% self.templ
            self.assertEqual(0, os.system(cmd))
            self.reportProgres()

        def __str__(self) -> str:
            return "%(cr_unix_path)s [1]: " % self.templ

    return TestCrystalStdLib

def compile_python_file_test(file_path : str, file_name : Optional[str] = None) -> Type[Any]:
    """Creates a test that tests if a file can be compiled by python"""
    file_name = file_name if file_name else file_path

    class CompileFile(unittest.TestCase):
        """Test if a file can be compiled by python."""

        templ = {
            "py_path": file_path,
            "py_unix_path": get_posix_path(file_path),
            "py_out_path": file_path + ".out",
            "py_error": file_path + ".err",
            "name": file_name,
        }
        def reportProgres(self) -> None:
            """Should be overloaded by the test result class"""

        def runTest(self) -> None:
            """The actual test goes here."""
            commands = (
                (
                'python "%(py_path)s" > '
                '"%(py_out_path)s" 2> "%(py_error)s"'
                ) % self.templ,
              )
            for cmd in commands:
                self.assertEqual(0, os.system(cmd))
                self.reportProgres()
        def __str__(self) -> str:
            return "%(py_unix_path)s [1]: " % self.templ
    return CompileFile




def compile_and_run_file_test(file_path : str, file_name : Optional[str] = None) -> Type[Any]:
    """Creates a test that compiles and runs the python file as crystal"""
    file_name = file_name if file_name else file_path

    class CompileAndRunFile(unittest.TestCase):
        """Tests that a file can be compiled and run as crystal"""
        name_path, ext = os.path.splitext(file_path)
        templ  = {
            "py_path": file_path,
            "py_dir_path": os.path.dirname(file_path),
            "py_unix_path": get_posix_path(file_path),
            "py_out_path": file_path + ".out",
            "cr_path": name_path + ".cr",
            "cr_out_path": name_path + ".cr.out",
            "cr_out_expected_path": name_path + ".cr.expected_out",
            "cr_out_expected_in_path": name_path + ".cr.expected_in_out",
            "py_error": file_path + ".err",
            "cr_error": name_path + ".cr.err",
            "compiler_error": file_path + ".comp.err",
            "name": file_name,
            "cmd_out": name_path + ".cmd.txt",
            "config_path": name_path + ".config.yaml",
            # expect that these next few options may be updated in the config file
            # on a per test basis
            "min_python_version": (0, 0),
            "max_python_version": (999, 999),
            "expected_exit_status": 0,
            "check_stdout": True,
            "check_stderr": True,
            "argument_list": [],
        }
        def reportProgres(self) -> None:
            """Should be overloaded by the test result class"""

        def enhance_configuration(self) -> None:
            """Read configuration overrides from a yaml file on a per-test basis"""
            config_file = self.templ["config_path"]
            if os.path.exists(config_file):
                with open(config_file, 'r') as cfg_fh:
                    self.templ.update(yaml.safe_load(cfg_fh))

        def skip_invalid_version(self) -> None:
            """Perform version comparison and skip the test if we are not
            within the range of valid versions"""
            templ = self.templ
            pymajor = sys.version_info.major
            pyminor = sys.version_info.minor
            if templ["min_python_version"]:
                minver = templ["min_python_version"]
                reason = "pyver {}.{} < {}.{}".format(pymajor, pyminor, minver[0], minver[1])
                cmpr = (pymajor < minver[0]) or (pymajor == minver[0] and pyminor < minver[1])
                if cmpr:
                    raise unittest.SkipTest(reason)

            if templ["max_python_version"]:
                maxver = templ["max_python_version"]
                reason = "pyver {}.{} > {}.{}".format(pymajor, pyminor, maxver[0], maxver[1])
                cmpr = (pymajor > maxver[0]) or (pymajor == maxver[0] and pyminor > maxver[1])
                if cmpr:
                    raise unittest.SkipTest(reason)

        def argument_string(self) -> str:
            """Produce a string for the argument list if it exists"""
            if self.templ["argument_list"] is None:
                return ""
            return " ".join(self.templ["argument_list"])

        def runTest(self) -> None:
            """The actual test goes here."""
            self.enhance_configuration()
            self.skip_invalid_version()
            self.templ["argument_str"] = self.argument_string()
            python_command = 'python "{py_path}" {argument_str} > "{py_out_path}" 2> "{py_error}"'.format(**self.templ)
            compile_command = 'python py2cr.py -p "{py_dir_path}" -r "{py_path}" -m -f -w -s 2> "{compiler_error}"'.format(**self.templ)
            crystal_command = 'crystal "{cr_path}" {argument_str} > "{cr_out_path}" 2> "{cr_error}"'.format(**self.templ)
            command_stages = [
                (python_command, "python"),
                (compile_command, "py2cr"),
                (crystal_command, "crystal") ]

            with open(self.templ['cmd_out'], mode = 'w') as cmdfh:
                for cmd, stage in command_stages:
                    cmdfh.write(cmd + '\n')
                    #print(cmd) # debug
                    # The compile command should always exit cleanly.
                    # The other two jobs may optionally have an overridden and equivalent expected_exit_status
                    if cmd == compile_command:
                        exitstatus = 0
                    else:
                        exitstatus = self.templ["expected_exit_status"]
                    result_exit = os.system(cmd) >> 8
                    self.assertEqual(exitstatus, result_exit, stage)
                    self.reportProgres()
            # Partial Match
            if os.path.exists(self.templ["cr_out_expected_in_path"]):
                # Fixed statement partial match
                with open(self.templ["cr_out_expected_in_path"], 'r') as exfh:
                    with open(self.templ["cr_out_path"]) as outfh:
                        self.assertIn(exfh.read(), outfh.read(), "diff")
            else: # Full text match
                # Fixed sentence matching
                if os.path.exists(self.templ["cr_out_expected_path"]):
                    expected_file_path = self.templ["cr_out_expected_path"]
                else: # Dynamic sentence matching
                    expected_file_path = self.templ["py_out_path"]
                with open(expected_file_path, 'r') as exfh:
                    with open(self.templ["cr_out_path"]) as outfh:
                        self.assertEqual(exfh.readlines(), outfh.readlines(), "diff")

            self.reportProgres()

        def __str__(self) -> str:
            return "%(py_unix_path)s [4]: " % self.templ

    return CompileAndRunFile

def compile_and_run_file_failing_test(*a, **k):
    """Turn a test to a failing test"""
    _class = compile_and_run_file_test(*a, **k)

    class FailingTest(_class):
        """Failing test"""
        @unittest.expectedFailure
        def runTest(self) -> bool:
            return super().runTest()

    return FailingTest

