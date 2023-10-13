from parsers import WaletBalanceParser, WaletTransactionsParser
from requesters import AsyncGetRequester
from extracters import WaletBalanseExtracter, WaletTransactionExtracter
from db.processers import BalanceDBProcesser, TransactionsDBProcesser, async_session
from app import App, BalansePipepline, TransactionsPipepline
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
address = '0x295e26495CEF6F69dFA69911d9D8e4F3bBadB89B'

pipelines = [
    BalansePipepline(parser=WaletBalanceParser(address, API_KEY, 
                                               AsyncGetRequester(), 
                                               WaletBalanseExtracter()), 
                     time_to_sleep=5, 
                     db_processer=BalanceDBProcesser(async_session)),

    TransactionsPipepline(parser=WaletTransactionsParser(address, API_KEY, 
                                                         AsyncGetRequester(), 
                                                         WaletTransactionExtracter()),
                     time_to_sleep=1, 
                     db_processer=TransactionsDBProcesser(async_session)),
]


if __name__ == '__main__':
    app = App()
    for pipeline in pipelines[::-1]:
        app.add_pipeline(pipeline)
    asyncio.run(app.start())
