import gzip
import tarfile
import os
import requests

def notify_msg(msg):
    dd = "https://oapi.dingtalk.com/robot/send?access_token=7f13ddca04851c2ea19a80fd37bb2700fde430ee581524a82fe001a2e0ed8f30"
    req = {}
    req['msgtype'] = "text"
    cont = {}
    cont['content'] = msg
    req['text'] = cont
    import json
    headers = {"content-type":"application/json;charset=utf-8"}
    r = requests.post(dd,data=json.dumps(req),headers=headers)
    print(r.json())

def un_gz(file_name):
    f_name = file_name.replace(".gz", "")
    g_file = gzip.GzipFile(file_name)
    open(f_name, "w+").write(g_file.read())
    g_file.close()


def un_tar(file_name):
     tar = tarfile.open(file_name)
     names = tar.getnames()
     to_name = file_name + "_files"
     if os.path.isdir(to_name):
         pass
     else:
         os.mkdir(to_name)
     for name in names:
         tar.extract(name, to_name)
     tar.close()
     return to_name

import sys
import json
import os
import arrow

days = 4

logfiles = os.listdir("log")
# logfiles = ["request.log.2020-12-01_00-00.log","request.log.2020-07-21_00-00.log","request.log.2020-11-27_00-00.log","request.log.2020-11-23_00-00.log",]

logfiles = sorted(logfiles)
logfiles = logfiles[-days:]
logfiles.reverse()
msgs = []
msgs.append("Daily Report:")
datas = {}
uuids = set()

for tfile in logfiles:
    day_data = {}
    day = None
    with open("log/"+tfile,"r") as f:
        while True:
            l = f.readline()
            if len(l)==0:
                break
            if "INFO:" in l:
                if "uuid" in l:
                    dmap = json.loads(l.split("INFO:")[1].strip())
                    uid = dmap['uuid']
                    day = l[:10]
                    dmap['day'] = day
                    day_data[uid] = (dmap)
                    uuids.add(uid)
            
    windows_count = 0
    for uid in day_data:
        it = day_data[uid]
        if "Windows" in it['UA']:
            windows_count+=1
    
    count = len(day_data)
    windows_ratio = windows_count/count

    mstr = "  %s uv:%3d windows:%.2f%%" % (day,count,windows_ratio*100)
    next_day = arrow.get(day).shift(days=1)
    next_day = next_day.format("YYYY-MM-DD")
    
    if next_day in datas:
        nd = datas[next_day]
        stay_count = len(list(set(day_data.keys()).intersection(set(nd.keys()))))
        stay_ratio = stay_count/count
        mstr += " 活跃次留:%.2f%%" % (stay_ratio*100)
        
    msgs.append(mstr)
    datas[day] = day_data

msgs.append("%d天活跃UV:%d" % (days,len(uuids)))

msg = "\n".join(msgs)
print(msg)
# exit(1)
# notify_msg(msg)
