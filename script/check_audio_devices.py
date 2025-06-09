import sounddevice as sd

print("Available audio devices:")
print("=" * 50)

devices = sd.query_devices()

for i, device in enumerate(devices):
    device_type = []
    if device['max_input_channels'] > 0:
        device_type.append("Input")
    if device['max_output_channels'] > 0:
        device_type.append("Output")
    
    print(f"Device ID {i}: {device['name']}")
    print(f"  Type: {' & '.join(device_type)}")
    print(f"  Input channels: {device['max_input_channels']}")
    print(f"  Output channels: {device['max_output_channels']}")
    print(f"  Sample rate: {device['default_samplerate']:.0f} Hz")
    print("-" * 30)

print("\nDefault devices:")
print(f"Input: {sd.query_devices(kind='input')['name']}")
print(f"Output: {sd.query_devices(kind='output')['name']}")

# マイクのテスト録音（オプション）
print("\nTesting microphone...")
print("Recording for 1 second...")
try:
    # 1秒間のテスト録音
    test_recording = sd.rec(int(1 * 44100), samplerate=44100, channels=1)
    sd.wait()  # 録音完了まで待機
    print("✓ Microphone test successful!")
    print(f"✓ Recorded {len(test_recording)} samples")
except Exception as e:
    print(f"✗ Microphone test failed: {e}")

print("\nSystem is ready for audio recording!")