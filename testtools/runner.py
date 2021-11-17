"""
The special runners that look for progress in a test
and have nicer output than the original.
"""
import sys
import unittest

class Py2RbTestResult(unittest.TestResult):
    """Test result class, handling all the results reported by the tests"""

    def __init__(self, *a, **k):
        import testtools.writer
        super(Py2RbTestResult, self).__init__(*a, **k)
        self.__writer = testtools.writer.Writer(a[0])
        self.__faild = False
        self.__color = ""
        self.__state = ""

    def startTest(self, test):
        super(Py2RbTestResult, self).startTest(test)
        test.reportProgres = self.addProgress
        test.stop = self.stop
        self.__writer.write(str(test))
        self.__state = "[Error]"
        self.__color = "Red"

    def stopTest(self, test):
        super(Py2RbTestResult, self).stopTest(test)
        self.__writer.write(self.__state, align="right", color=self.__color)

    def addProgress(self):
        """Part of tests done"""
        self.__writer.write(".")

    def addSuccess(self, test):
        super(Py2RbTestResult, self).addSuccess(test)
        self.__color = "Green"
        self.__state = "[OK]"

    def addSkip(self, test, reason):
        super(Py2RbTestResult, self).addSuccess(test)
        self.__color = "Purple"
        self.__state = "[Skip] ({})".format(reason)

    def addUnexpectedSuccess(self, test):
        super(Py2RbTestResult, self).addUnexpectedSuccess(test)
        self.__color = "Green"
        self.__state = "should fail but [OK]"

    def addExpectedFailure(self, test, err):
        super(Py2RbTestResult, self).addExpectedFailure(test, err)
        self.__color = "Purple"
        self.__state = "known to [FAIL]"

    def addFailure(self, test, err):
        """
        Somewhat of a hack here to check the error-message to see if we
        failed because of a difference in the output or we failed to
        compile.
        """
        super(Py2RbTestResult, self).addFailure(test, err)
        message = err[1].args[0]
        if message.endswith(": diff"):
            self.__state = "[FAIL-Diff]"
        else:
            self.__state = "[FAIL-Compile]"
        self.__color = "Red"

    def stopTestRun(self):
        super(Py2RbTestResult, self).stopTestRun()
        self.__writer.write("\n")

class Py2RbTestRunner(unittest.TextTestRunner):
    """Test runner with Py2RbTestResult as result class"""
    resultclass = Py2RbTestResult
