import asyncio
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from db import engine


Base = declarative_base()

# Определяем класс для таблицы "Кошельки"
class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True)

    # Определяем отношение кошельков с их балансами
    balances = relationship('Balance', back_populates='wallet')

# Определяем класс для таблицы "Балансы"
class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    wallet_id = Column(Integer, ForeignKey('wallets.id'))

    # Определяем отношение балансов с соответствующим кошельком
    wallet = relationship('Wallet', back_populates='balances')

# Определяем класс для таблицы "Транзакции"
class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('wallets.id'))
    receiver_id = Column(Integer, ForeignKey('wallets.id'))
    amount = Column(Float)
    hash = Column(String)
    transaction_time = Column(DateTime)
    status = Column(String)
    block = Column(Integer)

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init())