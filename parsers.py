from datetime import datetime
import re
from typing import Any
from string import Template

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
        print(f'\033[34m{datetime.now()}: Sleep {delay} secs\033[0m')
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
        print(f'\033[37m{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: \033[33mCreate task: {self.__class__.__name__}\033[0m')
        if self.sleeper:
            self.sleeper.sleep()
        data = await self.requester.make_request(url, body, session)
        print(f'\033[37m{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: \033[32mParsed: {self.__class__.__name__}\033[0m')
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
        self.address = wallet_address.lower()
        self.api_key = api_key
        self.urls = [f'https://api.bscscan.com/api?module=account&action=balance&address={self.address}&apikey={self.api_key}']
        self.bodies = [{}]

    async def parse(self):
        task = await self._get_many_page_tasks(self.urls, 
                                         self.bodies)
        data = list(self.extracter.extract(task))
        return {
            self.address : data[0]
        }


class WaletTransactionsParser(AsyncParser):
    def __init__(self, wallet_address, api_key, requester, extracter, 
                 sleeper=None, offset=1000, start_block=None, end_block=None) -> None:
        super().__init__(requester, extracter, sleeper)
        self.address = wallet_address.lower()
        self.api_key = api_key
        self.__start_block = start_block
        self.end_block = end_block
        self.offset = offset
        self.url_template = Template(f'https://api.bscscan.com/api?module=account&action=txlist&address={self.address}&startblock=$startblock&endblock={self.end_block}&page=1&offset={self.offset}&sort=desc&apikey={self.api_key}')
        self.urls = [self.url_template.substitute(startblock=start_block)]
        self.bodies = [{}]

    @property
    def start_block(self):
        return self.__start_block

    @start_block.setter
    def start_block(self, start_block):
        self.urls[0] = self.url_template.substitute(startblock=start_block)
        self.__start_block = start_block
        


    async def parse(self, start_block):
        self.start_block = start_block
        task = await self._get_many_page_tasks(self.urls, 
                                         self.bodies)
        data = list(self.extracter.extract(task))
        return data

