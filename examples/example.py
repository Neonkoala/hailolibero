# Hack to allow relative import above top level package
import os
import sys

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# Sample

from hailolibero import HailoLibero

import asyncio
import logging

base_ip_address = "***REMOVED***"


async def open_cabinet():
    libero = HailoLibero(ip_address=base_ip_address)

    await libero.open(dry_run=True)

    base_url = libero.base_url(base_ip_address)
    print(libero.jar.filter_cookies(request_url=base_url))

    await libero.cleanup()


if __name__ == "__main__":
    print("Starting HailoLibero example...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(open_cabinet())
