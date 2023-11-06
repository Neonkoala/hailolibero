# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from aiohttp import *
import asyncio
from yarl import URL
from furl import furl

# base_url = URL('http://***REMOVED***:81')
base_ip_address = "***REMOVED***"


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

    async def close(self):
        await self.session.close()

    async def auth(self):
        print("Authing...")

        form_data = FormData()
        form_data.add_field("pin", self.pin)

        async with self.session.post('/login', data=form_data, allow_redirects=False) as response:
            if response.status == 301:
                print("Auth successful!")
            else:
                print("Auth failed.")

    async def check_auth(self):
        print("Checking if already authed...")

        async with self.session.get('/', allow_redirects=False) as response:
            if response.status == 200:
                print("Already authed...")

                return True
            else:
                print("Auth failed")

                return False

    async def push(self):
        async with self.session.get('/push') as response:
            print("URL:", response.url)
            print("Status:", response.status)

            data = await response.text()
            print("Open cabinet:", data)


async def test_run():
    libero = HailoLibero(ip_address=base_ip_address)

    authed = await libero.check_auth()

    if not authed:
        await libero.auth()

    # await libero.push()

    base_url = libero.base_url(base_ip_address)
    print(libero.jar.filter_cookies(request_url=base_url))

    await libero.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting HailoLibero client...')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_run())
