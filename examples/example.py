# Hack to allow relative import above top level package
import os
import sys

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# Sample

from hailolibero import HailoLibero

import asyncio
import logging

base_ip_address = os.environ.get("IP_ADDRESS", "127.0.0.1")
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper()
)

async def interact_with_hailo():
    libero = HailoLibero(ip_address=base_ip_address)

    await libero.read_settings(dry_run=True)
    await libero.open(dry_run=True)

    libero.settings.led.value = 6
    await libero.write_settings(dry_run=True)

    base_url = libero.base_url(base_ip_address)

    print(libero.jar.filter_cookies(request_url=base_url))
    print(f"Current libero settings: {libero.settings}")
    print(f"Current libero info: {libero.info}")
    await libero.restart(dry_run=True)
    await libero.cleanup()


if __name__ == "__main__":
    print("Starting HailoLibero example...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(interact_with_hailo())
