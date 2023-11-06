# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from aiohttp import *
from furl import furl


class HailoLibero:
    session: ClientSession
    pin: str
    jar = CookieJar(unsafe=True)

    def __init__(self, ip_address: str, password: str = "hailo"):
        base_url = self.base_url(ip_address)

        self.session = ClientSession(base_url, cookie_jar=self.jar)
        self.pin = password

    @staticmethod
    def base_url(ip_address: str):
        return furl(scheme="http", host=ip_address, port=81).url

    async def configure(self, ip_address: str, pin: str):
        print('Starting HailoLibero client...')

        # Cleanup old session first
        await self.session.close()

        base_url = self.base_url(ip_address)

        self.session = ClientSession(base_url, cookie_jar=self.jar)
        self.pin = pin

    async def cleanup(self):
        await self.session.close()

    async def auth(self):
        print("Authing...")

        form_data = FormData()
        form_data.add_field("pin", self.pin)

        async with self.session.post('/login', data=form_data, allow_redirects=False) as response:
            # Assume if we are correctly authed we are redirected to homepage - "/"
            if response.status == 301:
                print("Auth successful!")

                return True
            else:
                print("Auth failed.")

                return False

    async def check_auth(self):
        print("Checking if already authed...")

        async with self.session.get('/', allow_redirects=False) as response:
            # Assume if already authed we won't get redirected
            if response.status == 200:
                print("Already authed...")

                return True
            else:
                print("Auth failed")

                return False

    async def open(self, dry_run=False):
        authed = await self.check_auth()

        if not authed:
            await self.auth()

        if dry_run:
            return

        async with self.session.get('/push') as response:
            print("URL:", response.url)
            print("Status:", response.status)

            data = await response.text()
            print("Open cabinet:", data)

            if data == "OK":
                print("Cabinet opened successfully!")

                return True
            else:
                print("Cabinet opening failed.")

                return False
