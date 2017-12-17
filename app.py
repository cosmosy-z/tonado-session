# Author Z

container = {} #放db的容器
import tornado.web

class Session(object):
    def __init__(self,handler):
        self.handler = handler
        self.random_str = None #默认存在一个random_str

    def generate_random_str(self):
        import hashlib
        import time
        obj = hashlib.md5()  # 调用hashlib里的md5()生成一个md5 hash对象
        obj.update(bytes(str(time.time()), encoding="utf-8"))  # 混入当下时间,更新加密
        random_str = obj.hexdigest()  # 生成一个随机值
        return random_str #返回随机值

    def __setitem__(self,key,value):
        if not self.random_str: #如果random_str依然为空，not random_str就为True，说明刚刚初始化了一个session
            random_str = self.handler.get_cookie("this_is_key") #去拿到random_str
            if not random_str:#如果randomstr为空，not_random_str就为True
                random_str = self.generate_random_str() #就生成一个random——str
                container[random_str] = {}#random——str的value为先空
            else:#如果randomstr不为空
                if random_str in container.keys():#如果randomstr在container里
                    pass
                else:#如果randomstr不在container里
                    random_str = self.generate_random_str()#就生成一个random——str
                    container[random_str] = {}#random——str的value为空
            self.random_str = random_str #random——str赋值给私有字段

        container[self.random_str][key] = value  # 掉用一次，插入一个key，value对
        self.handler.set_cookie("this_is_key",self.random_str)#将"this_is_key"和self.random_str做成键制对，放入cookie给到客户端

    def __getitem__(self,key):
        random_str = self.handler.get_cookie("this_is_key")  # 获取cookie为"this is key"的值
        if not random_str: #如果不存在
            return None#返回None

        #如果存在
        usef_info_dict = container[random_str]#那我们从服务器的container里获取下看看

        if random_str not in container.keys():#如果random_str不在container里
            return None#返回None

        # 如果random_str在container里
        value = usef_info_dict[key] #获取字典里的key
        return value #返回值


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session(self)

class IndexHandler(BaseHandler):
    def get(self):
        if self.get_argument('u',None):#如果获得了一个name为u的参数＃＃在浏览器输入127.0.0.1/8883/index?u=xxx
            self.session["k1"] = 123 #设值
            self.session["k2"] =  self.get_argument("u",None) + "parents"
            self.session["is_login"] = True
            self.write("登陆了")
        else:#如果没获得了一个name为u的参数
            self.write("请登陆")

class ManagerHandler(BaseHandler):
    def get(self):
        value = self.session["is_login"]#获取值
        if not value:
            self.redirect("/index")
        else:
            if value:#我们来看看这个字典中的key:is_login是否为True,为True的话就当它登陆了
                temp = "%s - %s" % (self.session['k1'],self.session['k2'])
                self.write(temp)#打印看看这个"k1"和'k2'的值是多少看看


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("login.html",status="")

    def post(self, *args, **kwargs):
        user = self.get_argument("user")
        pwd = self.get_argument("pwd")
        code = self.get_argument("code")
        print("Checkcode",self.session["Checkcode"])
        print(code)
        if self.session["Checkcode"] == code.upper():#把获取到的code大写化之后和seesion中的code对比
            self.write("登陆了")
        else:
            self.render("login.html",status="这个验证码不ok")


class CheckCodeHandler(BaseHandler):
    def get(self, *args, **kwargs):
        #生成图片并且返回，用write来返回
        import io
        import check_code
        mstream = io.BytesIO() #相当于在内存里创建了个临时文件
        img,code = check_code.create_validate_code() #创建图片对象，生成验证码,

        img.save(mstream,"GIF")# 将图片写入到io中，io是用来做输入和输出的
        #mstream.getvalue()相当于读到了图片里面的内容。
        self.session["Checkcode"] = code.upper() #将code大写化以后放入session，对应"Checkcode"
        self.write(mstream.getvalue())



settings = {
    "template_path":"template",
}

application= tornado.web.Application([
    (r"/index",IndexHandler),
    (r"/manage",ManagerHandler),
    (r"/login",LoginHandler),
    (r"/check_code",CheckCodeHandler)
],**settings)

if __name__ == '__main__':
    application.listen(8883)
    tornado.ioloop.IOLoop.instance().start()