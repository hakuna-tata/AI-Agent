import os
from dotenv import load_dotenv
from flask import Flask, request, send_file, send_from_directory
from voice_processing import VoiceProcessor

app = Flask(__name__)

load_dotenv()
processor = VoiceProcessor(
    os.getenv('AipSpeech_APP_ID'),
    os.getenv('AipSpeech_API_KEY'),
    os.getenv('AipSpeech_SECRET_KEY'),
    os.getenv('OPENAI_API_KEY')
)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'

    return response

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/voice_process', methods=['POST'])
def voice_process():
    try:
        voice_file = request.files['voice']
        voice_path = 'received_voice.wav'
        voice_file.save(voice_path)
        answer_mp3_path = processor.voice_process_chain(voice_path)
        if answer_mp3_path:
            return send_file(answer_mp3_path, mimetype='audio/mp3')
        else:
            return "语音处理失败", 500
        
    except Exception as e:
        return str(e), 500
    
    finally:
        if os.path.exists('received_voice.wav'):
            os.remove('received_voice.wav')
        if os.path.exists('answer_voice.mp3'):
            os.remove('answer_voice.mp3')
        if os.path.exists('answer_voice.wav'):
            os.remove('answer_voice.wav')
        if os.path.exists('answer_voice.mp3'):
            os.remove('answer_voice.mp3')

if __name__ == '__main__':
    app.run(debug=True)
