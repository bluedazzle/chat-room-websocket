# coding: utf-8
from __future__ import unicode_literals

import redis

redis_room = None
redis_common = None

ROOM_MEMBER_KEY = 'ROOM_MEMBER_{0}'
ROOM_SONG_KEY = 'ROOM_SONG_{0}'
ROOM_STATUS_KEY = 'ROOM_STATUS_{0}'
USER_SONG_KEY = 'USER_SONG_{0}'


def init_redis_room():
    global redis_room
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    return redis_room


def init_redis_common():
    global redis_common
    redis_common = redis.StrictRedis(host='localhost', port=6379, db=4)
    return redis_common


def init_redis():
    init_redis_common()
    init_redis_room()


class RedisProxy(object):
    def __init__(self, redis, base_key, props=[]):
        self.redis = redis
        self.base_key = base_key
        self.props = props

    def encode_value(self, *args):
        value = args[0]
        for arg in args[1:]:
            value = '{0}|{1}'.format(value, arg)
        return value

    def decode_value(self, itm):
        if not itm:
            return {}
        value_list = itm.split('|')
        value_dict = {}
        for index, value in enumerate(value_list):
            value_dict[self.props[index]] = value
        return value_dict

    def remove_member_from_set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.srem(key, value)

    def get_set_count(self, key):
        key = self.base_key.format(key)
        count = self.redis.scard(key)
        return count

    def get_set_members(self, key):
        key = self.base_key.format(key)
        result = self.redis.smembers(key)
        member_list = []
        for itm in result:
            member_list.append(self.decode_value(itm))
        return member_list

    def create_update_set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.sadd(key, value)


class KVRedisProxy(RedisProxy):
    def set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.set(key, value)

    def get(self, key):
        key = self.base_key.format(key)
        result = self.redis.get(key)
        self.decode_value(result)


if __name__ == '__main__':
    init_redis()
    rmp = RedisProxy(redis_room, ROOM_MEMBER_KEY, ['fullname', 'nick', 'avatar'])
    rmp.create_update_set('test', 'test_fullname', 'test_nick', 'test_avatar')
    print rmp.get_set_members('test')
    print rmp.get_set_members('test1')

    print rmp.get_set_count('test')
    print rmp.get_set_count('test1')

    rmp.remove_member_from_set('test', 'test_fullname', 'test_nick', 'test_avatar')
    print rmp.get_set_members('test')

    rms = RedisProxy(redis_room, ROOM_SONG_KEY, ['id', 'name', 'author', 'nick'])

    rms.create_update_set('test', '123', 'test_song_name', 'test_author', 'test_nick')
    print rms.get_set_members('test')
    print rms.get_set_members('test1')

    print rms.get_set_count('test')
    print rms.get_set_count('test1')

    rms.remove_member_from_set('test', '123', 'test_song_name', 'test_author', 'test_nick')
    print rms.get_set_members('test')
