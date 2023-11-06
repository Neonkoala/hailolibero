# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from aiohttp import *
import asyncio
from yarl import URL

base_url = URL('http://***REMOVED***:81')


class HailoLibero:
    session: ClientSession
    jar = CookieJar(unsafe=True)

    def __init__(self, device_url: URL):
        self.session = ClientSession(device_url, cookie_jar=self.jar)

    async def configure(self, device_url: URL):
        print('Starting HailoLibero client...')

        # Cleanup old session first
        await self.session.close()

        self.session = ClientSession(device_url, cookie_jar=self.jar)

    async def close(self):
        await self.session.close()

    async def auth(self):
        form_data = FormData()
        form_data.add_field("pin", "hailo")
        # formData.add_field("submit", "")

        async with self.session.post('/login', data=form_data) as response:
            print("URL:", response.url)
            print("Status:", response.status)

    async def check_auth(self):
        print("Checking if already authed...")

        async with self.session.get('/', allow_redirects=False) as response:
            print("URL:", response.url)
            print("Status:", response.status)

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
    libero = HailoLibero(device_url=base_url)

    authed = await libero.check_auth()

    if not authed:
        await libero.auth()

    # await libero.push()

    print(libero.jar.filter_cookies(request_url=base_url))

    await libero.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting HailoLibero client...')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_run())
