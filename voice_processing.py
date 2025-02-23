from aip import AipSpeech

class VoiceProcessor:
    def __init__(self, app_id, api_key, secret_key):
        self.speech_client = AipSpeech(app_id, api_key, secret_key)

    def process_voice(self, voice_file_path):
        try:
            with open(voice_file_path, 'rb') as f:
                audio_data = f.read()
            result = self.speech_client.asr(audio_data, 'wav', 16000, {
                'dev_pid': 1537,
            })
            if result['err_no'] == 0:
                text = result['result'][0]
                return text
            else:
                raise Exception("语音识别失败")
        except Exception as e:
            print(f"处理语音时出错: {e}")
        
            return None
        
    def parse_voice(self, voice_file_path):
        try:
            with open(voice_file_path, 'rb') as f:
                audio_data = f.read()
            result = self.speech_client.asr(audio_data, 'wav', 16000, {
                'dev_pid': 1537,
            })
            if result['err_no'] == 0:
                text = result['result'][0]
                return text
            else:
                raise Exception("语音识别失败")
        except Exception as e:
            print(f"处理语音时出错: {e}")
        
            return None
        
    def aiChat(self):
        return None

    def generate_voice(self):
        return None
