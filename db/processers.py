from sqlalchemy import select, or_
from db.models import Wallet, Balance, Transaction, Base
from db import AsyncSession, async_session

class DBProcesser:
    def __init__(self, async_session) -> None:
        self.session_engine = async_session

    async def create_wallet(self, wallet_address, session: AsyncSession):
        new_wallet = Wallet(address=wallet_address)
        session.add(new_wallet)
        await session.commit()
        return new_wallet

    async def get_wallet_by_name(self, wallet_address, session: AsyncSession):
        wallet = await session.execute(select(Wallet)\
                                       .filter_by(address=wallet_address))
        return wallet.first()
        
    async def get_wallet_by_id(self, wallet_id, session: AsyncSession):
        wallet = await session.execute(select(Wallet).get(wallet_id))
        return wallet.first()

    
    async def get_or_create_wallet(self, wallet_address, session: AsyncSession):
        wallet = await self.get_wallet_by_name(wallet_address, session)
        if not wallet:
            wallet = await self.create_wallet(wallet_address, session)
        return wallet

    async def add_wallets(self, wallet_addresses, session: AsyncSession):
        for wallet_address in wallet_address:
            new_wallet = Wallet(address=wallet_address)
            session.add(new_wallet)
        await session.commit()

    async def add_balance(self, wallet_address, amount, session: AsyncSession):
        wallet = await self.get_or_create_wallet(wallet_address)
        new_balance = Balance(amount=amount, wallet=wallet)
        session.add(new_balance)
        await session.commit() 
    
    async def add_transaction(self, transaction_data: dict, session: AsyncSession):
        data = {
            "sender_id" : await self.get_or_create_wallet(transaction_data.get('sender')).id,
            "receiver_id" : await self.get_or_create_wallet(transaction_data.get('receiver')).id,
            "amount" : transaction_data.get('receiver'),
            "hash" : transaction_data.get('hash'),
            "transaction_time" : transaction_data.get('transaction_time'),
            "status" : transaction_data.get('status'),
            "block" : transaction_data.get('block'),
        }

        transaction = Transaction(data)
        session.add(transaction)
        await session.commit()

    async def add_transactions(self, transactions_data: [dict], session: AsyncSession):
        for transaction_data in transactions_data:
            await self.add_transaction(transaction_data, session)
        await session.commit()


class BalanceDBProcesser(DBProcesser):
    __slots__ = ['add_balance']
    async def __call__(self, balanse_data):
        async with async_session() as session:
            wallet_address, balanse = balanse_data.items()
            await self.add_balance(wallet_address=wallet_address, 
                                amount=balanse, session=session)
            
class TransactionsDBProcesser(DBProcesser):
    __slots__ = ['add_transactions']
    async def __call__(self, transactions_data):
        async with async_session() as session:
            self.add_transactions(transactions_data, session)

    async def get_last_block(self, wallet_address):
        async with async_session() as session:
            wallet = await self.get_or_create_wallet(wallet_address, session)
            transaction = await session.execute(select(Transaction).filter(or_(sender_id=wallet.id, receiver_id=wallet.id))\
                                                            .order_by(Transaction.transaction_time.desc()))
            return transaction.first().block
