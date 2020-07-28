import tornado.ioloop
import tornado.web
import time
import json
import requests
import arrow
import logging
import os
import base64
from logging.handlers import TimedRotatingFileHandler
import gs

if not os.path.isdir("./log"):
    os.mkdir("./log")

fn = str(arrow.now())
fn = fn.replace(":","_")
log_file_handler = TimedRotatingFileHandler(filename="./log/request.log", when="midnight", interval=1, backupCount=365)
log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
logger = logging.getLogger("request")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
gs.logger = logger

web_all_data = {}

class BaseHandler(tornado.web.RequestHandler):
    def _get(self):
        pass
    def get(self):
        self._get()
    def _post(self):
        pass
    def post(self):
        psd = json.loads(self.request.body)
        user_agent = self.request.headers["User-Agent"]
        ip = self.request.remote_ip 
        li = {}
        li['uuid'] = psd.get('uuid','')
        li['UA'] = user_agent
        li['ip'] = ip
        li['path'] = self.request.path
        logger.info(json.dumps(li))
        ret = self._post(psd)
        self.write(json.dumps(ret))

class IndexHandler(BaseHandler):
    def _post(self,psd):
        global web_all_data
        text = psd['t']
        ret = {}
        datas=[]
        gs.parse_sina_text(datas,text)
        if len(datas)==0:
            ret['warning'] = "请求数据有误，请重制软件"
        else:
            ret['datas'] = datas
        # ret['warning'] = "免费版目前只支持一只股票"
        newversion = '''
        新版本v1.0.5发布.<a onclick="cm.open_url(\'https://luckyhu.top/gs\');" href="#">去下载</a>或
        <a onclick="$(\'#warnalert\').remove();ret_window_height();" href="#">忽略</a>
        '''
        if psd['v']!="1.0.5":
            ret['warning'] = newversion
        # print(ret)
        gs.save_today_his(web_all_data,datas)
        gs.sort_ret(ret,psd.get('sort',''))
        return ret

class ChartHandler(BaseHandler):
    def _post(self,user_data):
        global web_all_data
        key = user_data['key']
        if key in web_all_data:
            ret = web_all_data[key]
        else:
            ret = {'quote':{'per':"0.00%",'name':key},'hist':[]}
        return ret

class UpdateHandler(BaseHandler):
    def _post(self,user_data):
        global web_all_data
        key = user_data['key']
        ret = web_all_data.get(key,{})
        ret = ret.get('his',[])
        if len(ret)>0:
            return ret[-1]
        else:
            return {"err":0}

if __name__ == "__main__":
    pid = (os.getpid())
    os.system("echo %d > pid.log" % pid)
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/chart", ChartHandler),
        (r"/update", UpdateHandler),
    ])
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()