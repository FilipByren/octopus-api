import asyncio
import time
from typing import List, Dict, Any

import aiohttp
from tqdm import tqdm


class TentacleSession(aiohttp.ClientSession):
    """ TentacleSession is a wrapper around the aiohttp.ClientSession, where it introduces the retry and rate functionality
     missing in the default aiohttp.ClientSession.

        Args:
            sleep (float): The time the client will sleep after each request. \n
      	    retries (int): The number of retries for a successful request. \n
     	    retry_sleep (float): The time service sleeps between nonsuccessful request calls. Defaults to 1.0.

        Returns:
            TentacleSession(aiohttp.ClientSession)
    """
    retries: int
    retry_sleep: float = 1.0

    def __init__(self, retries=3, retry_sleep=1.0, **kwargs):
        self.retries = retries
        self.retry_sleep = retry_sleep
        super().__init__(raise_for_status=True, **kwargs)

    def __retry__(self, func, **kwargs) -> Any:
        attempts = 0
        error = Exception()
        while attempts < self.retries:
            try:
                return func(**kwargs)
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
    """ Initiates the Octopus client.
        Args:
            rate (Optional[float]): The rate limits of the endpoint; default to no limit. \n
 	        resolution (Optional[str]): The time resolution of the rate (sec, minute), defaults to None.
	        concurrency (int): Maximum concurrency on the given endpoint, defaults to 30.

        Returns:
            OctopusApi
    """
    rate_sec: float = None
    concurrency: int
    retries: int

    def __init__(self, rate: int = None, resolution: str = None, concurrency: int = 5,
                 retries: int = 3):

        if rate or resolution:
            if resolution.lower() not in ["minute", "sec"]:
                raise ValueError("Incorrect value of resolution, expecting minute or sec!")
            if not rate:
                raise ValueError("Can not set resolution of rate without rate")
            self.rate_sec = rate / (60 if resolution.lower() == "minute" else 1)

        self.concurrency = concurrency
        self.retries = retries

    def execute(self, requests_list: List[Dict[str, Any]], func: callable) -> List[Any]:
        """ Execute the requests given the functions instruction.

            Empower asyncio libraries for performing parallel executions of the user-defined function.
            Given a list of requests, the result is an out of order list of what the user-defined function returns.

            Args:
                requests_list (List[Dict[str, Any]): The list of requests in a dictionary format, e.g.
                [{"url": "http://example.com", "params": {...}, "body": {...}}..]
                func (callable): The user-defined function to execute, this function takes in the following arguments.
                    Args:
                        session (TentacleSession): The Octopus wrapper around the aiohttp.ClientSession.
                        request (Dict): The request within the requests_list above.

            Returns:
                List(func->return)
        """

        async def __tentacles__(rate: float, retries: int, concurrency: int, requests_list: List[Dict[str, Any]],
                                func: callable) -> List[Any]:

            responses: list = []
            progress_bar = tqdm(total=len(requests_list))
            sleep = 1 / rate if rate else 0

            async def func_mod(session: TentacleSession, request: Dict):
                resp = await func(session, request)
                responses.append(resp)
                progress_bar.update()

            conn = aiohttp.TCPConnector(limit_per_host=concurrency)
            async with TentacleSession(retries=retries, connector=conn) as session:

                tasks = set()
                for request in requests_list:
                    if len(tasks) >= self.concurrency:
                        _done, tasks = await asyncio.wait(
                            tasks, return_when=asyncio.FIRST_COMPLETED)
                    tasks.add(asyncio.create_task(func_mod(session, request)))
                    await asyncio.sleep(sleep)
                await asyncio.wait(tasks)
                return responses

        result = asyncio.run(__tentacles__(self.rate_sec, self.retries, self.concurrency, requests_list, func))
        if result:
            return result
        return []
