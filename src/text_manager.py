import os
import json
from pathlib import Path

class TextManager:
    def __init__(self, input_dir="data/input"):
        self.input_dir = Path(input_dir)
        self.current_file = None
        self.current_line = 0
        self.total_lines = 0
        self.all_texts = []
        self.session_file = "data/session.json"
        
    def load_all_texts(self):
        """全てのテキストファイルを読み込み"""
        text_files = list(self.input_dir.glob("*.txt"))
        self.all_texts = []
        
        for file_path in text_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                for i, line in enumerate(lines):
                    self.all_texts.append({
                        'file': file_path.name,
                        'line_number': i + 1,
                        'text': line,
                        'recorded': False,
                        'audio_file': None
                    })
        
        self.total_lines = len(self.all_texts)
        return self.all_texts
    
    def save_session(self):
        """セッション状態を保存"""
        session_data = {
            'current_index': self.current_line,
            'texts': self.all_texts
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def load_session(self):
        """セッション状態を復元"""
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                self.current_line = session_data.get('current_index', 0)
                self.all_texts = session_data.get('texts', [])
                self.total_lines = len(self.all_texts)
                return True
        return False
    
    def get_current_text(self):
        """現在の台本を取得"""
        if 0 <= self.current_line < len(self.all_texts):
            return self.all_texts[self.current_line]
        return None
    
    def mark_as_recorded(self, audio_filename):
        """録音済みとしてマーク"""
        if 0 <= self.current_line < len(self.all_texts):
            self.all_texts[self.current_line]['recorded'] = True
            self.all_texts[self.current_line]['audio_file'] = audio_filename
            self.save_session()
    
    def get_progress(self):
        """進捗情報を取得"""
        recorded_count = sum(1 for text in self.all_texts if text['recorded'])
        return {
            'current': self.current_line + 1,
            'total': self.total_lines,
            'recorded': recorded_count,
            'remaining': self.total_lines - recorded_count,
            'progress_percent': (recorded_count / self.total_lines * 100) if self.total_lines > 0 else 0
        }