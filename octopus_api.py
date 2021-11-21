import asyncio
import time
from typing import List, Dict, Any

import aiohttp
from more_itertools import chunked
from tqdm import tqdm


class TentacleSession(aiohttp.ClientSession):
    sleep: float
    retries: int
    retry_sleep: float = 1.0

    def __init__(self, sleep: float, retries=3, retry_sleep=1.0, **kwargs):
        self.retries = retries
        self.sleep = sleep
        self.retry_sleep = retry_sleep
        super().__init__(raise_for_status=True, **kwargs)

    def __retry__(self, func, **kwargs) -> Any:
        attempts = 0
        error = Exception()
        while attempts < self.retries:
            try:
                start_time = time.time()
                resp = func(**kwargs)
                response_time = round(time.time() - start_time, 1)
                if response_time < self.sleep:
                    time.sleep(self.sleep - response_time)
                return resp
            except Exception as error:
                attempts += 1
                error = error
                time.sleep(self.retry_sleep)

        raise error

    def get(self, **kwargs) -> Any:
        return self.__retry__(func=super().get, **kwargs)

    def patch(self, **kwargs) -> Any:
        return self.__retry__(func=super().patch, **kwargs)

    def post(self, **kwargs) -> Any:
        return self.__retry__(func=super().post, **kwargs)

    def put(self, **kwargs) -> Any:
        return self.__retry__(func=super().put, **kwargs)

    def request(self, **kwargs) -> Any:
        return self.__retry__(func=super().request, **kwargs)


class OctopusApi:
    rate_sec: float = None
    concurrency: int
    retries: int

    def __init__(self, rate: int = None, resolution: str = None, concurrency: int = 30,
                 retries: int = 3):

        if rate or resolution:
            if resolution.lower() not in ["minute", "sec"]:
                raise ValueError("Incorrect value of resolution, expecting minute or sec!")
            if not rate:
                raise ValueError("Can not set resolution of rate without rate")
            self.rate_sec = rate / (60 if resolution.lower() == "minute" else 1)

        self.concurrency = concurrency if not rate else 1
        self.retries = retries

    def execute(self, requests_list: List[Dict[str, Any]], func: callable) -> List[Any]:

        async def __tentacles__(rate: float, retries: int, concurrency: int, requests_list: List[Dict[str, Any]],
                                func: callable) -> List[Any]:
            sleep: float = 0
            if rate:
                sleep = round(1 / rate, 2)
            conn = aiohttp.TCPConnector(limit_per_host=concurrency)
            async with TentacleSession(sleep=sleep, retries=retries, connector=conn) as session:
                return await asyncio.gather(
                    *[func(session, request) for request in requests_list])

        batches = chunked(requests_list, self.concurrency)
        results = list()
        for batch in tqdm(list(batches)):
            r = asyncio.run(__tentacles__(self.rate_sec, self.retries, self.concurrency, batch, func))
            results.extend(r)

        return results
