function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}


function createWAV(audioBuffer) {
    const numOfChannels = audioBuffer.numberOfChannels;
    const length = audioBuffer.length * numOfChannels * 2; // 16-bit PCM
    const buffer = new ArrayBuffer(44 + length); // WAV 文件头长度为 44 字节
    const view = new DataView(buffer);

    // 写入 WAV 文件头
    writeString(view, 0, 'RIFF'); // RIFF Header
    view.setUint32(4, 36 + length, true); // File size
    writeString(view, 8, 'WAVE'); // WAVE Header
    writeString(view, 12, 'fmt '); // fmt Subchunk
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
    view.setUint16(22, numOfChannels, true); // Number of channels
    view.setUint32(24, audioBuffer.sampleRate, true); // Sample rate
    view.setUint32(28, audioBuffer.sampleRate * numOfChannels * 2, true); // Byte rate
    view.setUint16(32, numOfChannels * 2, true); // Block align
    view.setUint16(34, 16, true); // Bits per sample
    writeString(view, 36, 'data'); // data Subchunk
    view.setUint32(40, length, true); // Data size

    // 写入音频数据
    let offset = 44;
    for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
        const channelData = audioBuffer.getChannelData(i);
        for (let j = 0; j < channelData.length; j++) {
            const sample = Math.max(-1, Math.min(1, channelData[j])); // Clamp sample to [-1, 1]
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true); // Convert to 16-bit PCM
            offset += 2;
        }
    }

    return new Blob([view], { type: 'audio/wav' });
}

export function convertToWAV(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
            const arrayBuffer = reader.result;
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            audioContext.decodeAudioData(arrayBuffer, (audioBuffer) => {
                const wavBlob = createWAV(audioBuffer);
                resolve(wavBlob);
            }, (error) => reject(error));
        };

        reader.onerror = (error) => reject(error);
        reader.readAsArrayBuffer(blob);
    });
}