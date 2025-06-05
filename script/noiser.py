import noisereduce as nr
import soundfile as sf

# 録音後のWAVファイルを読み込む
data, rate = sf.read('dataset/audio_files/audio_1.wav')

# ノイズリダクション（最初の0.5秒をノイズプロファイルとして使う例）
reduced = nr.reduce_noise(y=data, sr=rate, y_noise=data[:int(rate*0.5)])

# ノイズ除去後のファイルを保存
sf.write('dataset/audio_files/audio_1_denoised.wav', reduced, rate)