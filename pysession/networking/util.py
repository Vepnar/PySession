import aiohttp

# TODO: lightly tested
# TODO: prevent recreating of session objects


async def request_text(url: str, **kwargs: dict) -> str:
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return await response.text()


async def request_json(url: str, **kwargs: dict) -> dict:
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return await response.json()


async def request_text(url: str, **kwargs: dict) -> aiohttp.StreamReader:
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return response.content


async def request_jsonrpc(
    url: str, method: dict, params: dict, ignore_self_signed: bool = False
):
    if not url:
        raise Exception("No url given")

    body = {"jsonrpc": "2.0", "id": "0", "method": method, "params": params}
    headers = {"Content-Type": "application/json"}
    return await request_json(url, json=body, headers=headers)
