"""\
Includes tests that check the setup for the tests.
If the library is compiled and if there is a crystal interpreter.
"""
import os
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import tempfile
class EnviromentTest(unittest.TestCase):
    "Test case that makes sure that the environment is up and working"
    def reportProgres(self):
        """Should be overloaded by the test result class"""

    def stop(self):
        """Should be overloaded by the test result class"""

    def runTest(self):
        """The actual test goes here."""
        if os.system(
            "crystal --help > %s" %
            os.path.join(
                tempfile.gettempdir(),
                tempfile.gettempprefix()
                )
            ):
            self.stop()
            raise RuntimeError("""Can't find the "crystal" command.""")
        self.reportProgres()
        if not os.path.exists("py2cr/builtins/module.cr"):
            self.stop()
            raise RuntimeError("""Can't find the "py2cr/builtins/module.cr" command.""")
        if not os.path.exists("py2cr/builtins/require.cr"):
            self.stop()
            raise RuntimeError("""Can't find the "py2cr/builtins/require.cr" command.""")
        self.reportProgres()

    def __str__(self):
        return 'Looking for "crystal", "py2cr/builtins/module.cr", "py2cr/builtins/require.cr" [3]:'


