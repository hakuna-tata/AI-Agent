import websockets
import uuid
import json
import gzip
import copy
import io

MESSAGE_TYPES = {11: "audio - only server response", 12: "frontend server response", 15: "error message from server"}
MESSAGE_TYPE_SPECIFIC_FLAGS = {0: "no sequence number", 1: "sequence number > 0",
                               2: "last message from server (seq < 0)", 3: "sequence number < 0"}
MESSAGE_SERIALIZATION_METHODS = {0: "no serialization", 1: "JSON", 15: "custom type"}
MESSAGE_COMPRESSIONS = {0: "no compression", 1: "gzip", 15: "custom compression method"}


class TTSClient:
    def __init__(self, appid, token, cluster, voice_type, host="openspeech.bytedance.com"):
        self.appid = appid
        self.token = token
        self.cluster = cluster
        self.voice_type = voice_type
        self.host = host
        self.api_url = f"wss://{self.host}/api/v1/tts/ws_binary"
        self.default_header = bytearray(b'\x11\x10\x11\x00')
        self.request_json = {
            "app": {
                "appid": self.appid,
                "token": self.token,
                "cluster": self.cluster
            },
            "user": {
                "uid": "3888080871850881223"
            },
            "audio": {
                "voice_type": self.voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": uuid.uuid4(),
                "text": "",
                "text_type": "plain",
                "operation": "xxx"
            }
        }

    async def submit_tts(self, text):
        submit_request_json = copy.deepcopy(self.request_json)
        submit_request_json["audio"]["voice_type"] = self.voice_type
        submit_request_json["request"]["reqid"] = str(uuid.uuid4())
        submit_request_json["request"]["text"] = text
        submit_request_json["request"]["operation"] = "submit"
        payload_bytes = str.encode(json.dumps(submit_request_json))
        payload_bytes = gzip.compress(payload_bytes)
        full_client_request = bytearray(self.default_header)
        full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))
        full_client_request.extend(payload_bytes)

        audio_data = io.BytesIO()
        header = {"Authorization": f"Bearer; {self.token}"}
        async with websockets.connect(self.api_url, additional_headers=header, ping_interval=None) as ws:
            await ws.send(full_client_request)
            while True:
                res = await ws.recv()
                done = self.parse_response(res, audio_data)
                if done:
                    break
            audio_data.seek(0)
            print("\nclosing the connection...")
            content = audio_data.read()
            audio_data.close()
            return content
    async def run_submit_tts(self, text):
        return await self.submit_tts(text)

    async def query_tts(self, text):
        query_request_json = copy.deepcopy(self.request_json)
        query_request_json["audio"]["voice_type"] = self.voice_type
        query_request_json["request"]["reqid"] = str(uuid.uuid4())
        query_request_json["request"]["text"] = text
        query_request_json["request"]["operation"] = "query"
        payload_bytes = str.encode(json.dumps(query_request_json))
        payload_bytes = gzip.compress(payload_bytes)  # if no compression, comment this line
        full_client_request = bytearray(self.default_header)
        full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
        full_client_request.extend(payload_bytes)  # payload
        file_to_save = open("answer_voice.mp3", "wb")
        header = {"Authorization": f"Bearer; {self.token}"}
        async with websockets.connect(self.api_url, additional_headers=header, ping_interval=None) as ws:
            await ws.send(full_client_request)
            res = await ws.recv()
            self.parse_response(res, file_to_save)
            file_to_save.close()
            print("\nclosing the connection...")

    def parse_response(self, res, file):
        print("--------------------------- response ---------------------------")
        header_size = res[0] & 0x0f
        message_type = res[1] >> 4
        message_type_specific_flags = res[1] & 0x0f
        message_compression = res[2] & 0x0f
        header_extensions = res[4:header_size * 4]
        payload = res[header_size * 4:]

        if header_size != 1:
            print(f"           Header extensions: {header_extensions}")
        if message_type == 0xb:  # audio - only server response
            if message_type_specific_flags == 0:  # no sequence number as ACK
                print("                Payload size: 0")
                return False
            else:
                sequence_number = int.from_bytes(payload[:4], "big", signed=True)
                payload_size = int.from_bytes(payload[4:8], "big", signed=False)
                payload = payload[8:]
                print(f"             Sequence number: {sequence_number}")
                print(f"                Payload size: {payload_size} bytes")
            file.write(payload)
            if sequence_number < 0:
                return True
            else:
                return False
        elif message_type == 0xf:
            code = int.from_bytes(payload[:4], "big", signed=False)
            msg_size = int.from_bytes(payload[4:8], "big", signed=False)
            error_msg = payload[8:]
            if message_compression == 1:
                error_msg = gzip.decompress(error_msg)
            error_msg = str(error_msg, "utf - 8")
            print(f"          Error message code: {code}")
            print(f"          Error message size: {msg_size} bytes")
            print(f"               Error message: {error_msg}")
            return True
        elif message_type == 0xc:
            msg_size = int.from_bytes(payload[:4], "big", signed=False)
            payload = payload[4:]
            if message_compression == 1:
                payload = gzip.decompress(payload)
            print(f"            Frontend message: {payload}")
        else:
            print("undefined message type!")
            return True
