import asyncio
import tornado.tcpclient
import json

test_obj = {"action": "get_user_units", "args": {"uid": 105, "name": "Nick"}}


async def send_message(msg):
    msg = msg + "\n"
    client = tornado.tcpclient.TCPClient()
    stream = await client.connect("0.0.0.0", "48777")
    stream.write(bytes(msg, "utf-8"))
    response = await stream.read_until(b"\n")
    print(f"response = {response.decode('utf-8')}")

loop = asyncio.get_event_loop()
loop.run_until_complete(send_message(json.dumps(test_obj)))
loop.close()