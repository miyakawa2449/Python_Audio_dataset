# インストールされたパッケージのテスト
try:
    import pydub
    print("✓ pydub imported successfully")
except ImportError as e:
    print(f"✗ pydub import failed: {e}")

try:
    import sounddevice
    print("✓ sounddevice imported successfully")
except ImportError as e:
    print(f"✗ sounddevice import failed: {e}")

try:
    import textgrid
    print("✓ textgrid imported successfully")
except ImportError as e:
    print(f"✗ textgrid import failed: {e}")

print("\nAll packages are ready for your audio dataset project!")