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

    py2cr_dot_cr = "lib/py2cr/src/py2cr.cr"
    crystal = "crystal"
    
    "Test case that makes sure that the environment is up and working"
    def reportProgres(self):
        """Should be overloaded by the test result class"""

    def stop(self):
        """Should be overloaded by the test result class"""

    def runTest(self):
        """The actual test goes here."""
        tmpfile = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix())
        if os.system(f"{self.crystal} --help > {tmpfile}"):
            self.stop()
            raise RuntimeError(f"Can't find the '{self.crystal}' command.")
        self.reportProgres()
        
        if not os.path.exists(self.py2cr_dot_cr):
            self.stop()
            raise RuntimeError(f"Can't find '{self.py2cr_dot_cr}'.")
        #if not os.path.exists("py2cr/builtins/require.cr"):
        #    self.stop()
        #    raise RuntimeError("""Can't find the "py2cr/builtins/require.cr" command.""")
        self.reportProgres()

    def __str__(self):
        return(f"Looking for '{self.crystal}', '{self.py2cr_dot_cr}' [3]:")


