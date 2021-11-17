#!/usr/bin/env python3

import asyncio


async def nested() -> int:
    return 42


async def async_main():
    assert await nested() == 42
    print("OK")


asyncio.run(async_main())
