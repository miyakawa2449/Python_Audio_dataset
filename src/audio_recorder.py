import sounddevice as sd
import numpy as np
import wave
import threading
import time
from pathlib import Path

class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.is_paused = False
        self.recorded_data = []
        self.current_recording = None
        self.recording_thread = None
        
    def start_recording(self):
        """録音開始"""
        if self.is_recording:
            return False
            
        self.is_recording = True
        self.is_paused = False
        self.recorded_data = []
        
        def record_callback(indata, frames, time, status):
            if not self.is_paused and self.is_recording:
                self.recorded_data.extend(indata.copy())
        
        self.stream = sd.InputStream(
            callback=record_callback,
            samplerate=self.sample_rate,
            channels=self.channels
        )
        self.stream.start()
        return True
    
    def pause_recording(self):
        """録音一時停止"""
        self.is_paused = True
        return True
    
    def resume_recording(self):
        """録音再開"""
        if self.is_recording:
            self.is_paused = False
            return True
        return False
    
    def stop_recording(self):
        """録音停止"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        self.is_paused = False  # 追加: 停止時にpaused状態もリセット
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if self.recorded_data:
            return np.array(self.recorded_data)
        return None
    
    def save_audio(self, audio_data, filename):
        """音声データを保存"""
        output_path = Path("dataset/audio_files") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 音声データを正規化
        audio_data = audio_data / np.max(np.abs(audio_data))
        audio_data = (audio_data * 32767).astype(np.int16)
        
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        return str(output_path)
    
    def play_audio(self, audio_data):
        """録音した音声を再生"""
        if audio_data is not None:
            sd.play(audio_data, self.sample_rate)
            sd.wait()
    
    def reset_recording(self):
        """録音状態を完全にリセット"""
        if self.is_recording:
            self.stop_recording()
        
        self.is_recording = False
        self.is_paused = False
        self.recorded_data = []
        
        if hasattr(self, 'stream'):
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass  # ストリームが既に閉じられている場合を考慮