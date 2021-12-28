from typing import List, Dict
from unittest import TestCase

import aiohttp

from octopus_api import TentacleSession, OctopusApi


class OctopusApiTest(TestCase):
    def test_1_rate_limited_endpoint(self):
        async def get_response(session: TentacleSession, request: Dict):
            async with session.get(url=request["url"], params=request["params"]) as response:
                body = await response.json()
                return body

        client = OctopusApi(rate=59, resolution="minute", connections=10)
        result: List = client.execute(requests_list=[{
            "url": "http://server:3000/",
            "params": {}}] * 60, func=get_response)
        assert result == [{"msg": "Hello World"}] * 60

    def test_2_above_rate_limit(self):
        async def get_response(session: TentacleSession, request: Dict):
            async with session.get(url=request["url"], params=request["params"]) as response:
                text = await response.text()
                return text

        client = OctopusApi(rate=100, connections=50, resolution="sec")
        try:
            _: List = client.execute(requests_list=[{
                "url": "http://server:3000/",
                "params": {}}] * 200, func=get_response)
        except aiohttp.client_exceptions.ClientResponseError as error:
            assert "Too Many Requests" == error.message
