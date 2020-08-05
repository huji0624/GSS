#coding=utf-8
import arrow

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

    if "ltg" in it:
        ltg_v = float(it['ltg'])*100
        if ltg_v>0:
            ltg = ret['volume_v']/ltg_v
            ret['swap'] = "%.2f%%" % (ltg)
            ret['swap_v'] = ltg
        else:
            ret['swap_v'] = 0
    else:
        ret['swap_v'] = 0

    if "ba0" in it:
        ba = float(it['ba0'])+float(it['ba1'])+float(it['ba2'])+float(it['ba3'])+float(it['ba4'])
        sa = float(it['sa0'])+float(it['sa1'])+float(it['sa2'])+float(it['sa3'])+float(it['sa4'])
        abr_v = (ba-sa)/(ba+sa)
        ret['abr_v'] = abr_v
        ret['abr'] = "%.2f%%" % (abr_v*100)
    else:
        ret['abr_v'] = 0

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
            logger.warning("code not right..."+line)
    return sugs

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

def parse_sina_a(l,base_info):
    stock = {}
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
    ba0 = left[10]
    if ba0=="0":
        pass
    else:
        stock['ba0'] = left[10]
        stock['bp0'] = left[11]
        stock['ba1'] = left[12]
        stock['bp1'] = left[13]
        stock['ba2'] = left[14]
        stock['bp2'] = left[15]
        stock['ba3'] = left[16]
        stock['bp3'] = left[17]
        stock['ba4'] = left[18]
        stock['bp4'] = left[19]
        stock['sa0'] = left[20]
        stock['sp0'] = left[21]
        stock['sa1'] = left[22]
        stock['sp1'] = left[23]
        stock['sa2'] = left[24]
        stock['sp2'] = left[25]
        stock['sa3'] = left[26]
        stock['sp3'] = left[27]
        stock['sa4'] = left[28]
        stock['sp4'] = left[29]
    if prc=="0.000":
        prc = pc
    name = left[0]
    key = code+"@a"
    stock['code'] = code
    stock['volume'] = vol
    stock['amount'] = amt
    stock['price'] = float(prc)
    stock['open'] = float(op)
    stock['pre_close'] = float(pc)
    stock['name'] = name
    stock['key'] = key
    stock['mkt'] = "a"
    if code==base_info.get('code',code):
        stock.update(base_info)
    else:
        logger.error("wrong code:"+code)

    return get_one_from('a',key,stock)

#var hq_str_fx_susdcny="23:29:00,6.8671,6.8668,6.8771,257,6.8749,6.8817,6.856,6.8668,在岸人民币,-0.18,-0.0121,0.003738,Cougar Capital Management. New York,6.9762,6.5979,*+-++--+,2019-06-28";
def parse_fx(l):
    left = l.split("hq_str_fx_s")[1].strip().split("=\"")
    if len(left)<2:
        logger.error("wrong text :"+l)
        return None
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

def parse_sina_a_i(l):
    base_info = {}
    l = l.split("hq_str_")[1]
    tks = l.split("_i=\"")
    code = tks[0].strip()
    l = tks[1]
    tks = l[:-2].split(",")
    ltg = tks[8].strip()
    if ltg!="":
        base_info['ltg']=ltg
    base_info['code']=code
    return base_info

def parse_sina_nf(l):
    obj = {}
    l = l.split("hq_str_nf_")[1]
    tks = l.split("=\"")
    code = tks[0].strip()
    key = code.lower() + "@nf"
    l = tks[1].strip()
    tks = l.split(",")
    obj['name'] = tks[0]
    obj['code'] = code
    obj['key'] = key
    obj['open'] = float(tks[2])
    obj['high'] = float(tks[3])
    obj['low'] = float(tks[4])
    #[5]jie suan jia
    obj['price'] = float(tks[8])
    obj['bp0'] = tks[6]
    obj['sp0'] = tks[7]
    obj['pre_close'] = float(tks[10])
    obj['volume'] = tks[14]
    return get_one_from('nf', key, obj)

