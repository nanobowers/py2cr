#!/usr/bin/env python3


def nested_containers():
    CODES = {"KEY": [1, 3]}
    return 1 in CODES["KEY"]


if nested_containers():
    print("OK")
