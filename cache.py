# coding: utf-8
from __future__ import unicode_literals

import redis
import time

from const import RoomStatus

redis_room = None
redis_common = None

ROOM_MEMBER_KEY = 'ROOM_MEMBER_{0}'
ROOM_SONG_KEY = 'ROOM_SONG_{0}'
ROOM_STATUS_KEY = 'ROOM_STATUS_{0}'
USER_SONG_KEY = 'USER_SONG_{0}'

TIME_REST = 30
TIME_ASK = 15
TIME_UNLIMIT = 3600 * 24


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
    def __init__(self, redis, base_key, pk=None, props=[]):
        self.redis = redis
        self.base_key = base_key
        self.props = props
        self.pk = pk

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
        print value_list, self.props
        for index, value in enumerate(value_list):
            value_dict[self.props[index]] = value
        return value_dict

    def remove_member_from_set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        res = self.redis.srem(key, value)
        return res

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

    def exist(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        return self.redis.sismember(key, value)

    def search(self, key, pk):
        if not self.pk:
            return False, None
        mem_list = self.get_set_members(key)
        for itm in mem_list:
            itm = self.decode_value(itm)
            if itm.get(self.pk) == pk:
                return True, itm
        return False, None

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


class ListRedisProxy(RedisProxy):
    def pop(self, key):
        key = self.base_key.format(key)
        # value = self.encode_value(*args)
        res = self.redis.lpop(key)
        value = self.decode_value(res)
        return value

    def get(self, key, index=0, decode=True):
        key = self.base_key(key)
        res = self.redis.lindex(key, index)
        if decode:
            value = self.decode_value(res)
            return value
        return res

    def remove(self, key, index):
        if index < 0:
            return
        value = self.get(key, index, False)
        key = self.base_key.format(key)
        self.redis.lrem(key, 0, value)

    def get_count(self, key):
        key = self.base_key.format(key)
        count = self.redis.llen(key)
        return count

    def get_members(self, key):
        key = self.base_key.format(key)
        result = self.redis.lrange(key, 0, -1)
        member_list = []
        for itm in result:
            member_list.append(self.decode_value(itm))
        return member_list

    def search(self, key, pk, *args):
        key = self.base_key.format(key)
        value = None
        if not self.pk:
            value = self.encode_value(*args)
        result = self.redis.lrange(key, 0, -1)
        for index, itm in enumerate(result):
            if self.pk:
                itm = self.decode_value(itm)
                if itm.get(self.pk) == pk:
                    return index
            else:
                if itm == value:
                    return index
        return -1

    def push(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.rpush(key, value)


class HashRedisProxy(RedisProxy):
    # def __init__(self):
    # status: 1 演唱中 2 上麦询问中 3 间隔休息中 4 无限期休息中
    status = {'status': RoomStatus.singing, "start_time": 0, "end_time": 0, "current_time": 0, "duration": 0}
    reset_song = {'sid': 0, 'name': '', 'author': '', 'nick': '', 'fullname': ''}

    def generate_time_tuple(self, duration):
        time_tuple = {}
        start_time = int(time.time())
        time_tuple['start_time'] = start_time
        time_tuple['end_time'] = start_time + duration
        time_tuple['current_time'] = start_time
        return time_tuple

    def set_song(self, key, song):
        """
        song {'sid', 'name', 'author', 'nick', 'fullname'}
        """
        duration = song.get("duration", 0)
        time_dict = self.generate_time_tuple(duration)
        self.status.update(time_dict)
        self.status.update(song)
        self.set(key, **self.status)
        return self.status

    def set_rest(self, key, new=False):
        status = RoomStatus.rest
        time_dict = self.generate_time_tuple(TIME_REST)
        if new:
            time_dict = self.generate_time_tuple(TIME_UNLIMIT)
            status = RoomStatus.free
        self.status.update(time_dict)
        self.status.update(self.reset_song)
        self.status['status'] = status
        self.status['duration'] = TIME_UNLIMIT if new else TIME_REST
        self.set(key, **self.status)
        return self.status

    def set_ask(self, key, fullname, name):
        time_dict = self.generate_time_tuple(TIME_ASK)
        self.status.update(time_dict)
        self.status.update(self.reset_song)
        self.status['fullname'] = fullname
        self.status['name'] = name
        self.status['status'] = RoomStatus.ask
        self.status['duration'] = TIME_ASK
        self.set(key, **self.status)
        return self.status

    def set(self, key, **kwargs):
        key = self.base_key.format(key)
        self.redis.hmset(key, kwargs)

    def get(self, key):
        now = int(time.time())
        key = self.base_key.format(key)
        result = self.redis.hgetall(key)
        result['current_time'] = now
        return result


if __name__ == '__main__':
    init_redis()
    rmp = RedisProxy(redis_room, ROOM_MEMBER_KEY, ['fullname', 'nick', 'avatar'])
    rmp.create_update_set('test', 'test_fullname', 'test_nick', 'test_avatar')
    print rmp.exist('test', 'test_fullname', 'test_nick1', 'test_avatar')
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

    print rms.remove_member_from_set('test', '123', 'test_song_name', 'test_author', 'test_nick')
    print rms.get_set_members('test')
    print '==================test list ======================='
    lmp = ListRedisProxy(redis_room, ROOM_SONG_KEY, ['id', 'name', 'author', 'nick'])
    lmp.push('test2', '1', 'test_name', 'test_author', 'test_nick')
    print lmp.get_count('test2')
    lmp.push('test2', '2', 'test_name', 'test_author', 'test_nick')
    print lmp.pop('test2')
    print lmp.search('test2', '2', 'test_name', 'test_author', 'test_nick')
    print lmp.get_members('test2')

    print '==================test room status ======================='
    hrp = HashRedisProxy(redis_room, ROOM_STATUS_KEY)
    print hrp.set_song('test', {'sid': 1, 'name': 'test_name', 'author': 'test_author', 'nick': 'test_nick',
                                'fullname': 'test_fullname', 'duration': 100})
    print hrp.get('test')
    print hrp.set_rest('test')
    print hrp.get('test')
    print hrp.set_ask('test', 'test_fullname1')
    print hrp.get('test')
    time.sleep(2)
    print hrp.get('test')
    print hrp.set_rest('test', True)