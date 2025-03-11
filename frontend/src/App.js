import React, { useState, useEffect } from 'react';
import { Input, Button, SpinLoading  } from 'antd-mobile';
import axios from "axios";
import convertToWAV from './utils/convertToWAV';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isSpeak, setIsSpeak] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  useEffect(() => {
    if (navigator.mediaDevices) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const mr = new MediaRecorder(stream);
          let audioChunks = [];
          mr.ondataavailable = (event) => {
            if (event.data.size > 0) {
              audioChunks.push(event.data);
            }
          };
          mr.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            convertToWAV(audioBlob).then((wavBlob) => {
              sendVoice(wavBlob);
              audioChunks = [];
            });
          };
          setMediaRecorder(mr);
        })
        .catch(error => {
          console.error('获取音频设备失败:', error);
        });
    } else {
      console.error('浏览器不支持语音录入功能');
    }
  }, []);

  useEffect(() => {
    const handleContextMenu = (e) => {
      e.preventDefault();
    };
    document.addEventListener('contextmenu', handleContextMenu);
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, []);

  const sendText = async () => {
    if (inputText.trim() !== '') {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), type: 'sent', mediaType: 'text', content: inputText }
      ]);
      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/text_process',
          { text: inputText },
          {
            responseType: "blob",
          }
        );
        setInputText('');

        const audioUrl = URL.createObjectURL(response.data);
        setMessages((prevMessages) => [
          ...prevMessages,
          { id: Date.now(), type: 'received', mediaType: 'audio', content: audioUrl },
        ]);
      } catch (e) {
        console.error('语音获取失败:', e);
      } finally {
        setInputText('');
      }
    }
  };
  const sendVoice = async (wavBlob) => {
    if (wavBlob) {
      const audioUrl = URL.createObjectURL(wavBlob);
      setMessages(prevMessages => [
        ...prevMessages,
        { id: Date.now(), type: 'sent', mediaType: 'audio', content: audioUrl },
      ]);

      try {
        const formData = new FormData();
        formData.append('voice', wavBlob, 'voice.wav');
        const response = await axios.post(
          'http://127.0.0.1:5000/voice_process',
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            responseType: "blob",
          }
        );

        const audioUrl = URL.createObjectURL(response.data);
        setMessages((prevMessages) => [
          ...prevMessages,
          { id: Date.now(), type: 'received', mediaType: 'audio', content: audioUrl },
        ]);
      } catch(e) {
        console.error('语音获取失败:', e);
      }
    }
  };

  const handleTouchStart = () => {
    setIsSpeak(true);
    mediaRecorder?.start();
  };
  const handleTouchEnd = () => {
    setIsSpeak(false);
    mediaRecorder?.stop();
  };

  return (
    <div className="app-container">
      <div className="chat-header">
        <div className="avatar"></div>
        <div className="name">懒羊羊</div>
      </div>
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            {msg.mediaType === "audio" && (
              <audio src={msg.content} controls className="audio" />
            )}
            {
              msg.mediaType === "text" && msg.content
            }
          </div>
        ))}
      </div>
      <div className="input-container">
        <div className="chat-input">
          <Input
            placeholder='请输入内容'
            value={inputText}
            onChange={(val) => setInputText(val)}
          />
          <Button className='button' color='primary' onClick={sendText}>发送</Button>
          <Button
            className='button'
            color='primary'
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
          >{isSpeak ? '停止' : '语音'}</Button>
        </div>
      </div>
      {isSpeak && (
         <div className="loading-overlay">
          <div className="loading-content">
            <SpinLoading color='currentColor' />
            <p>正在讲话中...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
