yarn build
tar czvf d.tar.gz dist
scp d.tar.gz huji@yun:~/GSS/.
rm d.tar.gz
ssh huji@yun "cd GSS;rm -rf static;tar xvf d.tar.gz;mv dist static;"