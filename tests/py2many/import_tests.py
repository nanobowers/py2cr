#!/usr/bin/env python3

import typing


def test():
    a: typing.List[int] = [1, 2, 3]
    return a[1]


b = test()
assert b == 2
print("OK")
