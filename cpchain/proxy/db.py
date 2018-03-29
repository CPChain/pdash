from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import BINARY, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from cpchain import config

Base = declarative_base()

default_db = 'sqlite:///' + config.proxy.dbpath

class Trade(Base):
    __tablename__ = 'Trade'

    id = Column(Integer, primary_key=True)
    buyer_addr = Column(BINARY, nullable=False)
    seller_addr = Column(BINARY, nullable=False)
    market_hash = Column(BINARY, nullable=False)
    AES_key = Column(BINARY, nullable=False)
    file_hash = Column(BINARY, nullable=False)
    time_stamp = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Trade(buyer_addr='%s', seller_addr='%s', \
            market_hash='%s', AES_key='%s', file_hash='%s' \
            time_stamp='%s')>" % (self.buyer_addr, \
            self.seller_addr, self.market_hash, self.AES_key, \
            self.file_hash, self.time_stamp)

def db_session_create(db=default_db):
    engine = create_engine(db, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def db_count(session, trade):
    count = session.query(Trade).filter(
                Trade.buyer_addr ==  trade.buyer_addr,
                Trade.seller_addr == trade.seller_addr,
                Trade.market_hash == trade.market_hash,
                Trade.AES_key == trade.AES_key,
                Trade.file_hash == trade.file_hash).count()
    return count

def db_query(session, trade):
    instances = session.query(Trade).filter(
                Trade.buyer_addr ==  trade.buyer_addr,
                Trade.seller_addr == trade.seller_addr,
                Trade.market_hash == trade.market_hash,
                Trade.AES_key == trade.AES_key,
                Trade.file_hash == trade.file_hash).all()
    return instances

def db_insert(session, trade):
    trade.time_stamp = datetime.now()
    session.add(trade)
    session.commit()

def db_delete(session, trade):
    session.delete(trade)
    session.commit()

def db_session_close(session):
    session.close()

def db_reclaim(db=default_db):
    session = db_session_create(db)

    reclaim_period = datetime.now() - timedelta(days=3)
    for instance in session.query(Trade).filter(
                    Trade.time_stamp < reclaim_period).all():
        db_delete(session, instance)

    session.commit(session)
    db_session_close(session)
