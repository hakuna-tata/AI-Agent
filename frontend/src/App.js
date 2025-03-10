import React, { useState, useEffect } from 'react';
import { Input, Button, SpinLoading  } from 'antd-mobile';
import convertToWAV from './utils/convertToWAV' 
import './App.css';
import Speech from 'speak-tts';

const sp = new Speech();

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
              const audioUrl = URL.createObjectURL(wavBlob);
              setMessages(prevMessages => [
                ...prevMessages,
                { id: Date.now(), type: 'sent', mediaType: 'audio', content: audioUrl }
              ]);
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
    const initSpeak = async () => {
      try {
        await sp.init({
          volume: 1,
          lang: 'zh-CN',
          rate: 1,
          pitch: 1,
        });
      } catch (error) {
        console.error('语音初始化失败:', error);
      }
    };
    initSpeak();
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

  const sendMessage = async () => {
    if (inputText.trim() !== '') {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), type: 'sent', mediaType: 'text', content: inputText }
      ]);
      setInputText('');

      const reply = "你好";
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), type: 'received', mediaType: 'text', content: reply }
      ]);

      try {
        await sp.speak({ text: reply });
      } catch (error) {
        console.error('语音播放失败:', error);
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
          <Button className='button' color='primary' onClick={sendMessage}>发送</Button>
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
