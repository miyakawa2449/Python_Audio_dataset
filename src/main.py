# main.py

import os
import time
from text_manager import TextManager
from audio_recorder import AudioRecorder
from pathlib import Path

class AudioDatasetCreator:
    def __init__(self):
        self.text_manager = TextManager()
        self.audio_recorder = AudioRecorder()
        self.current_audio = None
        self.setup_directories()
    
    def setup_directories(self):
        """必要なディレクトリを作成"""
        Path("dataset/audio_files").mkdir(parents=True, exist_ok=True)
        Path("dataset/meta_files").mkdir(parents=True, exist_ok=True)
    
    def display_interface(self):
        """ユーザーインターフェースを表示"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        current_text = self.text_manager.get_current_text()
        progress = self.text_manager.get_progress()
        
        print("=" * 60)
        print("🎙️  AI音声学習用データセット作成ツール")
        print("=" * 60)
        
        if current_text:
            print(f"\n📄 原稿ファイル: {current_text['file']}")
            print(f"📝 台本 ({progress['current']}/{progress['total']}):")
            print(f"   {current_text['text']}")
            print(f"\n📊 進捗: {progress['recorded']}/{progress['total']} 録音済み ({progress['progress_percent']:.1f}%)")
            
            status = "✅ 録音済み" if current_text['recorded'] else "⭕ 未録音"
            print(f"📍 状態: {status}")
        
        print("\n" + "=" * 60)
        print("🎛️  操作コマンド:")
        print("   r  : 録音開始/再開")
        print("   p  : 録音一時停止")
        print("   s  : 録音停止・保存")
        print("   l  : 録音音声の再生")
        print("   n  : 次の台本へ")
        print("   b  : 前の台本へ")
        print("   j  : 指定行にジャンプ")
        print("   rf : テキストファイル再読み込み")
        print("   q  : 終了")
        print("   sync : ファイルとセッション同期")
        print("=" * 60)
    
    def countdown(self, seconds=3):
        """カウントダウン表示"""
        for i in range(seconds, 0, -1):
            print(f"\r🔴 録音開始まで {i} 秒...", end="", flush=True)
            time.sleep(1)
        print("\r🔴 録音中... (pで一時停止、sで停止)    ")
    
    def run(self):
        """メインループ"""
        # セッション復元または新規作成
        if not self.text_manager.load_session():
            print("📚 テキストファイルを読み込んでいます...")
            self.text_manager.load_all_texts()
            print(f"✅ {self.text_manager.total_lines} 行のテキストを読み込みました")
        else:
            print("📚 セッションを復元しました")
            # 既存セッションの場合、ファイルと同期
            print("🔄 録音ファイルとの同期を確認中...")
            self.text_manager.sync_with_actual_files()
    
        time.sleep(2)
        
        while True:
            self.display_interface()
            command = input("\nコマンドを入力してください: ").strip().lower()
            
            if command == 'r':
                # 録音状態をリセットしてから開始
                self.audio_recorder.reset_recording()
                
                if not self.audio_recorder.is_recording:
                    self.countdown()
                    if self.audio_recorder.start_recording():
                        print("🎙️ 録音開始！")
                    else:
                        print("❌ 録音開始に失敗しました")
                        input("Enterを押して続行...")
                else:
                    if self.audio_recorder.resume_recording():
                        print("▶️ 録音再開")
            
            elif command == 'p':
                if self.audio_recorder.is_recording:
                    self.audio_recorder.pause_recording()
                    print("⏸️ 録音一時停止")
            
            elif command == 's':
                if self.audio_recorder.is_recording:
                    current_text = self.text_manager.get_current_text()
                    
                    # 新しいファイル名形式
                    file_number = self.text_manager.get_next_filename()
                    audio_filename = f"audio_{file_number}.wav"
                    meta_filename = f"meta_{file_number}.txt"
                    
                    # 既存ファイルのチェック
                    existing_audio = Path("dataset/audio_files") / audio_filename
                    if existing_audio.exists():
                        overwrite = input(f"⚠️  {audio_filename} は既に存在します。上書きしますか？ (y/n): ").strip().lower()
                        if overwrite != 'y':
                            print("❌ 録音保存をキャンセルしました")
                            input("Enterを押して続行...")
                            continue
                    
                    self.current_audio = self.audio_recorder.stop_recording()
                    if self.current_audio is not None:
                        # 音声ファイル保存
                        self.audio_recorder.save_audio(self.current_audio, audio_filename)
                        
                        # メタファイル保存
                        self.save_meta_file(current_text, meta_filename, file_number)
                        
                        # metadata.txt更新
                        self.update_metadata_file(audio_filename, current_text['text'])
                        
                        # セッション更新
                        self.text_manager.mark_as_recorded(audio_filename, file_number)
                        
                        print(f"💾 録音保存完了: {audio_filename}")
                        print(f"📝 テキスト保存: {meta_filename}")
                        input("Enterを押して続行...")
            
            elif command == 'l':
                if self.current_audio is not None:
                    print("🔊 録音音声を再生中...")
                    self.audio_recorder.play_audio(self.current_audio)
                else:
                    print("❌ 再生する音声がありません")
                    input("Enterを押して続行...")
            
            elif command == 'n':
                if self.text_manager.current_line < self.text_manager.total_lines - 1:
                    self.text_manager.current_line += 1
                    self.text_manager.save_session()
                    self.current_audio = None
            
            elif command == 'b':
                if self.text_manager.current_line > 0:
                    self.text_manager.current_line -= 1
                    self.text_manager.save_session()
                    self.current_audio = None
            
            elif command == 'j':
                try:
                    line_num = int(input("ジャンプする行番号を入力: ")) - 1
                    if 0 <= line_num < self.text_manager.total_lines:
                        self.text_manager.current_line = line_num
                        self.text_manager.save_session()
                        self.current_audio = None
                    else:
                        print("❌ 無効な行番号です")
                        input("Enterを押して続行...")
                except ValueError:
                    print("❌ 数値を入力してください")
                    input("Enterを押して続行...")
            
            elif command == 'refresh' or command == 'rf':
                print("📚 テキストファイルを再読み込み中...")
                current_line = self.text_manager.current_line  # 現在位置を保存
                self.text_manager.load_all_texts()
                # 現在位置が範囲外になった場合は最後の行に移動
                if current_line >= self.text_manager.total_lines:
                    self.text_manager.current_line = max(0, self.text_manager.total_lines - 1)
                else:
                    self.text_manager.current_line = current_line
                self.text_manager.save_session()
                self.current_audio = None
                print(f"✅ テキスト再読み込み完了 ({self.text_manager.total_lines} 行)")
                input("Enterを押して続行...")
            
            elif command == 'q':
                if self.audio_recorder.is_recording:
                    self.audio_recorder.stop_recording()
                print("👋 お疲れさまでした！")
                break
            
            elif command == 'status' or command == 'st':
                print("📊 詳細ステータス:")
                recorded_lines = [i+1 for i, text in enumerate(self.text_manager.all_texts) if text['recorded']]
                unrecorded_lines = [i+1 for i, text in enumerate(self.text_manager.all_texts) if not text['recorded']]
                
                print(f"   現在の行: {self.text_manager.current_line + 1}")
                print(f"   総行数: {self.text_manager.total_lines}")
                print(f"   録音済み: {len(recorded_lines)} 行")
                print(f"   未録音: {len(unrecorded_lines)} 行")
                
                if len(unrecorded_lines) <= 20:  # 未録音が20行以下なら表示
                    print(f"   未録音の行番号: {unrecorded_lines}")
                else:
                    print(f"   未録音の行番号（最初の10行）: {unrecorded_lines[:10]}")
                
                input("Enterを押して続行...")
            
            elif command == 'cleanup':
                print("🧹 重複データのクリーンアップ中...")
                self.cleanup_duplicates()
                print("✅ クリーンアップ完了")
                input("Enterを押して続行...")
            
            elif command == 'sync':
                print("🔄 セッションデータとファイルを同期中...")
                self.text_manager.sync_with_actual_files()
                print("✅ 同期完了")
                input("Enterを押して続行...")
    
    def save_meta_file(self, text_data, meta_filename, file_number):
        """メタファイルを保存（新形式）"""
        meta_path = Path("dataset/meta_files") / meta_filename
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(text_data['text'])

    def update_metadata_file(self, audio_filename, text_content):
        """metadata.txtの更新（新形式対応）"""
        metadata_path = Path("dataset/metadata.txt")
        
        # 新しいエントリを追加
        with open(metadata_path, 'a', encoding='utf-8') as f:
            f.write(f"{audio_filename}|{text_content}\n")

    def cleanup_duplicates(self):
        """重複したメタデータをクリーンアップ"""
        metadata_path = Path("dataset/metadata.txt")
        if not metadata_path.exists():
            return
        
        # 重複を除去した辞書
        unique_entries = {}
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '|' in line:
                    filename, text = line.strip().split('|', 1)
                    unique_entries[filename] = text
        
        # クリーンアップされたデータを書き戻し
        with open(metadata_path, 'w', encoding='utf-8') as f:
            for filename, text in unique_entries.items():
                f.write(f"{filename}|{text}\n")
        
        print(f"📊 {len(unique_entries)} 件のユニークなエントリを保持")

if __name__ == "__main__":
    app = AudioDatasetCreator()
    app.run()