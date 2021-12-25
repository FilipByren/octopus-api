# octopus-api
![octopus_icon](https://github.com/FilipByren/octopus-api/blob/main/image.png?raw=true)
## About
Octopus-api is a python library for performing client-based optimized concurrent requests and limit rates set by the endpoint contract.

Octopus-api is simple; it combines the [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) library's functionality and makes sure the requests follows the constraints set by the contract.

## Installation
`pip install octopus-api`

## PyPi
https://pypi.org/project/octopus-api/


## Get started
To start Octopus, you first initiate the client, setting your constraints. 
```python
client = OctopusApi(rate=30, resolution="minute", retries=10)
client = OctopusApi(rate=5, resolution="sec", retries=3)
client = OctopusApi(concurrency=100, retries=5)
```
After that, you will specify what you want to perform on the endpoint response. This is done within a user-defined function.
```python
async def patch_data(session: TentacleSession, request: Dict):
    async with session.patch(url=request["url"], data=requests["data"], params=request["params"]) as response:
        body = await response.json()
        return body["id"]
```

As Octopus `TentacleSession` uses [aiohttp](https://docs.aiohttp.org/en/stable/) under the hood, the resulting  way to write 
**POST**, **GET**, **PUT** and **PATCH** for aiohttp will be the same for octopus. The only difference is the added functionality of 
retries and rate limits (if set).

Finally, you finish everything up with the `execute` call for the octopus client, where you provide the list of requests dicts your defined and the user function. The execute call will then return the waited list of returned values.

```python
result: List = client.execute(requests_list=[
    {
        "url": "http://localhost:3000",
        "data": {"id": "a", "first_name": "filip"},
        "params": {"id": "a"}
    },
    {
        "url": "http://localhost:3000",
        "data": {"id": "b", "first_name": "morris"},
        "params": {"id": "b"} 
    }
    ] , func=patch_data)
```


### Examples

Optimize the request based concurrency constraints:
```python
from octopus_api import TentacleSession, OctopusApi
from typing import Dict, List

if __name__ == '__main__':
    async def get_text(session: TentacleSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.text()
            return body


    client = OctopusApi(concurrency=100)
    result: List = client.execute(requests_list=[{
        "url": "http://google.com",
        "params": {}}] * 100, func=get_text)
    print(result)

```
Optimize the request based on rate limit constraints:
```python
from octopus_api import TentacleSession, OctopusApi
from typing import Dict, List

if __name__ == '__main__':
    async def get_ethereum_id(session: TentacleSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.json()
            return body["id"]

    client = OctopusApi(rate=30, resolution="minute")
    result: List = client.execute(requests_list=[{
        "url": "http://api.coingecko.com/api/v3/coins/ethereum?tickers=false&localization=false&market_data=false",
        "params": {}}] * 100, func=get_ethereum_id)
    print(result)

```
Optimize the request based on rate limit and concurrency limit:
```python
from octopus_api import TentacleSession, OctopusApi
from typing import Dict, List

if __name__ == '__main__':
    async def get_ethereum(session: TentacleSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.json()
            return body

    client = OctopusApi(rate=50, resolution="sec", concurrency=6)
    result: List = client.execute(requests_list=[{
        "url": "https://api.pro.coinbase.com/products/ETH-EUR/candles?granularity=900&start=2021-12-04T00:00:00Z&end=2021-12-04T00:00:00Z",
        "params": {}}] * 1000, func=get_ethereum)
    print(result)
```


## Limitations
1. Returned result from the user defined function comes in out of order.
