import os.path as osp

# https://qiita.com/zakuro9715/items/7e393ef1c80da8811027
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker


from cpchain import root_dir, config

dbpath = osp.join(root_dir, config.wallet.dbpath)
engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class FileInfo(Base):
    __tablename__ = 'fileinfo'
    hashcode = Column(String, primary_key=True)
    name = Column(String)
    path = Column(String)
    size = Column(Integer)
    remote_type = Column(String)
    remote_uri = Column(String)
    aes_key = Column(String)

    def __repr__(self):
        return "<FileInfo(path='%s', remote_uri='%s')>" % (self.path, self.remote_uri)


def create_table():
    """Use this to create all tables.
    """
    Base.metadata.create_all(engine)


fileinfo = FileInfo(hashcode=0x3234241, name="asdf", path="iasdf", size=3234, remote_type="asdf", remote_uri="asdfadsf")
