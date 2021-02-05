#!/usr/bin/env python

#docs
#https://binance-docs.github.io/apidocs/spot/cn/#websocket

import asyncio
import websockets
import json
import sys
import time
import arrow
import os

subs = {
    "method": "SUBSCRIBE",
    "params":[
        "btcusdt@trade",
        "btcusdt@depth20",
        "ethusdt@trade",
        "ethusdt@depth20"
    ],"id": 1
}

if not os.path.isdir("./datas"):
    os.mkdir("./datas")
g_open_file = None

async def send_pong(websocket):
    print("Send Pong..."+str(arrow.now()))
    await websocket.pong()

def new_file():
    global g_open_file
    if g_open_file is not None:
        g_open_file.close()
    fn = arrow.utcnow().format('YYYY_MM_DD_HH_mm_ss') + ".data"
    fp = "datas/"+fn
    g_open_file = open(fp,"a")

async def recv(websocket):
    new_file()

    last_ts = 0
    last_nf = time.time()
    while True:
        res = await websocket.recv()
        res = json.loads(res)
        now = time.time()
        res['lt'] = now #localtime
        if now - last_ts > 3*60:
            last_ts = now
            await send_pong(websocket)
        g_open_file.write(json.dumps(res)+"\n")
        if now - last_nf > 60*60*6:
            last_nf = now
            new_file()

async def main():
    uri = "wss://stream.binance.com:9443/stream"
    while True:
        await asyncio.sleep(1)
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps(subs))
                await recv(websocket)
        except IOError as e:
            print(e)
        except websockets.exceptions.ConnectionClosedError as e:
            print(e)
        except websockets.exceptions.WebSocketException as e:
            print(e)
        else:
            continue

asyncio.get_event_loop().run_until_complete(main())
