import os
from flask import Flask
from voice_processing import VoiceProcessor

app = Flask(__name__)
processor = VoiceProcessor('117689738', 'i570W6mSVYwiyzVTCqDiHro8', 'n2F9vbzUfIXSpiNGdXsY6sSNcsf4pHPW')

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'

    return response


@app.route('/voice_process', methods=['GET'])
def voice_process():
    try:
        # file_path = os.path.join(os.getcwd(), 'test.wav')
        answer_wav_path = processor.process_voice(file_path)
        if answer_wav_path:
            return answer_wav_path
        else:
            return "语音处理失败", 500
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
