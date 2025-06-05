# main.py

import os
import wave
import time
import pyaudio
import threading

def load_scripts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

class Recorder:
    def __init__(self, filename):
        self.filename = filename
        self.frames = []
        self.running = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.thread = None

    def start(self):
        self.running = True
        self.frames = []
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=4096)
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def _record(self):
        print("録音中... 's' + Enter で停止")
        while self.running:
            data = self.stream.read(4096, exception_on_overflow=False)
            self.frames.append(data)

    def stop_and_save(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()  # スレッドの終了を必ず待つ
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
        print("録音終了・保存しました")

def play_audio(filename):
    chunk = 4096
    wf = wave.open(filename, 'rb')
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    pa.terminate()
    wf.close()

def clear_screen():
    os.system('clear')  # Linux/Mac
    # os.system('cls')  # Windowsの場合はこちら

def main():
    input_file = 'data/input/cocoro.txt'
    audio_dir = 'dataset/audio_files'
    meta_dir = 'dataset/meta_files'
    metadata_file = 'dataset/metadata.txt'
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)  # メタファイル用ディレクトリ作成

    scripts = load_scripts(input_file)
    total = len(scripts)
    idx = 0
    metadata = []
    while idx < total:
        clear_screen()
        script = scripts[idx]
        print(f"台本 [{idx+1}/{total}]:\n{script}")
        print("\n--- 操作コマンド ---")
        print("r：録音開始")
        print("p：録音音声の再生")
        print("r：再録音")
        print("s：録音を保存")
        print("n：次の台本へ")
        print("="*40)
        temp_audio = os.path.join(audio_dir, f"audio_{idx+1}_temp.wav")
        final_audio = os.path.join(audio_dir, f"audio_{idx+1}.wav")
        meta_file = os.path.join(meta_dir, f"meta_{idx+1}.txt")
        recorded = False
        saved = False
        recorder = None
        while True:
            cmd = input("コマンドを入力してください（r/p/s/n）: ").strip().lower()
            if cmd == 'r':
                print("3秒後に録音開始します...")
                time.sleep(1)
                print("2...")
                time.sleep(1)
                print("1...")
                time.sleep(1)
                recorder = Recorder(temp_audio)
                recorder.start()
                input("'s' + Enter で録音を停止します: ")
                recorder.stop_and_save()
                recorded = True
                saved = False
            elif cmd == 'p' and recorded:
                print("再生中...")
                play_audio(temp_audio)
                print("再生終了")
            elif cmd == 's' and recorded:
                os.rename(temp_audio, final_audio)
                metadata.append(f"{script}|audio_{idx+1}.wav")
                # 台本テキストをmetaファイルとして保存
                with open(meta_file, 'w', encoding='utf-8') as mf:
                    mf.write(script)
                print(f"保存しました。meta_{idx+1}.txt を作成しました。nで次へ")
                saved = True
            elif cmd == 'n' and saved and os.path.exists(final_audio):
                break
        idx += 1
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(metadata))
    print("全て完了しました。")

if __name__ == "__main__":
    main()