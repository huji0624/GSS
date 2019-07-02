#coding=utf-8

import web
import time
import json
import requests
import arrow
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.DEBUG)

urls = (
    '/', 'index',
    '/sug', 'sug',
    '/chart', 'chart',
    '/update', 'update'
)

def id_market_from_key(key):
    pair = key.split("@")
    id = pair[0]
    m = pair[1]
    return id,m

def get_one_from(m,one,it):
    ret = {}
    ret['key'] = one

    ret['name'] = it['name']
    ret['code'] = it['code']

    if it['price']<1 or m=="fx":
        ret['price'] = "%.4f" % (it['price'])
    else:
        ret['price'] = "%.2f" % (it['price'])
    ret['price_v'] = it['price']

    if it['pre_close']<1 or m=="fx":
        ret['pre_close'] = "%.4f" % (it['pre_close'])
    else:
        ret['pre_close'] = "%.2f" % (it['pre_close'])
    ret['pre_close_v'] = it['pre_close']

    if it['open']<1 or m=="fx":
        ret['open'] = "%.4f" % (it['open'])
    else:
        ret['open'] = "%.2f" % (it['open'])
    ret['open_v'] = it['open']

    if 'volume' in it:
        vol = float(it['volume'])/10000
        if vol<10000:
            vol = "%.1f万" % (vol)
        else:
            vol = "%.1f亿" % (vol/10000)
        ret['volume'] = vol
        ret['volume_v'] = float(it['volume'])
    else:
        ret['volume_v'] = 0

    if "amount" in it:
        amt = float(it['amount'])/10000
        if amt<10000:
            amt = "%.1f万" % (amt)
        else:
            amt = "%.1f亿" % (amt/10000)
        ret['amount'] = amt
        ret['amount_v'] = float(it['amount'])
    else:
        ret['amount_v'] = 0

    prc = float(ret['price'])
    pcl = float(it['pre_close'])
    per_v = (prc-pcl)/pcl*100
    ret['per'] = "%.2f%%" % (per_v)
    ret['per_v'] = per_v
    return ret

def parse_sina_sug(m,text):
    sugs = []
    text = text.split('="')[1]
    text = text.split('";')[0].strip()
    if text == "":
        return sugs
    lines = text.split(";")
    for line in lines:
        tokens = line.split(',')
        mkt = tokens[1]
        code = tokens[2].strip()#600335
        mcode = tokens[3]#sh600335
        name = tokens[4].strip()
        if m=="a" and mkt=="11":
            sug = {}
            sug['code'] = code
            sug['name'] = name
            if mcode in ["sh000001","sz399001"]:
                sug['key'] = mcode[:2]+"@a"
            elif mcode == "sz399006":
                sug['key'] = "cyb@a"
            else:
                sug['key'] = code+"@a"
            sugs.append(sug)
        elif m=="hk" and mkt=="31":
            sug = {}
            sug['code'] = code
            sug['name'] = name
            sug['key'] = code+"@hk"
            sugs.append(sug)
        else:
            logging.warning("code not right..."+line)
    return sugs

class update:
    def POST(self):
        data = web.data()
        user_data = json.loads(data.decode("utf-8"))
        key = user_data['key']
        ret = web.all_data.get(key,{})
        ret = ret.get('his',[])
        if len(ret)>0:
            return json.dumps(ret[-1])
        else:
            return json.dumps({"err":0})

def test_chart_data():
    import random
    his = []
    the_time = arrow.now().timestamp
    for i in range(500):
        his.append({"time":the_time+i*10,"price":random.random()-0.5})
    for i in range(500):
        his.append({"time":the_time+i*10+60*60*4,"price":random.random()-0.5})
    return {"his":his,"quote":{"per":"5.55%","name":"KOKO"}}

class chart:
    def POST(self):
        data = web.data()
        user_data = json.loads(data.decode("utf-8"))
        key = user_data['key']
        # if key == "sh600336@a":
        #     return json.dumps(test_chart_data())
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
            logging.info("get sug : " + id)
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

def parse_hk(l):
    left = l.split('hq_str_rt_hk')[1].split("=")
    code = left[0]
    left = left[1].split(",")
    vol = left[12]
    amt = left[11]
    prc = left[6]
    op = left[2]
    pc = left[3]
    name = left[1]
    key = code+"@hk"
    stock = {}
    stock['code'] = code
    stock['volume'] = vol
    stock['amount'] = amt
    stock['price'] = float(prc)
    stock['open'] = float(op)
    stock['pre_close'] = float(pc)
    stock['name'] = name
    stock['key'] = key
    stock['mkt'] = "hk"
    return get_one_from('hk',key,stock)

def parse_sina_a(l):
    left = l.split('hq_str_')[1].split("=\"")
    if left[0]=="?":
        return None
    code = left[0]
    left = left[1].split(",")
    vol = left[8]
    amt = left[9]
    prc = left[3]
    op = left[1]
    pc = left[2]
    if prc=="0.000":
        prc = pc
    name = left[0]
    key = code+"@a"
    stock = {}
    stock['code'] = code
    stock['volume'] = vol
    stock['amount'] = amt
    stock['price'] = float(prc)
    stock['open'] = float(op)
    stock['pre_close'] = float(pc)
    stock['name'] = name
    stock['key'] = key
    stock['mkt'] = "a"
    return get_one_from('a',key,stock)

