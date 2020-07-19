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

day_data = {}

import sys
import json
tfile = sys.argv[1]
with open(tfile,"r") as f:
    t = f.read()
    lines = t.split("\n")
    for l in lines:
        if "INFO:" in l:
            if "uuid" in l:
                dmap = json.loads(l.split("INFO:")[1].strip())
                uid = dmap['uuid']
                day = l[:10]
                dd = day_data.get(day,{})
                uid_v_count = dd.get(uid,0)
                dd[uid] = uid_v_count+1
                day_data[day] = dd

keys = day_data.keys()
keys.sort()
last_dd = None
msgs = []
for k in keys:
    if "-" not in k:
        continue
    dd = day_data[k]
    print(k + " : " + str(len(dd)))
    visit_total = 0
    last_day_user_cnt = 0.0
    one_visit = 0
    for d in dd:
        vt = dd[d]
        visit_total += vt
        is_last_day_user = False
        if vt==1:
            one_visit += 1
        if last_dd is not None and d in last_dd:
            is_last_day_user = True
            last_day_user_cnt += 1
        msgs.append("  "+ d + " : "+str(vt)+"v "+str(vt*10/60)+"min - is_last_day_user: "+str(is_last_day_user))
    msgs.append("  total visit : "+str(visit_total))
    msgs.append("  av visit : "+str(visit_total/len(dd)))
    msgs.append("  one visit count : "+str(one_visit)+" valide user : "+str(len(dd)-one_visit))
    if last_dd is not None:
        msgs.append("  ratio of last day user %f" % (last_day_user_cnt/len(last_dd)))
    last_dd = dd

notify_msg("\n".join(msgs))
