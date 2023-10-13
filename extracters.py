from abc import ABC, abstractmethod
from functools import reduce
from typing import Any
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime

class Extracter(ABC):

    @staticmethod
    def get_html_page_from_response(response):
        return(response.get('html'))

    @staticmethod
    def get_json_from_response(response):
        return(response.get('json'))

    @staticmethod
    def get_status_code_page_from_response(response):
        return(response.get('status'))

    @abstractmethod
    def extract(self, responce: dict):
        pass

class WaletBalanseExtracter(Extracter):
    
    def extract_one(self, response: dict):
        data = response.get('json')
        try:
            return int(data.get('result')) / 10**18
        except Exception as ex: 
            print(ex)

    def extract_many(self, responses: [dict]):
        return (self.extract_one(response) for response in responses)
    
    def extract(self, data: Any):
        return self.extract_one(data) if isinstance(data, dict) \
                                      else self.extract_many(data)
    

class WaletTransactionExtracter(Extracter):   

    def get_field(self, data, field_name):
        try:
            return data.get(field_name)
        except:
            return None

    def get_sender(self, data):
        return self.get_field(data, 'from')
    
    def get_receiver(self, data):
        return self.get_field(data, 'to')

    def get_amount(self, data):
        return int(self.get_field(data, 'value')) / 10**18
    
    def get_hash(self, data):
        return self.get_field(data, 'hash')

    def get_transaction_time(self, data):
        return datetime.fromtimestamp(int(self.get_field(data, 'timeStamp')))

    def get_status(self, data):
        return self.get_field(data, 'functionName')
    
    def get_block(self, data):
        return self.get_field(data, 'blockNumber')

    def extract_data(response):
        return response

    def extract_one(self, response: dict):
        data = response.get('json').get('result')
        return [{
            'sender'           : self.get_sender(transaction),
            'receiver'         : self.get_receiver(transaction),
            'amount'           : self.get_amount(transaction),
            'hash'             : self.get_hash(transaction),
            'transaction_time' : self.get_transaction_time(transaction),
            'status'           : self.get_status(transaction),
            'block'            : self.get_block(transaction)
        } for transaction in data]

    def extract_many(self, responses: [dict]):
        return reduce(lambda a, b: a+b, (self.extract_one(response) for response in responses))
    
    def extract(self, data: Any):
        return self.extract_one(data) if isinstance(data, dict) \
                                      else self.extract_many(data)
    