#var hq_str_fx_susdcny="23:29:00,6.8671,6.8668,6.8771,257,6.8749,6.8817,6.856,6.8668,在岸人民币,-0.18,-0.0121,0.003738,Cougar Capital Management. New York,6.9762,6.5979,*+-++--+,2019-06-28";
def parse_fx(l):
    left = l.split("hq_str_fx_s")[1].strip().split("=\"")
    code = left[0]
    left = left[1].split(",")
    name = left[9]
    op = left[5]
    pc = left[3]
    prc = left[2]
    high = left[6]
    low = left[7]
    key = code+"@fc"
    stock = {}
    stock['code'] = code
    stock['price'] = float(prc)
    stock['open'] = float(op)
    stock['pre_close'] = float(pc)
    stock['name'] = name
    stock['key'] = key
    stock['mkt'] = "fx"
    return get_one_from('fx',key,stock)

#var hq_str_btc_btcbtcusd="01:10:34,0.0000,0.0000,11906.7000,0,11906.7000,12174.3000,10970.5000,11897.3000,比特币美元(BTC/USD),1260000.0000,2019-06-29";
def parse_cc(l):
    left = l.split("hq_str_btc_")[1].strip().split("=\"")
    code = left[0]
    left = left[1].split(",")
    # print(left)
    name = left[9]
    op = left[5]
    pc = left[3]
    prc = left[8]
    high = left[6]
    low = left[7]
    vol = left[10]
    # amt = left[9]
    key = code+"@fc"
    stock = {}
    stock['volume'] = vol
    # stock['amount'] = amt
    stock['code'] = code
    stock['price'] = float(prc)
    stock['open'] = float(op)
    stock['pre_close'] = float(pc)
    stock['name'] = name
    stock['key'] = key
    stock['mkt'] = "cc"
    return get_one_from('cc',key,stock)

def parse_sina_text(datas,text):
    lines = text.split("\n")
    # logging.info(lines)
    for l in lines:
        if len(l.strip())==0:
            continue
        d = None
        if "hq_str_rt_hk" in l:
            d = parse_hk(l)
        elif "hq_str_fx_s" in l:
            d = parse_fx(l)
        elif "hq_str_btc" in l:
            d = parse_cc(l)
        else:
            d = parse_sina_a(l)
        if d is not None:
            datas.append(d)

def save_key_if_new(now,k,d):
    rc = web.all_data.get(k, {})
    if (now - rc.get('last', 0)) > 10:
        rc['last'] = now
        his = rc.get('his', [])
        his.append(d)
        rc['his'] = his
        rc['quote'] = d
    web.all_data[k] = rc

def save_key_and_pop_old(now,k,d):
    rc = web.all_data.get(k, {})
    if (now - rc.get('last', 0)) > 10:
        rc['last'] = now
        his = rc.get('his', [])
        his.append(d)
        if (d['time']-his[0]['time'])>24*60*60:
            his.pop(0)
        rc['his'] = his
        rc['quote'] = d
        web.all_data[k] = rc

def between_day_time(an,h1,m1,h2,m2):
    # print("is %s between %d:%d - %d:%d" % (str(an),h1,m1,h2,m2))
    h = an.hour
    m = an.minute
    if h<h1 or h>h2:
        return False
    elif h==h2 and m>m2:
        return False
    elif h==h1 and m<m1:
        return False
    return True

def save_today_his(datas):
    an = arrow.now()
    now = an.timestamp
    for d in datas:
        d['time'] = now
        k = d['key']
        id, m = id_market_from_key(k)
        if m=="a":
            is_a_clean_time = between_day_time(an, 9, 25, 9, 29)
            is_a_open = between_day_time(an, 9, 30, 11, 30) or between_day_time(an, 13, 0, 15, 0)
            if is_a_clean_time and k in web.all_data:
                del web.all_data[k]
            elif is_a_open:
                save_key_if_new(now,k,d)
        elif m=="hk":
            is_clean_time = between_day_time(an, 9, 25, 9, 29)
            is_open = between_day_time(an,9,30,12,0) or between_day_time(an,13,0,16,0)
            if is_clean_time and k in web.all_data:
                del web.all_data[k]
            elif is_open:
                save_key_if_new(now, k, d)
        else:
            save_key_and_pop_old(now,k,d)

def sort_ret(ret,sort):
    if sort!="":
        tks = sort.split("#")
        dts = ret['datas']
        k = tks[0] + "_v"
        od = tks[1]
        s_dts = sorted(dts,key=lambda x:x[k],reverse=(od=="desc"))
        ret['datas'] = s_dts
    ret['sort'] = sort

class index:
    def POST(self):
        data = web.data()
        psd = json.loads(data.decode("utf-8"))
        #logging.info("post:"+str(psd))
        logging.info("uuid:"+psd['uuid'])
        logging.info(web.ctx.env['HTTP_USER_AGENT'])
        text = psd['t']
        ret = {}
        datas=[]
        parse_sina_text(datas,text)
        ret['datas'] = datas
        # ret['warning'] = "免费版目前只支持一只股票"
        newversion = '''
        新版本v1.0.1发布.<a onclick="cm.open_url(\'https://luckyhu.top/gs\');" href="#">去下载</a>或
        <a onclick="$(\'#warnalert\').remove();ret_window_height();" href="#">忽略</a>
        '''
	if psd['v']!="1.0.1":
            ret['warning'] = newversion
        # print(ret)
        save_today_his(datas)
        sort_ret(ret,psd.get('sort',''))
        return json.dumps(ret)

if __name__ == "__main__":
    web.all_data = {}
    app = web.application(urls, globals())
    app.run()