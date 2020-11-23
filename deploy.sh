cd ..
cp -R GSS GSS_dist
rm -rf GSS_dist/.git
tar czvf gss.tar.gz GSS_dist
rm -rf GSS_dist
scp gss.tar.gz root@yun:~/.
rm gss.tar.gz
ssh root@yun 'kill `cat GSS_dist/pid.log`;rm -rf GSS_dist;tar xvf gss.tar.gz;cd GSS_dist;nohup python3 web.py > ../http.log 2>&1 &'
