#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

import json
import time
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import logging

logger = logging.getLogger(__name__)

from tornado.options import define, options

from models import session, User

define("port", default=8888, help="run on the given port", type=int)


class ChatCenter(object):
    '''
        处理websocket 服务器与客户端交互
    '''
    newer = 'newer'
    chatRegister = {'newer': set()}

    def register(self, newer):
        '''
            保存新加入的客户端连接、监听实例，并向聊天室其他成员发送消息！
        '''
        self.chatRegister[self.newer].add(newer)
        logger.info('INFO new socket connecting')

    def unregister(self, lefter):
        '''
            客户端关闭连接，删除聊天室内对应的客户端连接实例
        '''
        room = lefter.room_id
        self.chatRegister[room].remove(lefter)
        logger.info('INFO socket close from room {0}'.format(room))

    def callbackNews(self, sender, message):
        '''
            处理客户端提交的消息，发送给对应聊天室内所有的客户端
        '''
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            "timestamp": str(time.time()),
        }
        # chat["html"] = tornado.escape.to_basestring(
        #     self.render_string("message.html", message=chat))
        room = parsed.get("room")
        send_type = parsed.get("type", 0)
        # token = parsed.get("token", '')
        if send_type == 1:
            self.distribute_room(room, sender)
            logger.info('INFO socket enter room {0}'.format(room))
        elif send_type == 2:
            # user = session.query(User).filter(User.token == token).first()
            # if user:
            #     user.active = True
            #     session.commit()
            sender.write_message(json.dumps({'body': 'pong'}))
        else:
            self.callbackTrigger(room, chat)

    def callbackTrigger(self, home, message):
        '''
            消息触发器，将最新消息返回给对应聊天室的所有成员
        '''
        start = time.time()
        for callbacker in self.chatRegister[home]:
            try:
                callbacker.write_message(json.dumps(message))
            except Exception as e:
                logger.error("ERROR IN sending message: {0}, reason {1}".format(message, e))
        end = time.time()
        logging.info("Send message to {0} waiters, cost {1}s message: {2}".format(len(self.chatRegister[home]),
                                                                                  (end - start) * 1000.0, message))

    def generate_new_room(self, room):
        if room not in self.chatRegister:
            self.chatRegister[room] = set()
        return True

    def distribute_room(self, room, sender):
        self.generate_new_room(room)
        sender.room_id = room
        self.chatRegister[room].add(sender)
        self.chatRegister[self.newer].remove(sender)


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
        self.application.chat_center.callbackNews(self, message)  # 处理客户端提交的最新消息
        # except Exception as e:
        #     logger.error('ERROR IN new message coming, message {0}, reason {1}'.format(message, e))
        #     raise e

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
