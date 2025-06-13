# script/convert_filenames.py
from pathlib import Path
import shutil
import json
import re

def convert_existing_files():
    """既存ファイルを新形式に変換（session.jsonも含む）"""
    
    print("🔄 既存ファイルを新形式に変換中...")
    
    # ファイルパスの確認
    audio_dir = Path("dataset/audio_files")
    meta_dir = Path("dataset/meta_files")
    metadata_path = Path("dataset/metadata.txt")
    session_path = Path("data/session.json")
    
    if not audio_dir.exists() or not metadata_path.exists():
        print("❌ dataset/audio_files または dataset/metadata.txt が見つかりません")
        return
    
    # metadata.txtから対応関係を読み取り
    conversions = []
    filename_mapping = {}  # 旧ファイル名 → 新ファイル名のマッピング
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if '|' in line:
                old_filename, text = line.strip().split('|', 1)
                new_audio = f"audio_{i}.wav"
                new_meta = f"meta_{i}.txt"
                
                conversions.append({
                    'old_audio': old_filename,
                    'new_audio': new_audio,
                    'new_meta': new_meta,
                    'text': text
                })
                
                # ファイル名マッピングを作成
                filename_mapping[old_filename] = new_audio
    
    print(f"📊 {len(conversions)} 件のファイルを変換します")
    
    # バックアップ作成
    backup_dir = Path("dataset/backup")
    backup_dir.mkdir(exist_ok=True)
    shutil.copy2(metadata_path, backup_dir / "metadata_original.txt")
    
    if session_path.exists():
        shutil.copy2(session_path, backup_dir / "session_original.json")
        print("💾 metadata.txt と session.json をバックアップしました")
    else:
        print("💾 metadata.txt をバックアップしました")
    
    # ファイル変換実行
    converted_count = 0
    
    for conv in conversions:
        # 音声ファイル変換
        old_audio_path = audio_dir / conv['old_audio']
        new_audio_path = audio_dir / conv['new_audio']
        
        if old_audio_path.exists():
            if not new_audio_path.exists():  # 重複防止
                shutil.move(old_audio_path, new_audio_path)
                print(f"🔄 {conv['old_audio']} → {conv['new_audio']}")
                converted_count += 1
            else:
                print(f"⚠️ {conv['new_audio']} は既に存在します")
        else:
            print(f"❌ {conv['old_audio']} が見つかりません")
        
        # メタファイル作成
        new_meta_path = meta_dir / conv['new_meta']
        if not new_meta_path.exists():
            with open(new_meta_path, 'w', encoding='utf-8') as f:
                f.write(conv['text'])
            print(f"📝 {conv['new_meta']} 作成")
    
    # session.jsonの更新
    if session_path.exists():
        print("🔄 session.json を更新中...")
        update_session_file(session_path, filename_mapping)
    
    # 新しいmetadata.txt作成
    with open(metadata_path, 'w', encoding='utf-8') as f:
        for conv in conversions:
            f.write(f"{conv['new_audio']}|{conv['text']}\n")
    
    print(f"✅ 変換完了: {converted_count} ファイル")
    print("📋 metadata.txt を新形式で更新しました")
    print("🔄 session.json のファイル名も更新しました")
    print("💾 オリジナルファイルは dataset/backup/ に保存")

def update_session_file(session_path, filename_mapping):
    """session.jsonのファイル名を更新"""
    
    try:
        # session.jsonを読み込み
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        updated_count = 0
        
        # all_textsの各項目を更新
        if 'all_texts' in session_data:
            for text_item in session_data['all_texts']:
                if 'audio_file' in text_item and text_item['audio_file']:
                    old_filename = text_item['audio_file']
                    if old_filename in filename_mapping:
                        new_filename = filename_mapping[old_filename]
                        text_item['audio_file'] = new_filename
                        updated_count += 1
                        print(f"📝 session.json: {old_filename} → {new_filename}")
        
        # 更新されたsession.jsonを保存
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ session.json内の {updated_count} 件のファイル名を更新しました")
        
    except json.JSONDecodeError:
        print("❌ session.json の読み込みに失敗しました（フォーマットエラー）")
    except Exception as e:
        print(f"❌ session.json の更新中にエラーが発生しました: {e}")

def verify_conversion():
    """変換結果の検証"""
    print("\n🔍 変換結果の検証中...")
    
    # ファイル数の確認
    audio_files = list(Path("dataset/audio_files").glob("audio_*.wav"))
    meta_files = list(Path("dataset/meta_files").glob("meta_*.txt"))
    
    print(f"📊 音声ファイル: {len(audio_files)} 件")
    print(f"📊 メタファイル: {len(meta_files)} 件")
    
    # metadata.txtの確認
    metadata_path = Path("dataset/metadata.txt")
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"📊 metadata.txt: {len(lines)} 行")
        
        # 最初の3行を表示
        print("📋 metadata.txt の内容例:")
        for i, line in enumerate(lines[:3], 1):
            print(f"   {i}: {line.strip()}")
    
    # session.jsonの確認
    session_path = Path("data/session.json")
    if session_path.exists():
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            recorded_files = [item['audio_file'] for item in session_data.get('all_texts', []) 
                            if item.get('recorded') and item.get('audio_file')]
            print(f"📊 session.json: {len(recorded_files)} 件の録音済みファイル")
            
            # 最初の3つを表示
            print("📋 session.json の録音済みファイル例:")
            for i, filename in enumerate(recorded_files[:3], 1):
                print(f"   {i}: {filename}")
                
        except Exception as e:
            print(f"❌ session.json の確認中にエラー: {e}")

if __name__ == "__main__":
    print("🎯 ファイル名変換スクリプト（session.json対応版）")
    print("=" * 60)
    
    # 確認メッセージ
    print("変換対象:")
    print("  • 音声ファイル: audio_cocoro.txt_XXXX.wav → audio_N.wav")
    print("  • メタファイル: meta_cocoro.txt_XXXX.txt → meta_N.txt")  
    print("  • metadata.txt: ファイル名を新形式に更新")
    print("  • session.json: 内部のファイル名を新形式に更新")
    print()
    
    confirm = input("既存のファイル名を audio_1.wav 形式に変換しますか？ (y/n): ").strip().lower()
    if confirm == 'y':
        convert_existing_files()
        verify_conversion()
        print("\n🎉 変換が完了しました！")
        print("⚠️ プログラムを再起動して新形式で録音を継続してください")
    else:
        print("❌ 変換をキャンセルしました")