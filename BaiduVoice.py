import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('baidu_tts_api_key')
SECRET_KEY = os.getenv('baidu_tts_api_secret')


def tts(text):
    url = "https://tsn.baidu.com/text2audio"

    payload = 'tex='+text+'&tok=' + get_access_token() + '&cuid=2Sg5H3hVWF0lAGowMHtTBTARKgeSsRrp&ctp=1&lan=zh&spd=5&pit=5&vol=5&per=1&aue=3'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            answer_mp3_path='answer_voice.mp3'
            if content_type.startswith('audio/'):
                with open(answer_mp3_path, 'wb') as f:
                    f.write(response.content)
            elif content_type.startswith('application/json'):
                error = json.loads(response.content)
                raise Exception('baidu语音合成失败，原因是：'+error['err_msg'])
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        raise Exception('baidu语音合成请求发生异常')


def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    tts("你太顽皮了")