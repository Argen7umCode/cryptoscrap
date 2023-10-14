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
address = '0xa6f79B60359f141df90A0C745125B131cAAfFD12'.lower()

pipelines = [
    BalansePipepline(parser=WaletBalanceParser(address, API_KEY, 
                                               AsyncGetRequester(), 
                                               WaletBalanseExtracter()), 
                     time_to_sleep=15, 
                     db_processer=BalanceDBProcesser(async_session)),

    TransactionsPipepline(parser=WaletTransactionsParser(address, API_KEY,
                                                         AsyncGetRequester(), 
                                                         WaletTransactionExtracter()),
                     time_to_sleep=5, 
                     db_processer=TransactionsDBProcesser(async_session)),
]


if __name__ == '__main__':
    app = App()
    for pipeline in pipelines[::-1]:
        app.add_pipeline(pipeline)
    asyncio.run(app.start())
