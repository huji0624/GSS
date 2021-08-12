# -*- coding: utf-8 -*-

def uploadOSS(filepath):
    import oss2
    import os
    auth = oss2.Auth('LTAI4G32xPc2e75k1x2pTtUK', 'Hxt9iLdkQnkPjXTi2PuK827K6dIPiL')
    bucket = oss2.Bucket(auth, 'http://oss-ap-northeast-1-internal.aliyuncs.com', 'bnquantdata')
    result=bucket.put_object_from_file(os.path.basename(filepath), filepath)

    print('http status: {0}'.format(result.status))
    print('request_id: {0}'.format(result.request_id))
    print('ETag: {0}'.format(result.etag))
    print('date: {0}'.format(result.headers['date']))

    if result.status==200:
        print("upload file ok.delete file:"+filepath)
        os.remove(filepath)
    else:
        print("upload fail:"+filepath)

import os

files = os.listdir("tars")
for fn in files:
    fp = "/root/tars/"+fn
    uploadOSS(fp)