# coding: utf-8
# from __future__ import unicode_literals


class ChoiceBase(object):
    __choices__ = ()

    def get_choices(self):
        return self.__choices__

    @classmethod
    def get_display_name(cls, value):
        _names = dict(cls.__choices__)
        return _names.get(value) or ""

    @classmethod
    def all_elements(cls):
        _dict = dict(cls.__choices__)
        return _dict.keys()


class RoomStatus(ChoiceBase):
    singing = '1'
    ask = '2'
    rest = '3'
    free = '4'

    __choices__ = (
        (singing, u'演唱中'),
        (ask, u'上麦询问中'),
        (rest, u'间隔休息中'),
        (free, u'空闲'),
    )
