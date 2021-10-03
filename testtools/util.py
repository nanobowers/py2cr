"""
Module that defines Tool functions and test runners/result for use with
the unittest library.
"""
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import posixpath
import re
import yaml

def get_posix_path(path):
    """translates path to a posix path"""
    heads = []
    tail = path
    while tail != '':
        tail, head = os.path.split(tail)
        heads.append(head)
    return posixpath.join(*heads[::-1])

def run_crystal_with_stdlib(file_path, file_name=None):
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
        def reportProgres(self):
            """Should be overloaded by the test result class."""
    
        def runTest(self):
            """The actual test goes here."""
            cmd = (
                  'crystal "py2cr/builtins/module.cr" '
                  ' "%(cr_path)s" > "%(cr_out_path)s" 2> "%(cr_error)s"'
                  )% self.templ
            self.assertEqual(0, os.system(cmd))
            self.reportProgres()

        def __str__(self):
            return "%(cr_unix_path)s [1]: " % self.templ

    return TestCrystalStdLib

def compile_python_file_test(file_path, file_name=None):
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
        def reportProgres(self):
            """Should be overloaded by the test result class"""

        def runTest(self):
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
        def __str__(self):
            return "%(py_unix_path)s [1]: " % self.templ
    return CompileFile




def compile_and_run_file_test(file_path, file_name=None):
    """Creates a test that compiles and runs the python file as crystal"""
    file_name = file_name if file_name else file_path

    class CompileAndRunFile(unittest.TestCase):
        """Tests that a file can be compiled and run as crystal"""
        name_path, ext = os.path.splitext(file_path)
        templ = {
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
        "min_python_version": None,
        "max_python_version": None,
        "expected_exit_status": 0,
        "check_stdout": True,
        "check_stderr": True,
        "argument_list": [],
        }
        def reportProgres(self):
            """Should be overloaded by the test result class"""

        def enhance_configuration(self):
            """Read configuration overrides from a yaml file on a per-test basis"""
            config_file = self.templ["config_path"]
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.templ.update(yaml.safe_load(f))

        def skip_invalid_version(self):
            """Perform version comparison and skip the test if we are not
            within the range of valid versions"""
            templ=self.templ
            pymajor = sys.version_info.major
            pyminor = sys.version_info.minor
            if templ["min_python_version"]:
                minver = templ["min_python_version"]
                reason = "pyver {}.{} < {}.{}".format(pymajor, pyminor, minver[0], minver[1])
                cmpr = (pymajor < minver[0]) or (pymajor == minver[0] and pyminor < minver[1])
                if cmpr:
                    raise unittest.SkipTest(reason)

            if templ["max_python_version"]:
                minver = templ["max_python_version"]
                reason = "pyver {}.{} > {}.{}".format(pymajor, pyminor, minver[0], minver[1])
                cmpr = (pymajor > minver[0]) or (pymajor == minver[0] and pyminor > minver[1])
                if cmpr:
                    raise unittest.SkipTest(reason)

            return None

        def argument_string(self):
            """Produce a string for the argument list if it exists"""
            if self.templ["argument_list"] is None:
                return ""
            return " ".join(self.templ["argument_list"])
                

        
        def runTest(self):
            """The actual test goes here."""
            self.enhance_configuration()
            self.skip_invalid_version()
            self.templ["argument_str"] = self.argument_string()
            python_command = 'python "{py_path}" {argument_str} > "{py_out_path}" 2> "{py_error}"'.format(**self.templ)
            compile_command = 'python py2cr.py -p "{py_dir_path}" -r "{py_path}" -m -f -w -s 2> "{compiler_error}"'.format(**self.templ)
            crystal_command = 'crystal "{cr_path}" {argument_str} > "{cr_out_path}" 2> "{cr_error}"'.format(**self.templ)
            commands = [python_command, compile_command, crystal_command]
            with open(self.templ['cmd_out'], mode = 'w') as fh:
                for cmd in commands:
                    fh.write(cmd + '\n')
                    #print(cmd) # debug
                    # The compile command should always exit cleanly.
                    # The other two jobs may optionally have an overridden and equivalent expected_exit_status
                    if cmd == compile_command:
                        exitstatus = 0
                    else:
                        exitstatus = self.templ["expected_exit_status"]
                    result_exit = os.system(cmd) >> 8
                    self.assertEqual(exitstatus, result_exit)
                    self.reportProgres()
            # Partial Match
            if os.path.exists(self.templ["cr_out_expected_in_path"]):
                # Fixed statement partial match
                f = open(self.templ["cr_out_expected_in_path"])
                g = open(self.templ["cr_out_path"])
                self.assertIn(
                    f.read(),
                    g.read()
                    )
                f.close()
                g.close()
            else: # Full text match
                # Fixed sentence matching
                if os.path.exists(self.templ["cr_out_expected_path"]):
                    expected_file_path = self.templ["cr_out_expected_path"]
                else: # Dynamic sentence matching
                    expected_file_path = self.templ["py_out_path"]
                f = open(expected_file_path, 'r')
                g = open(self.templ["cr_out_path"])
                self.assertEqual(
                    f.readlines(),
                    g.readlines()
                    )
                f.close()
                g.close()
            self.reportProgres()

        def __str__(self):
            return "%(py_unix_path)s [4]: " % self.templ

    return CompileAndRunFile

def compile_and_run_file_failing_test(*a, **k):
    """Turn a test to a failing test"""
    _class = compile_and_run_file_test(*a, **k)

    class FailingTest(_class):
        """Failing test"""
        @unittest.expectedFailure
        def runTest(self):
            return super(FailingTest, self).runTest()

    return FailingTest

