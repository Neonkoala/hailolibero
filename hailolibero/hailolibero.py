import asyncio
import atexit
import logging
import os
from aiohttp import *
from furl import furl
from bs4 import BeautifulSoup

import typing
from pydantic import BaseModel

class HailoValue(BaseModel):
    value: int
    min: int
    max: int

class HailoSettings(BaseModel):

    led: HailoValue
    pwr: HailoValue
    dist: HailoValue

    ssid: str
    key: str

    # dhcp = 1, static = 0
    ipconf: bool

    ip: str = None
    subnet: str = None
    gateway: str  = None

class HailoInfo(BaseModel):

    device: str
    firmware: str

    status: str

    dhcp_ip: str = None
    dhcp_subnet: str = None

class HailoLibero:
    session: ClientSession
    pin: str
    jar: None
    settings: HailoSettings
    info: HailoInfo
    ip_address: str

    def __init__(self, ip_address: str, password: str = "hailo"):

        logging.info("Starting HailoLibero client...")

        self.ip_address = ip_address
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

        base_url = self.base_url(self.ip_address)
        self.jar = CookieJar(unsafe=True)
        self.session = ClientSession(base_url, cookie_jar=self.jar)
        self.pin = pin

    async def cleanup(self):
        await self.session.close()

    async def auth(self):
        logging.debug("Authing...")

        base_url = self.base_url(self.ip_address)
        self.jar = CookieJar(unsafe=True)
        self.session = ClientSession(base_url, cookie_jar=self.jar)

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

    async def read_settings(self):
        result_settings = {}
        result_info = {}

        logging.debug("Reading settings..")
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        try:
            async with self.session.get("/", allow_redirects=False) as response:
                data = await response.text()

                soup = BeautifulSoup(data, 'html.parser')

                # Settings
                for input in soup.find_all(lambda t: t.name == 'input'
                                                        and ( not t.get('class') or 'button' not in t.get('class') )
                                                        and ( t.get('type') != 'radio' or t.get('checked') != None )
                                            ):
                    if input.get('type') == 'range':
                        result_settings[input.get('name')] = {
                                'value': input.get('value'),
                                'min':  input.get('min'),
                                'max': input.get('max')
                            }
                    else:
                        result_settings[input.get('name')] = input.get('value')

                self.settings = HailoSettings.parse_obj({**result_settings})

                # Info
                p = soup.find("p")
                spans = p.findChildren("span")

                result_info = {
                    'device':      spans[0].next_sibling[1:],
                    'firmware':    spans[1].next_sibling[1:],
                    'status':      spans[2].next_sibling[1:],
                    'dhcp_ip':     spans[4].next_sibling[1:],
                    'dhcp_subnet': spans[5].next_sibling[1:]
                }
                self.info = HailoInfo.parse_obj({**result_info})
                return True

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))

    async def write_settings(self,dry_run=False):
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        if dry_run:
            logging.debug("Dry run..")
            return True

        form_data = FormData()
        form_data.add_field("led", self.settings.led.value)
        form_data.add_field("pwr", self.settings.pwr.value)
        form_data.add_field("dist", self.settings.dist.value)

        try:
            logging.debug(f"Writing settings.. {form_data}")
            async with self.session.post("/settings", data=form_data, allow_redirects=False) as response:
                data = await response.text()
                if response.status == 200:
                    logging.info(f"Write settings: {data}")
                    return True
                else:
                    logging.error(f"Error writing settings: {data}")
                    return False

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))

    async def restart(self,dry_run=False):
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        if dry_run:
            logging.debug("Dry run..")
            return True

        try:
            logging.debug("Restarting..")
            async with self.session.post("/restart", allow_redirects=False) as response:
                data = await response.text()
                if response.status == 200:
                    logging.info(f"Result: {data}")
                    return True
                else:
                    logging.error(f"Error restarting: {data}")
                    return False

        except ClientConnectorError as e:
            logging.error("Connection Error", str(e))

    async def open(self, dry_run=False):
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        if dry_run:
            logging.debug("Dry run..")
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
