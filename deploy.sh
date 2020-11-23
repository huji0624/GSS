ssh root@yun 'cd GSS;kill `cat pid.log`;nohup /home/huji/anaconda3/bin/python3 web.py > http.log 2>&1 &'
