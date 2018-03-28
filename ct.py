# -*-coding:utf-8-*-
import json
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
from uuid import uuid4


class ChatHome(object):
    '''
        处理websocket 服务器与客户端交互
    '''
    chatRegister = {}

    def register(self, newer):
        '''
            保存新加入的客户端连接、监听实例，并向聊天室其他成员发送消息！
        '''
        home = str(newer.get_argument('n'))  # 获取所在聊天室
        if home in self.chatRegister:
            self.chatRegister[home].append(newer)
        else:
            self.chatRegister[home] = [newer]

        message = {
            'from': 'sys',
            'message': '%s 加入聊天室（%s）' % (str(newer.get_argument('u')), home)
        }
        self.callbackTrigger(home, message)

    def unregister(self, lefter):
        '''
            客户端关闭连接，删除聊天室内对应的客户端连接实例
        '''
        home = str(lefter.get_argument('n'))
        self.chatRegister[home].remove(lefter)
        if self.chatRegister[home]:
            message = {
                'from': 'sys',
                'message': '%s 离开聊天室（%s）' % (str(lefter.get_argument('u')), home)
            }
            self.callbackTrigger(home, message)

    def callbackNews(self, sender, message):
        '''
            处理客户端提交的消息，发送给对应聊天室内所有的客户端
        '''
        home = str(sender.get_argument('n'))
        user = str(sender.get_argument('u'))
        message = {
            'from': user,
            'message': message
        }
        self.callbackTrigger(home, message)

    def callbackTrigger(self, home, message):
        '''
            消息触发器，将最新消息返回给对应聊天室的所有成员
        '''
        for callbacker in self.chatRegister[home]:
            callbacker.write_message(json.dumps(message))


class chatBasicHandler(tornado.web.RequestHandler):
    '''
        主页， 选择进入聊天室
    '''

    def get(self, *args, **kwargs):
        session = uuid4()  # 生成随机标识码，代替用户登录
        self.render('chat/basic.html', session=session)


class homeHandler(tornado.web.RequestHandler):
    '''
        聊天室， 获取主页选择聊天室跳转的get信息渲染页面
    '''

    def get(self, *args, **kwargs):
        n = self.get_argument('n')  # 聊天室
        u = self.get_argument('u')  # 用户
        self.render('chat/home.html', n=n, u=u)


class newChatStatus(tornado.websocket.WebSocketHandler):
    '''
        websocket， 记录客户端连接，删除客户端连接，接收最新消息
    '''

    def open(self):
        n = str(self.get_argument('n'))
        self.write_message(json.dumps({'from': 'sys', 'message': '欢迎来到 聊天室（%s）' % n}))  # 向新加入用户发送首次消息
        self.application.chathome.register(self)  # 记录客户端连接

    def on_close(self):
        self.application.chathome.unregister(self)  # 删除客户端连接

    def on_message(self, message):
        self.application.chathome.callbackNews(self, message)  # 处理客户端提交的最新消息


class Application(tornado.web.Application):
    def __init__(self):
        self.chathome = ChatHome()

        handlers = [
            (r'/', chatBasicHandler),
            (r'/home/', homeHandler),
            (r'/newChatStatus/', newChatStatus),
        ]

        settings = {
            'template_path': 'html',
            'static_path': 'static'
        }

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
