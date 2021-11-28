"""
The special runners that look for progress in a test
and have nicer output than the original.
"""
from typing import Tuple, Any
import sys
import unittest

class Py2CrTestResult(unittest.TestResult):
    """Test result class, handling all the results reported by the tests"""

    def __init__(self, *a, **k) -> None:
        import testtools.writer
        super(Py2CrTestResult, self).__init__(*a, **k)
        self.__writer = testtools.writer.Writer(a[0])
        self.__faild = False
        self.__color = ""
        self.__state = ""

    def startTest(self, test : unittest.TestCase) -> None:
        super(Py2CrTestResult, self).startTest(test)
        test.reportProgres = self.addProgress
        test.stop = self.stop
        self.__writer.write(str(test))
        self.__state = "[Error]"
        self.__color = "Red"

    def stopTest(self, test : unittest.TestCase) -> None:
        super(Py2CrTestResult, self).stopTest(test)
        self.__writer.write(self.__state, align="right", color=self.__color)

    def addProgress(self) -> None:
        """Part of tests done"""
        self.__writer.write(".")

    def addSuccess(self, test : unittest.TestCase) -> None:
        super(Py2CrTestResult, self).addSuccess(test)
        self.__color = "Green"
        self.__state = "[OK]"

    def addSkip(self, test : unittest.TestCase, reason : str) -> None:
        super(Py2CrTestResult, self).addSuccess(test)
        self.__color = "Purple"
        self.__state = "[Skip] ({})".format(reason)

    def addUnexpectedSuccess(self, test : unittest.TestCase) -> None:
        super(Py2CrTestResult, self).addUnexpectedSuccess(test)
        self.__color = "Green"
        self.__state = "should fail but [OK]"

    def addExpectedFailure(self, test, err : Tuple[Any,Any,Any]) -> None:
        super(Py2CrTestResult, self).addExpectedFailure(test, err)
        self.__color = "Purple"
        self.__state = "known to [FAIL]"

    def addFailure(self, test: unittest.TestCase , err : Tuple[Any,Any,Any]) -> None:
        """
        Somewhat of a hack here to check the error-message to see if we
        failed because of a difference in the output or we failed to
        compile.
        """
        super(Py2CrTestResult, self).addFailure(test, err)
        message = err[1].args[0]
        if message.endswith(": diff"):
            self.__state = "[FAIL-Diff]"
        else:
            self.__state = "[FAIL-Compile]"
        self.__color = "Red"

    def stopTestRun(self) -> None:
        super(Py2CrTestResult, self).stopTestRun()
        self.__writer.write("\n")

class Py2CrTestRunner(unittest.TextTestRunner):
    """Test runner with Py2CrTestResult as result class"""
    resultclass = Py2CrTestResult
