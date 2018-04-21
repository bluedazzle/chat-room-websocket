# coding: utf-8
from __future__ import unicode_literals

from sqlalchemy import Column, String, DateTime, Integer, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PartyUser(Base):
    __tablename__ = 'core_party_user'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)
    token = Column(String)
    fullname = Column(String)
    nick = Column(String)
    avatar = Column(String)
    online = Column(Boolean)
    headline = Column(String)


class Room(Base):
    __tablename__ = 'core_room'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)
    name = Column(String)
    creator_nick = Column(String)
    creator_id = Column(Integer)
    cover = Column(String)


engine = create_engine('postgresql+psycopg2://rapospectre:123456qq@localhost:5432/ktv',
                       encoding='utf-8'.encode())

DBSession = sessionmaker(bind=engine)

session = DBSession()
