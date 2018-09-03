import os

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.mysql import BIGINT, BINARY, TIMESTAMP
from sqlalchemy.orm import sessionmaker

from cpchain import config
from cpchain.utils import join_with_rc

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'Trade'

    id = Column(Integer, primary_key=True)
    order_id = Column(BIGINT, nullable=False)
    order_type = Column(String, nullable=False)
    buyer_addr = Column(String, nullable=False)
    seller_addr = Column(String, nullable=False)
    market_hash = Column(String, nullable=False)
    AES_key = Column(BINARY, nullable=False)
    data_path = Column(String, nullable=False)
    order_delivered = Column(Boolean, nullable=False)
    time_stamp = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Trade(order_id= '%d', buyer_addr='%s', \
            seller_addr='%s', market_hash='%s', AES_key='%s', \
            uri='%s', order_delivered='%s', \
            time_stamp='%s')>" % (
                self.order_id, self.buyer_addr,
                self.seller_addr, self.market_hash,
                self.AES_key,
                self.data_path, self.order_delivered,
                self.time_stamp)

class ProxyDB(object):
    db_path = join_with_rc(config.proxy.dbpath)
    default_db = 'sqlite:///' + db_path

    def __init__(self, db=default_db):
        self.engine = create_engine(db, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def query(self, trade):
        return self.session.query(Trade).filter(
            Trade.order_id == trade.order_id,
            Trade.order_type == trade.order_type,
            Trade.buyer_addr == trade.buyer_addr,
            Trade.seller_addr == trade.seller_addr,
            Trade.market_hash == trade.market_hash
            ).first()

    def query_data_path(self, data_path):
        return self.session.query(Trade).filter(
            Trade.data_path == data_path).first()

    def insert(self, trade):
        trade.time_stamp = trade.time_stamp or datetime.now()
        self.session.add(trade)
        self.session.commit()

    def delete(self, trade):
        self.session.delete(trade)
        self.session.commit()

    def update(self):
        self.session.commit()

    def reclaim(self):
        reclaim_period = datetime.now() - timedelta(days=7)
        for instance in self.session.query(Trade).filter(
                Trade.time_stamp < reclaim_period).all():
            self.delete(instance)

        self.session.commit()
