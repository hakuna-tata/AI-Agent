import base64
import hashlib
import hmac
import json
from urllib.parse import urlencode
import time
import websocket
import threading

class IATClient:
    def __init__(self, appid, api_key, api_secret):
        self.APPID = appid
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.URL = 'wss://ws-api.xfyun.cn/v2/iat'
    
    def create_url(self):
        now = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + now + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"

        signature_sha = hmac.new(
            self.API_SECRET.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": now,
            "host": "ws-api.xfyun.cn"
        }
        url = self.URL + '?' + urlencode(v)

        return url

    def on_open(self, ws, audio_file):
        def run(*args):
            param = {
                "common": {"app_id": self.APPID},
                "business": {"language": "zh_cn", "domain": "iat", "accent": "mandarin"},
                "data": {
                    "status": 0,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": ""
                }
            }
            ws.send(json.dumps(param))
            with open(audio_file, 'rb') as f:
                while True:
                    data = f.read(1280)
                    if not data:
                        break
                    frame = {
                        "data": {
                            "status": 1,
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": base64.b64encode(data).decode()
                        }
                    }
                    ws.send(json.dumps(frame))
                    time.sleep(0.04)
            end = {
                "data": {
                    "status": 2,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": ""
                }
            }
            ws.send(json.dumps(end))

        threading.Thread(target=run, args=(audio_file,)).start()
    def on_message(self, ws, message):
        result = json.loads(message)
        code = result["code"]
        if code != 0:
            print(f"Error: {result['message']}")
            ws.close()
        else:
            if result["data"]["status"] == 2:
                ws.close()
            if result["data"]["result"]:
                result_str = ''.join([w["cw"][0]["w"] for w in result["data"]["result"]["ws"]])
                print(result_str)

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    def recognize(self, audio_file):
        url = self.create_url()
        print(url)
        ws = websocket.WebSocketApp(url,
            on_open=lambda w: self.on_open(w, audio_file),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)
        ws.run_forever()