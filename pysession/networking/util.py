"""Utilities for sending async post requests"""

from typing import Any, Callable, Dict

import aiohttp

# TODO: create test case for "request_jsonrpc"
# TODO: prevent recreating of session objects


async def request_text(url: str, **kwargs) -> str:
    """Do a post request and return the retrieved data as str"""
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return await response.text()


async def request_json(url: str, **kwargs) -> dict:
    """Do an async post request and parse the returned json object"""
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return await response.json()


async def request_stream(
    url: str, stream_callback: Callable, **kwargs
) -> aiohttp.StreamReader:
    """Request a stream with a callback. This can be used for retrieving large binary blobs"""
    # Inject timeout of 30 seconds
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as response:
            assert response.status == 200
            return await stream_callback(response.content)


async def request_jsonrpc(
    url: str,
    method: Dict[str, Any],
    params: Dict[str, Any],
    ignore_self_signed: bool = False,
):
    if not url:
        raise Exception("No url given")

    body = {"jsonrpc": "2.0", "id": "0", "method": method, "params": params}
    headers = {"Content-Type": "application/json"}
    return await request_json(
        url, json=body, headers=headers, verify=not ignore_self_signed
    )