#var hq_str_of180031="银华中小盘混合,3.49,5.27,3.457,0.95,2020-07-20";
#var hq_str_fu_180031="银华中小盘混合,10:50:00,3.4423,3.4070,5.1870,0.2329,1.0361,2020-07-28";
def parse_sina_of(l):
    obj = {}
    l = l.split("hq_str_of")[1]
    tks = l.split("=\"")
    code = tks[0].strip()
    key = code + "@of"
    l = tks[1].strip()
    tks = l.split(",")
    if len(tks)<4:
        logger.error("wrong text :"+l)
        return None
    obj['name'] = tks[0]
    obj['code'] = code
    obj['key'] = key
    obj['open'] = float(tks[3])
    # obj['high'] = float(tks[3])
    # obj['low'] = float(tks[4])
    #[5]jie suan jia
    obj['price'] = float(tks[1])
    # obj['bp0'] = tks[6]
    # obj['sp0'] = tks[7]
    obj['pre_close'] = float(tks[3])
    # obj['volume'] = tks[14]
    return get_one_from('of', key, obj)

#var hq_str_fu_180031="银华中小盘混合,10:50:00,3.4423,3.4070,5.1870,0.2329,1.0361,2020-07-28";
def parse_sina_fu(l):
    obj = {}
    l = l.split("hq_str_fu_")[1]
    tks = l.split("=\"")
    code = tks[0].strip()
    key = code + "@of"
    l = tks[1].strip()
    tks = l.split(",")
    if len(tks)<3:
        logger.error("wrong text :"+l)
        return None
    obj['name'] = tks[0]+"(估价)"
    obj['code'] = code
    obj['key'] = key
    obj['open'] = float(tks[3])
    obj['price'] = float(tks[2])
    obj['pre_close'] = float(tks[3])
    # obj['volume'] = tks[14]
    return get_one_from('of', key, obj)

def parse_sina_text(datas,text):
    print("sina text:")
    print(text)
    lines = text.split("\n")
    base_info = {}
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
        elif "hq_str_nf" in l:
            d = parse_sina_nf(l)
        elif "hq_str_of" in l:
            d = parse_sina_of(l)
            if d is None:
                pass
            elif len(datas)>0 and datas[-1]['code']==d['code']:
                d = None
        elif "hq_str_fu" in l:
            d = parse_sina_fu(l)
        elif "hq_str_sys_auth" in l:
            logger.error("parse_sina_text fail:"+l)
        else:
            if "_i=" in l:
                base_info = parse_sina_a_i(l)
            else:
                d = parse_sina_a(l, base_info)
        if d is not None:
            datas.append(d)

def save_key_and_pop_old(web_all_data,now,k,d):
    rc = web_all_data.get(k, {})
    if (now - rc.get('last', 0)) > 15:
        rc['last'] = now
        his = rc.get('his', [])
        his.append(d)
        if (d['time']-his[0]['time'])>24*60*60:
            his.pop(0)
        rc['his'] = his
        rc['quote'] = d
        rc['hot'] = rc.get('hot',0) + 1
        web_all_data[k] = rc
    if (now - rc.get('last', 0)) > 100:
        rc['hot'] = rc.get('hot',0)/2

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

def save_today_his(all_data,datas):
    an = arrow.now()
    now = an.timestamp
    for d in datas:
        d['time'] = now
        k = d['key']
        id, m = id_market_from_key(k)
        if m=="a":
            is_a_open = between_day_time(an, 9, 30, 11, 30) or between_day_time(an, 13, 0, 15, 0)
            if is_a_open:
                save_key_and_pop_old(all_data,now,k,d)
        elif m=="hk":
            is_open = between_day_time(an,9,30,12,0) or between_day_time(an,13,0,16,0)
            if is_open:
                save_key_and_pop_old(all_data,now, k, d)
        elif m=="nf":
            is_open = between_day_time(an,9,00,11,30) or between_day_time(an,13,30,15,0) or between_day_time(an,21,00,23,30)
            if is_open:
                save_key_and_pop_old(all_data,now, k, d)
        else:
            save_key_and_pop_old(all_data,now,k,d)

def sort_ret(ret,sort):
    if sort!="":
        tks = sort.split("#")
        dts = ret['datas']
        k = tks[0] + "_v"
        od = tks[1]
        s_dts = sorted(dts,key=lambda x:x[k],reverse=(od=="desc"))
        ret['datas'] = s_dts
    ret['sort'] = sort
