from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.models import Wallet, Balance, Transaction, Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


engine = create_async_engine('sqlite+aiosqlite:///wallets.db', echo=True)
Session = sessionmaker(bind=engine)


class DBProcesser:
    def __init__(self, Session) -> None:
        self.session_engine = Session

    async def create_wallet(self, wallet_address, session: AsyncSession):
        new_wallet = Wallet(address=wallet_address)
        session.add(new_wallet)
        await session.commit()
        return new_wallet

    async def get_wallet_by_name(self, wallet_address, session: AsyncSession):
        wallet = await session.query(Wallet)\
                                .filter_by(address=wallet_address).first()
        return wallet
        
    async def get_wallet_by_id(self, wallet_id, session: AsyncSession):
        return await session.query(Wallet).get(wallet_id)

    async def get_create_wallet_or_create(self, wallet_address, session: AsyncSession):
        wallet = await self.get_wallet_by_name(wallet_address)
        if not wallet:
            wallet = await self.create_wallet(session)
        return wallet

    async def add_wallets(self, wallet_addresses, session: AsyncSession):
        for wallet_address in wallet_address:
            new_wallet = Wallet(address=wallet_address)
            session.add(new_wallet)
        await session.commit()

    async def add_balance(self, wallet_address, amount, session: AsyncSession):
        wallet = await self.get_create_wallet_or_create(wallet_address)
        new_balance = Balance(amount=amount, wallet=wallet)
        session.add(new_balance)
        await session.commit() 
    
    async def add_transaction(self, transaction_data: dict, session: AsyncSession):
        data = {
            "sender_id" : await self.get_create_wallet_or_create(transaction_data.get('sender')).id,
            "receiver_id" : await self.get_create_wallet_or_create(transaction_data.get('receiver')).id,
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
        async with AsyncSession(engine) as session:
            wallet_address, balanse = balanse_data.items()
            await self.add_balance(wallet_address=wallet_address, 
                                amount=balanse)
            
class TransactionsDBProcesser(DBProcesser):
    __slots__ = ['add_transactions']
    async def __call__(self, transactions_data):
        async with AsyncSession(engine) as session:
            self.add_transactions(transactions_data)

    async def get_last_block(wallet_address):
        async with AsyncSession(engine) as session:
            return await session.query(Transaction).filter_by(address=wallet_address).order_by(Transaction.transaction_time.desc()).first().block

