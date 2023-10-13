from parsers import WaletBalanceParser, WaletTransactionsParser
from requesters import AsyncGetRequester
from extracters import WaletBalanseExtracter, WaletTransactionExtracter
from db.processers import BalanceDBProcesser, TransactionsDBProcesser, Session
from app import App, BalansePipepline, TransactionsPipepline
import asyncio
from decouple import Config

config = Config()

api_key = config.get('API_KEY')
address = '0x295e26495CEF6F69dFA69911d9D8e4F3bBadB89B'

pipelines = [
    BalansePipepline(parser=WaletBalanceParser(address, API_KEY, 
                                               AsyncGetRequester(), 
                                               WaletBalanseExtracter()), 
                     time_to_sleep=5, 
                     db_processer=BalanceDBProcesser(Session)),

    TransactionsPipepline(parser=WaletTransactionsParser(address, API_KEY, 
                                                         AsyncGetRequester(), 
                                                         WaletTransactionExtracter()),
                     time_to_sleep=1, 
                     db_processer=TransactionsDBProcesser(Session)),
]


if __name__ == '__main__':
    app = App()
    for pipeline in pipelines[::-1]:
        app.add_pipeline(pipeline)
    asyncio.run(app.start())
