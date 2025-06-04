# main.py

import os
import time
import wave
import pyaudio
from text_processor import split_text_into_segments # 'split_text' を 'split_text_into_segments' に変更

def record_audio(filename, duration):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    print(f"Recording {filename} for {duration} seconds...")
    frames = []

    for _ in range(0, int(44100 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

def main():
    input_file = 'data/input/cocoro.txt'
    audio_dir = 'dataset/audio_files'
    metadata_file = 'dataset/metadata.txt'

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    segments = split_text_into_segments(text, min_duration=3, max_duration=5) # 関数名を変更
    metadata = []

    for i, segment in enumerate(segments):
        filename = os.path.join(audio_dir, f"audio_{i + 1}.wav")
        record_audio(filename, len(segment) / 10)  # Approximate duration based on character count
        metadata.append(f"audio_{i + 1}.wav|{segment.strip()}")

    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(metadata))

if __name__ == "__main__":
    main()