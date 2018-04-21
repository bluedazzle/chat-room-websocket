#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

import json
import time

import redis
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import logging

from cache import init_redis, redis_room, ROOM_STATUS_KEY, RedisProxy, ROOM_MEMBER_KEY, ROOM_SONG_KEY, KVRedisProxy, \
    USER_SONG_KEY
from message import WsMessage

logger = logging.getLogger(__name__)

from tornado.options import define, options

from db import session, Room, PartyUser

define("port", default=8888, help="run on the given port", type=int)


class ChatCenter(object):
    '''
        处理websocket 服务器与客户端交互
    '''
    newer = 'newer'
    chat_register = {'newer': set()}
    members = None
    songs = None
    user = None
    user_song = None

    def __init__(self):
        self.members = RedisProxy(redis_room, ROOM_MEMBER_KEY, ['fullname', 'nick', 'avatar'])
        self.songs = RedisProxy(redis_room, ROOM_SONG_KEY, ['sid', 'name', 'author', 'nick', 'fullname'])
        self.user_song = KVRedisProxy(redis_room, USER_SONG_KEY, ['sid', 'name', 'author'])

    def parameter_wrapper(self, message):
        parsed = tornado.escape.json_decode(message)
        msg = WsMessage(parsed)
        for k, v in parsed:
            setattr(msg, k, v)
        return msg

    def response_wrapper(self, message):
        chat = {
            "id": str(uuid.uuid4()),
            "body": message.body,
            "timestamp": str(time.time()),
        }
        return chat

    def register(self, newer):
        '''
            保存新加入的客户端连接、监听实例，并向聊天室其他成员发送消息！
        '''
        self.chat_register[self.newer].add(newer)
        logger.info('INFO new socket connecting')

    def unregister(self, lefter):
        '''
            客户端关闭连接，删除聊天室内对应的客户端连接实例
        '''
        room = lefter.room_id
        self.chat_register[room].remove(lefter)
        self.members.remove_member_from_set(room, self.user.fullname, self.user.nick, self.user.avatar)
        song = self.user_song.get(self.user.fullname)
        self.songs.remove_member_from_set(room, song.get('sid'), song.get('name'), song.get('author'), self.user.nick,
                                          self.user.fullname)
        logger.info('INFO socket close from room {0}'.format(room))

    def callback_news(self, sender, message):
        '''
            处理客户端提交的消息
            message : {
                "action": "xx", # 路由
                "body": "xx", # 内容
            }
        '''
        message = self.parameter_wrapper(message)
        urls = {'join': self.distribute_room,
                'status': self.room_info,
                'boardcast': self.boardcast_in_room}
        view_func = urls.get(message.action, self.boardcast_in_room)
        view_func(sender, message)

        # room = parsed.get("room")
        # send_type = parsed.get("type", 0)
        # token = parsed.get("token", '')
        # if send_type == 1:
        #     self.distribute_room(room, sender)
        #     logger.info('INFO socket enter room {0}'.format(room))
        # elif send_type == 2:
        #     user = session.query(User).filter(User.token == token).first()
        #     if user:
        #         user.active = True
        #         session.commit()
        # sender.write_message(json.dumps({'body': 'pong'}))
        # else:
        #     self.callback_trigger(room, chat)

    # 路由 房间信息
    def room_info(self, sender, message):
        key = ROOM_STATUS_KEY.format(message.room)
        result = redis_room.hgetall(key)
        out_dict = {'room': message.room}
        room = session.query(Room).filter(Room.room_id == message.room).first()
        if room:
            out_dict['name'] = room.name
            out_dict['cover'] = room.cover
        # todo 房间人数
        out_dict['count'] = self.members.get_set_count(message.room)
        out_dict['members'] = self.members.get_set_members(message.room)
        out_dict['songs'] = self.songs.get_set_members(message.room)
        for k, v in result.items():
            out_dict[k] = json.loads(v)
        sender.write_message(self.response_wrapper(message))

    # 路由 广播
    def boardcast_in_room(self, sender, message):
        self.callback_trigger(message.room, self.response_wrapper(message))

    def callback_trigger(self, home, message):
        '''
            消息触发器，将最新消息返回给对应聊天室的所有成员
        '''
        start = time.time()
        for callbacker in self.chat_register[home]:
            try:
                callbacker.write_message(json.dumps(message))
            except Exception as e:
                logger.error("ERROR IN sending message: {0}, reason {1}".format(message, e))
        end = time.time()
        logging.info("Send message to {0} waiters, cost {1}s message: {2}".format(len(self.chat_register[home]),
                                                                                  (end - start) * 1000.0, message))

    def generate_new_room(self, room):
        if room not in self.chat_register:
            self.chat_register[room] = set()
        return True

    def distribute_room(self, sender, message):
        self.generate_new_room(message.room)
        sender.room_id = message.room
        sender.token = message.token
        user = session.query(PartyUser).filter(PartyUser.token == message.token).first()
        if user:
            sender.user = user
            self.chat_register[message.room].add(sender)
            self.chat_register[self.newer].remove(sender)
            self.members.create_update_set(message.room, user.fullname, user.nick, user.avatar)


class Application(tornado.web.Application):
    def __init__(self):
        self.chat_center = ChatCenter()

        handlers = [
            (r"/index", RoomHandler),
            (r"/room", MainHandler),
            (r"/", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class RoomHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render("room.html")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        room = self.get_argument("room", None)
        if room:
            self.render("index.html", messages=[], room=room)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        self.room_id = None
        self.token = None
        super(ChatSocketHandler, self).__init__(application, request, **kwargs)

    def open(self):
        # try:
        self.application.chat_center.register(self)  # 记录客户端连接
        # except Exception as e:
        #     logger.error('ERROR IN init web socket , reason {0}'.format(e))
        #     raise e

    def on_close(self):
        try:
            self.application.chat_center.unregister(self)  # 删除客户端连接
        except Exception as e:
            logger.error('ERROR IN close web socket, reason {0}'.format(e))
            raise e

    def on_message(self, message):
        # try:
        self.application.chat_center.callback_news(self, message)  # 处理客户端提交的最新消息
        # except Exception as e:
        #     logger.error('ERROR IN new message coming, message {0}, reason {1}'.format(message, e))
        #     raise e

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}


def main():
    init_redis()
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
