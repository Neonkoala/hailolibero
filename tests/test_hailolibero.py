import pytest
from aioresponses import aioresponses
from hailolibero import HailoLibero


@pytest.fixture
async def libero(scope="module"):
    client = HailoLibero(ip_address="example.com")
    yield client


@pytest.mark.asyncio
async def test_push_logged_out(libero: HailoLibero):
    with aioresponses() as mocked:
        mocked.get("/", status=301)
        mocked.post(
            '/login',
            headers={'Location': 'http://example.com:81/'},
            status=301
        )
        mocked.get(
            '/push',
            status=200,
            body="OK"
        )

        opened = await libero.open(False)
        assert opened

        mocked.assert_called_with('/push')


@pytest.mark.asyncio
async def test_push_already_logged_in(libero: HailoLibero):
    with aioresponses() as mocked:
        mocked.get("/", status=200)
        mocked.get(
            '/push',
            status=200,
            body="OK"
        )

        opened = await libero.open(False)
        assert opened

        mocked.assert_called_with('/push')
