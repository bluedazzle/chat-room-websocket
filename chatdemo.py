#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""
import time
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
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
    rooms = {'new': {'waiters': set()}}
    socket_room_dict = {}
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def generate_new_room(self, room):
        if room not in ChatSocketHandler.rooms:
            ChatSocketHandler.rooms[room] = {'cache': [],
                                             'waiters': set()}
        return True

    def open(self):
        ChatSocketHandler.rooms['new']['waiters'].add(self)

    def on_close(self):
        room = ChatSocketHandler.socket_room_dict[self]
        ChatSocketHandler.rooms[room]['waiters'].remove(self)

    @classmethod
    def update_cache(cls, chat, room):
        cache = cls.rooms[room]['cache']
        cache.append(chat)
        if len(cache) > cls.cache_size:
            cache = cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat, room):
        logging.info("sending message to %d waiters", len(cls.rooms[room]['waiters']))
        for waiter in cls.rooms[room]['waiters']:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def distribute_room(self, room):
        self.generate_new_room(room)
        ChatSocketHandler.rooms[room]['waiters'].add(self)
        ChatSocketHandler.socket_room_dict[self] = room
        ChatSocketHandler.rooms['new']['waiters'].remove(self)

    def on_message(self, message):
        print "got message {0}".format(message.encode('utf-8'))
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
	    "timestamp": str(time.time()),
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))
        room = parsed.get("room")
        send_type = parsed.get("type", 0)
        if send_type == 1:
            self.distribute_room(room)
        else:
            ChatSocketHandler.update_cache(chat, room)
            ChatSocketHandler.send_updates(chat, room)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
