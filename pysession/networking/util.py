import aiohttp

# TODO: untested codebase


async def _make_request(url: str, **kwargs: dict) -> aiohttp.ClientResponse:
    """Creates an ASYNC session and posts the given url

    Note: Close the session after using.
    """
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        return session.post(url, **kwargs)


async def request_text(url: str, **kwargs: dict) -> str:
    async with _make_request(url, **kwargs) as response:
        return response.text()


async def request_json(url: str, **kwargs: dict) -> dict:
    async with _make_request(url, **kwargs) as response:
        return response.json()


async def request_buffer(url: str, **kwargs: dict) -> aiohttp.StreamReader:
    async with _make_request(url, **kwargs) as response:
        return await response.content


async def request_jsonrpc(
    url: str, method: dict, params: dict, ignore_self_signed: bool = False
):
    if not url:
        raise Exception("No url given")

    body = {"jsonrpc": "2.0", "id": "0", "method": method, "params": params}
    headers = {"Content-Type": "application/json"}
    return await request_json(url, json=body, headers=headers)
