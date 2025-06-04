# main.py

import os
import wave
import time
import pyaudio  # 音声録音と再生のためのライブラリ

def load_scripts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def record_audio(filename):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=4096)
    frames = []
    print("録音中... 's' + Enter で停止")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        frames.append(data)
        if input("録音を終了するには 's' を入力してEnter: ").strip().lower() == 's':
            break
    stream.stop_stream()
    stream.close()
    audio.terminate()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
    print("録音終了")

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

def main():
    input_file = 'data/input/cocoro.txt'
    audio_dir = 'dataset/audio_files'
    metadata_file = 'dataset/metadata.txt'
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    scripts = load_scripts(input_file)
    total = len(scripts)
    idx = 0
    metadata = []
    while idx < total:
        script = scripts[idx]
        print("\n" + "="*40)
        print(f"台本 [{idx+1}/{total}]:\n{script}")
        print("\n--- 操作コマンド ---")
        print("r：録音開始（3秒カウントダウン後）")
        print("p：録音音声の再生")
        print("r：再録音")
        print("s：録音を保存")
        print("n：次の台本へ")
        print("="*40)
        temp_audio = os.path.join(audio_dir, f"audio_{idx+1}_temp.wav")
        final_audio = os.path.join(audio_dir, f"audio_{idx+1}.wav")
        recorded = False
        while True:
            cmd = input("コマンドを入力してください（r/p/s/n）: ").strip().lower()
            if cmd == 'r':
                print("3秒後に録音開始します...")
                time.sleep(1)
                print("2...")
                time.sleep(1)
                print("1...")
                time.sleep(1)
                record_audio(temp_audio)
                recorded = True
            elif cmd == 'p' and recorded:
                print("再生中...")
                play_audio(temp_audio)
                print("再生終了")
            elif cmd == 's' and recorded:
                os.rename(temp_audio, final_audio)
                metadata.append(f"{script}|audio_{idx+1}.wav")
                print("保存しました。nで次へ")
            elif cmd == 'n' and recorded and os.path.exists(final_audio):
                break
        idx += 1
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(metadata))
    print("全て完了しました。")

if __name__ == "__main__":
    main()