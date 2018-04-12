from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import BINARY, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from cpchain import config, root_dir

import os
from uuid import uuid1 as uuid

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'Trade'

    id = Column(Integer, primary_key=True)
    buyer_addr = Column(BINARY, nullable=False)
    seller_addr = Column(BINARY, nullable=False)
    market_hash = Column(BINARY, nullable=False)
    AES_key = Column(BINARY, nullable=False)
    file_hash = Column(BINARY, nullable=False)
    file_uuid = Column(String, nullable=False)
    time_stamp = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Trade(buyer_addr='%s', seller_addr='%s', \
            market_hash='%s', AES_key='%s', file_hash='%s' \
            file_uuid='%s' time_stamp='%s')>" % (self.buyer_addr,
            self.seller_addr, self.market_hash, self.AES_key,
            self.file_hash, self.file_uuid, self.time_stamp)

class ProxyDB(object):
    db_path = os.path.join(config.home, config.proxy.dbpath)
    db_path = os.path.expanduser(db_path)
    default_db = 'sqlite:///' + db_path

    def __init__(self, db=default_db):
        self.engine = create_engine(db, echo=False)
        Base.metadata.create_all(self.engine)

    def session_create(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def count(self, trade):
        count = self.session.query(Trade).filter(
                    Trade.buyer_addr ==  trade.buyer_addr,
                    Trade.seller_addr == trade.seller_addr,
                    Trade.market_hash == trade.market_hash).count()
        return count

    def query(self, trade):
        return self.session.query(Trade).filter(
                    Trade.buyer_addr ==  trade.buyer_addr,
                    Trade.seller_addr == trade.seller_addr,
                    Trade.market_hash == trade.market_hash).first()

    def query_file_uuid(self, uuid):
        return self.session.query(Trade).filter(
                    Trade.file_uuid == uuid).first()

    def insert(self, trade):
        trade.time_stamp = trade.time_stamp or datetime.now()
        trade.file_uuid = str(uuid())
        self.session.add(trade)
        self.session.commit()

    def delete(self, trade):
        self.session.delete(trade)
        self.session.commit()

    def session_close(self):
        self.session.close()

    def reclaim(self):
        reclaim_period = datetime.now() - timedelta(days=7)
        for instance in self.session.query(Trade).filter(
                        Trade.time_stamp < reclaim_period).all():
            self.delete(instance)

        self.session.commit()
        self.session_close()
