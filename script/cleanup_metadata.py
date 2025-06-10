# cleanup_metadata.py
from pathlib import Path

def cleanup_metadata():
    metadata_path = Path("dataset/metadata.txt")
    
    unique_entries = {}
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line:
                filename, text = line.strip().split('|', 1)
                unique_entries[filename] = text
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        for filename, text in sorted(unique_entries.items()):
            f.write(f"{filename}|{text}\n")
    
    print(f"✅ クリーンアップ完了: {len(unique_entries)} 件のユニークエントリ")

if __name__ == "__main__":
    cleanup_metadata()