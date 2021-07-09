"""Unit test for /pysession/networking/util.py"""
import pytest
from aiohttp.client_exceptions import ContentTypeError

from pysession.networking.util import request_json, request_stream, request_text


@pytest.fixture
def http_bin_url():
    return "https://httpbin.org/"


@pytest.mark.asyncio
async def test_valid_json(http_bin_url):
    result = await request_json(http_bin_url + "/anything")

    assert "method" in result
    assert result["method"] == "POST"


@pytest.mark.asyncio
async def test_invalid_json(http_bin_url):
    try:
        await request_json(http_bin_url + "/status/200")
        assert False
    except ContentTypeError:
        pass


@pytest.mark.asyncio
async def test_error_request(http_bin_url):
    """Test if the buildin error status code checker works"""
    try:
        await request_text(http_bin_url + "/status/500")
        assert False
    except AssertionError:
        pass


@pytest.mark.asyncio
async def test_http_timeout(http_bin_url):
    """Test a timeout of 10 seconds. This should be 31 seconds to work"""
    await request_text(http_bin_url + "/delay/10")


@pytest.mark.asyncio
async def test_valid_text(http_bin_url):
    result = await request_text(http_bin_url + "/status/200")
    assert not result


@pytest.mark.asyncio
async def test_valid_buffer(http_bin_url):
    """Test http streams"""

    async def handle_stream(stream):
        """Handle data stream"""
        buffer = ""
        async for data, _ in stream.iter_chunks():
            buffer += data.decode("UTF-8")
        return buffer

    buffer = await request_stream(http_bin_url + "/anything", handle_stream)
    assert "https://httpbin.org/anything" in buffer
