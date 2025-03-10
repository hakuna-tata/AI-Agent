import time
from aip import AipSpeech
from openai import OpenAI

import voice_copy_tts


class VoiceProcessor:
    def __init__(self, app_id, api_key, secret_key, openai_key):
        self.speech_client = AipSpeech(
            app_id,
            api_key,
            secret_key
        )
        self.openai_client = OpenAI(
            api_key=openai_key,
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
        )
        self.messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，能够回答用户问题并且解决问题，给用户提供情绪价值。"
            }
        ]
        
    def parse_voice(self, voice_file_path):
        try:
            start_time = time.time()
            with open(voice_file_path, 'rb') as f:
                audio_data = f.read()
            result = self.speech_client.asr(audio_data, 'wav', 16000, {
                'dev_pid': 1537,
            })
            if result['err_no'] == 0:
                end_time = time.time()
                print("语音解析结果:", result['result'][0])
                print(f"语音解析耗时: {end_time - start_time:.4f} 秒")
                return result['result'][0]
            else:
                raise Exception("语音识别失败")
            
        except Exception as e:
            print(f"处理语音时出错: {e}")
            return None
        
    def aiChat(self, content):
        start_time = time.time()
        self.messages.append({"role": "user", "content": content})
        try:
            completion = self.openai_client.chat.completions.create(
                model="qwen-turbo",
                messages=self.messages
            )
            assistant_output = completion.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_output})
            end_time = time.time()
            print("大模型回答结果:", assistant_output)
            print(f"大模型对话耗时: {end_time - start_time:.4f} 秒")
            return assistant_output
        
        except Exception as e:
            print(f"大模型处理时出错: {e}")
            return None 

    def generate_voice(self, answer):
        try:
            start_time = time.time()
            result = self.speech_client.synthesis(answer, 'zh', 1, {
                'vol': 5,
            })
            if not isinstance(result, dict):
                answer_mp3_path = 'answer_voice.mp3'
                with open(answer_mp3_path, 'wb') as f:
                    f.write(result)
                end_time = time.time()
                print(f"语音合成耗时: {end_time - start_time:.4f} 秒")
                return answer_mp3_path
            else:
                raise Exception("语音合成失败")
            
        except Exception as e:
            print(f"处理语音时出错: {e}")
            return None

    def voice_process_chain(self, voice_file_path):
        try:
            client_voice_conetent=self.parse_voice(voice_file_path)
            ai_chat_content=self.aiChat(client_voice_conetent)
            generate_content_audio=voice_copy_tts.submit_tts(ai_chat_content)
            return generate_content_audio
        
        except Exception as e:
            print(f"流程链式调用失败: {e}")
            return None