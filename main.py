#coding=utf-8

# import web
import time
import json
import requests
import arrow
import logging
import os
import base64
from logging.handlers import TimedRotatingFileHandler

class BaseRoute:
    def _POST(self,psd):
        raise Exception("_POST must implement.")

    def POST(self):
        data = web.data()
        psd = json.loads(data.decode("utf-8"))
        data = None
        if 'en' in psd:
            s = psd['en']
            s = base64.b64decode(s)
            s = urllib.request.unquote(s)
            data = json.loads(s)
            ret = self._POST(data)
            en = urllib.request.quote(ret)
            en = base64.b64encode(en)
            rd = {}
            rd['en'] = en
            return json.dumps(rd)
        else:
            data = psd
            return self._POST(data)

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

urls = (
    '/', 'index',
    '/sug', 'sug',
    '/chart', 'chart',
    '/update', 'update'
)

class update(BaseRoute):
    def _POST(self,user_data):
        key = user_data['key']
        ret = web.all_data.get(key,{})
        ret = ret.get('his',[])
        if len(ret)>0:
            return json.dumps(ret[-1])
        else:
            return json.dumps({"err":0})

class chart(BaseRoute):
    def _POST(self,user_data):
        key = user_data['key']
        if key in web.all_data:
            ret = web.all_data[key]
        else:
            ret = {'quote':{'per':"0.00%",'name':key},'hist':[]}
        return json.dumps(ret)

class sug:
    def GET(self):
        user_data = web.input()
        key = user_data.key
        if key.endswith("?"):
            key = key[:-1]
        if key.strip().startswith("@"):
            return {"message":"no input"}
        id,m = id_market_from_key(key)
        if m == "a" or m=="hk":
            logger.info("get sug : " + id)
            sina_key = id
            now = int(1000*time.time())
            url = "https://suggest3.sinajs.cn/suggest/type=&key=%s&name=suggestdata_%d" % (sina_key,now)
            ret = requests.get(url)
            sina_sug = parse_sina_sug(m,ret.text)
            ret_sug = {}
            ret_sug['value'] = sina_sug
            return json.dumps(ret_sug)
        else:
            return json.dumps({"err":"not support.."+key})

class index(BaseRoute):
    def _POST(self,psd):
        # data = web.data()
        # psd = json.loads(data.decode("utf-8"))
        li = {}
        li['uuid'] = psd['uuid']
        li['UA'] = web.ctx.env['HTTP_USER_AGENT']
        li['ip'] = web.ctx.ip
        import json
        logger.info(json.dumps(li))
        text = psd['t']
        ret = {}
        datas=[]
        parse_sina_text(datas,text)
        ret['datas'] = datas
        # ret['warning'] = "免费版目前只支持一只股票"
        newversion = '''
        新版本v1.1.1发布.<a onclick="cm.open_url(\'https://luckyhu.top/gs\');" href="#">去下载</a>或
        <a onclick="$(\'#warnalert\').remove();ret_window_height();" href="#">忽略</a>
        '''
        if psd['v']!="1.1.1":
            ret['warning'] = newversion
        # print(ret)
        save_today_his(datas)
        sort_ret(ret,psd.get('sort',''))
        return json.dumps(ret)



if __name__ == "__main__":
    pid = (os.getpid())
    os.system("echo %d > pid.log" % pid)
    # web.all_data = {}
    # app = web.application(urls, globals())
    # app.run()
