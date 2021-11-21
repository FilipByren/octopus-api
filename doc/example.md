```python
from octopus_api import TentacleSession, OctopusApi
from typing import Dict, List

if __name__ == '__main__':
    async def get_ethereum_id(session: TentacleSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.json()
            return body["id"]


    async def get_text(session: TentacleSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.text()
            return body


    client = OctopusApi(concurrency=100)
    result: List = client.execute(requests_list=[{
        "url": "http://google.com",
        "params": {}}] * 100, func=get_text)
    print(result)

    # Optimized based on rate limiting
    client = OctopusApi(rate=30, resolution="minute")
    result: List = client.execute(requests_list=[{
        "url": "http://api.coingecko.com/api/v3/coins/ethereum?tickers=false&localization=false&market_data=false",
        "params": {}}] * 100, func=get_ethereum_id)
    print(result)

```