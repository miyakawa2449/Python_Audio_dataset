def split_text_into_segments(text, min_duration=3, max_duration=5):
    import re

    # 1. Split the text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    segments = []
    current_segment = ""
    current_duration = 0

    # 2. Iterate through sentences and create segments
    for sentence in sentences:
        # Estimate duration based on average speaking rate (about 150 words per minute)
        estimated_duration = len(sentence.split()) / 150 * 60
        
        if current_duration + estimated_duration > max_duration:
            # If adding this sentence exceeds max duration, save the current segment
            segments.append(current_segment.strip())
            current_segment = sentence
            current_duration = estimated_duration
        else:
            # Add sentence to the current segment
            current_segment += " " + sentence
            current_duration += estimated_duration

    # Add the last segment if it exists
    if current_segment:
        segments.append(current_segment.strip())

    return segments

def create_audio_dataset(input_file, output_dir, metadata_file):
    import os
    import sounddevice as sd
    import numpy as np
    import wave

    # Read the text from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split the text into segments
    segments = split_text_into_segments(text)

    # Prepare metadata
    metadata = []

    # Record audio for each segment
    for i, segment in enumerate(segments):
        print(f"Recording segment {i + 1}/{len(segments)}: {segment}")
        
        # Record audio
        fs = 44100  # Sample rate
        duration = 5  # seconds
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished

        # Save the recording
        audio_file_name = f"audio_segment_{i + 1}.wav"
        audio_file_path = os.path.join(output_dir, audio_file_name)
        with wave.open(audio_file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

        # Append to metadata
        metadata.append(f"{audio_file_name}|{segment}")

    # Write metadata to file
    with open(metadata_file, 'w', encoding='utf-8') as f:
        for entry in metadata:
            f.write(entry + '\n')

# Example usage
if __name__ == "__main__":
    input_file = 'data/input/cocoro.txt'
    output_dir = 'dataset/audio_files'
    metadata_file = 'dataset/metadata.txt'

    create_audio_dataset(input_file, output_dir, metadata_file)