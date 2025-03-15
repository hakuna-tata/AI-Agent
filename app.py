import os
import asyncio
import io
from dotenv import load_dotenv
from flask import Flask, request, send_file, send_from_directory
from voice_ai_content import AIChat
from voice_copy import TTSClient

app = Flask(__name__)

load_dotenv()
aiChatClient = AIChat(
    os.getenv('OPEN_AI_KEY')
)
ttsClient = TTSClient(
    os.getenv('VOLC_APP_ID'),
    os.getenv('VOLC_ACCESS_TOKEN'),
    os.getenv('VOLC_CLUSTER'),
    os.getenv('VOLC_VOICE_TYPE')
)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/text_process', methods=['POST'])
def text_process():
    try:
        data = request.get_json()
        text = data.get("text")
        if not text:
            return {"error": "No text provided"}, 400
        
        content = aiChatClient.aiChat(text)
        audio_data = asyncio.run(ttsClient.run_submit_tts(content))
        audio_stream = io.BytesIO(audio_data)
        response = send_file(
            audio_stream,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='synthesized_audio.mp3'
        )
        return response

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/voice_process', methods=['POST'])
def voice_process():
    try:
        voice_file = request.files['voice']
        voice_path = 'received_voice.wav'
        voice_file.save(voice_path)

        audio_text = '你好啊，懒羊羊'
        content = aiChatClient.aiChat(audio_text)
        audio_data = asyncio.run(ttsClient.run_submit_tts(content))
        audio_stream = io.BytesIO(audio_data)
        response = send_file(
            audio_stream,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='synthesized_audio.mp3'
        )
        return response

    except Exception as e:
        return {"error": str(e)}, 500
    
    finally:
        if os.path.exists('received_voice.wav'):
            os.remove('received_voice.wav')

if __name__ == '__main__':
    app.run(debug=True)
