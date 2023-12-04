import asyncio
import atexit
import logging
import os
from aiohttp import *
from furl import furl


class HailoLibero:
    session: ClientSession
    pin: str
    jar = CookieJar(unsafe=True)

    def __init__(self, ip_address: str, password: str = "hailo"):
        logging.basicConfig(
            level=os.environ.get("LOGLEVEL", "INFO").upper()
        )

        logging.info("Starting HailoLibero client...")

        base_url = self.base_url(ip_address)

        self.session = ClientSession(base_url, cookie_jar=self.jar)
        self.pin = password

        atexit.register(self._shutdown)

    def _shutdown(self):
        asyncio.run(self.session.close())

    @staticmethod
    def base_url(ip_address: str):
        return furl(scheme="http", host=ip_address, port=81).url

    async def configure(self, ip_address: str, pin: str):
        # Cleanup old session first
        await self.session.close()

        base_url = self.base_url(ip_address)

        self.session = ClientSession(base_url, cookie_jar=self.jar)
        self.pin = pin

    async def cleanup(self):
        await self.session.close()

    async def auth(self):
        logging.debug("Authing...")

        form_data = FormData()
        form_data.add_field("pin", self.pin)

        try:
            async with self.session.post("/login", data=form_data, allow_redirects=False) as response:
                # Assume if we are correctly authed we are redirected to homepage - "/"
                if response.status == 301:
                    redirect_header = response.headers.get("Location")

                    if furl(redirect_header).path == "/":
                        logging.debug("Auth successful!")
                        return True

                logging.debug("Auth failed.")

                return False

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))

    async def check_auth(self):
        logging.debug("Checking if already authed...")

        try:
            async with self.session.get("/", allow_redirects=False) as response:
                # Assume if already authed we won't get redirected
                if response.status == 200:
                    logging.debug("Already authed...")

                    return True
                elif response.status == 301:
                    logging.debug("Not authed")

                    return False
                else:
                    raise Exception("Unknown auth error")

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))

    async def open(self, dry_run=False):
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        if dry_run:
            return True

        try:
            async with self.session.get("/push") as response:
                data = await response.text()
                logging.debug("Open cabinet response:", data)

                if response.status == 200 and data == "OK":
                    logging.info("Cabinet opened successfully!")

                    return True
                else:
                    logging.info("Cabinet opening failed.")

                    return False

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))
