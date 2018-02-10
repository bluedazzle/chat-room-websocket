# coding: utf-8
from __future__ import unicode_literals

from sqlalchemy import Column, String, DateTime, Integer, Boolean, create_engine, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'core_partyuser'

    id = Column(Integer, primary_key=True)
    nick = Column(String)
    fullname = Column(String)
    room_id = Column(Integer)
    token = Column(String)
    active = Column(Boolean)


engine = create_engine('postgresql+psycopg2://postgres:123456qq@localhost:5432/ktv',
                       encoding='utf-8'.encode())

DBSession = sessionmaker(bind=engine, autoflush=False)

session = DBSession()
