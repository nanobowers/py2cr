"""
A formatter module that keeps track of indentation
"""

from .errors import CrystalError

class Formatter:
    """
    A very simple code formatter that handles efficient
    concatenation and indentation of lines.
    """

    def __init__(self, indent_string="  "):
        self.__buffer = []
        self.__indentation = 0
        self.__indent_string = indent_string
        self.__indent_temp = ""
        self.__string_buffer = ""

    def dedent(self):
        """
        Subtracts one indentation level.
        """
        self.__indentation -= 1
        self.__indent_temp = self.__indent_string*self.__indentation

    def indent(self):
        """
        Adds one indentation level.
        """
        self.__indentation += 1
        self.__indent_temp = self.__indent_string*self.__indentation

    def indent_string(self):
        """
        Return current indentation string.
        """
        return self.__indent_temp

    def clear(self):
        """
        Clear the buffer
        """
        self.__buffer = []

    def write(self, text, indent=True, newline=True):
        """
        Writes the string text to the buffer with indentation
        and a newline if not specified otherwise.
        """
        if text is None:
            raise CrystalError("Convert Error.")
        if indent:
            self.__buffer.append(self.__indent_temp)
        self.__buffer.append(text)
        if newline:
            self.__buffer.append("\n")

    def read(self, size=None):
        """
        Returns a string representation of the buffer.
        """
        if size is None:
            text = self.__string_buffer + "".join(self.__buffer)
            self.__buffer = []
            self.__string_buffer = ""
            return text

        if len(self.__string_buffer) < size:
            self.__string_buffer += "".join(self.__buffer)
            self.__buffer = []
            if len(self.__string_buffer) < size:
                text, self.__string_buffer = self.__string_buffer, ""
                return text
            else:
                text, self.__string_buffer = self.__string_buffer[:size], \
                    self.__string_buffer[size:]
                return text
        else:
            text, self.__string_buffer = self.__string_buffer[:size], \
                self.__string_buffer[size:]
            return text


def capitalize(text):
    """
    Returns a capitalized string.  Note that this differs
    from python's str.capitalize()/title() methods for
    cases like "fooBarBaz"
    """
    if text == '':
        return ''
    return text[0].upper() + text[1:]
