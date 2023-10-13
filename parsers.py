from pprint import pprint
import re
from typing import Any

from requesters import AsyncGetRequester, AsyncPostRequester
from extracters import WaletBalanseExtracter, WaletTransactionExtracter
from bs4 import BeautifulSoup
import time
from random import randint

import asyncio
import aiohttp

headers = {
        'User-Agent'    : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.1.800 Yowser/2.5 Safari/537.36',
        'Content-Type' : 'application/json',
    }

class Sleeper:
    # Класс отвечает за задержку между запросами
    def __init__(self, max_sleep) -> None:
        self.num = 0
        self.max_sleep = max_sleep

    def sleep(self, *args: Any, **kwds: Any) -> Any:
        delay = 5 if self.num % 10 == 1 else randint(0, self.max_sleep * 10) / 10 \
              if randint(0, 1) == 1 else 0
        print(f'Sleep {delay} secs')
        time.sleep(delay) 
        self.num += 1


class AsyncParser:
    def __init__(self, requester, extracter, sleeper=None) -> None:
        super().__init__()
        self.__urls = None
        self.__bodies = None
        self.requester = requester
        self.extracter = extracter
        self.sleeper = sleeper

    @property
    def urls(self):
        return self.__urls

    @urls.setter
    def urls(self, urls):
        self.__urls = urls
    
    @property
    def bodies(self):
        return self.__bodies

    @bodies.setter
    def bodies(self, bodies):
        self.__bodies = bodies

    async def _make_one_page_task(self, url, body, session):
        print(f'Create task: {url} {body}')
        if self.sleeper:
            self.sleeper.sleep()
        data = await self.requester.make_request(url, body, session)
        print(f'Parsed: {url} {body}')
        return data
    
    @staticmethod
    def zip_urls_bodies(urls, bodies):
        url_len = len(urls)
        bodies_len = len(bodies)
        if all([url_len == 1, bodies_len != 1]):
            return list(zip(urls*bodies_len, bodies))
        elif all([url_len != 1, bodies_len == 1]):
            return list(zip(urls, bodies*url_len)) 
        else:
            return list(zip(urls, bodies)) 
        
    async def _get_many_page_tasks(self, urls, bodies):
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [self._make_one_page_task(url, body, session)
                                    for url, body in self.zip_urls_bodies(urls=urls,
                                                                        bodies=bodies)]
            data = await asyncio.gather(*tasks)
        return data

    async def parse(self):
        task = await self._get_many_page_tasks(self.urls, 
                                         self.bodies)
        data = self.extracter.extract(task)
        return list(data)


class WaletBalanceParser(AsyncParser):
    def __init__(self, wallet_address, api_key, requester, extracter, sleeper=None) -> None:
        super().__init__(requester, extracter, sleeper)
        self.address = wallet_address
        self.api_key = api_key
        self.urls = [f'https://api.bscscan.com/api?module=account&action=balance&address={self.address}&apikey={self.api_key}']
        self.bodies = [{}]

    async def parse(self):
        task = await self._get_many_page_tasks(self.urls, 
                                         self.bodies)
        data = self.extracter.extract(task)
        return {
            self.address : data
        }


class WaletTransactionsParser(AsyncParser):
    def __init__(self, wallet_address, api_key, requester, extracter, 
                 sleeper=None, offset=100, start_block=None, end_block=None) -> None:
        super().__init__(requester, extracter, sleeper)
        self.address = wallet_address
        self.api_key = api_key
        self.__start_block = start_block
        self.end_block = end_block
        self.offset = offset
        self.urls = [f'https://api.bscscan.com/api?module=account&action=txlist&address={self.address}&startblock={self.start_block}&endblock={self.end_block}&page=1&offset={self.offset}&sort=desc&apikey={self.api_key}']
        self.bodies = [{}]

    @property
    def start_block(self):
        return self.__start_block

    @start_block.setter
    def start_block(self, start_block):
        self.__start_block = start_block
        self.urls[0] = self.urls[0].replace(re.match('&startblock=(\d+)&', self.urls[0]).group(0), 
                                            start_block)

    async def parse(self, start_block):
        self.start_block = start_block
        task = await self._get_many_page_tasks(self.urls, 
                                         self.bodies)
        data = self.extracter.extract(task)
        return list(data)

# if __name__ == "__main__":
#     address = '0x295e26495CEF6F69dFA69911d9D8e4F3bBadB89B'
#     api_key = 'BWHU9UUTWCR7WTJC88UYGYDV7JHX2FTN9H'
#     parser = WaletTransactionsParser(address, start_block='32563743', 
#                                               end_block=32564115,
#                                               api_key=api_key,
#                                               requester=AsyncGetRequester(),
#                                               extracter=WaletTransactionExtracter())
#     pprint(asyncio.run(parser.parse()))