import numpy as np
import librosa
import matplotlib.pyplot as plt

duration = 30
x_sr = 200
bpm_min, bpm_max = 60, 240

# 楽曲の信号を読み込む
filepath = "./asset/bgm/tuikyu.mp3"
y, sr = librosa.load(filepath, offset=38, duration=duration, mono=True)

# ビート検出用信号の生成
# リサンプリング & パワー信号の抽出
x = np.abs(librosa.resample(y, sr, x_sr)) ** 2
x_len = len(x)

# 各BPMに対応する複素正弦波行列を生成
M = np.zeros((bpm_max, x_len), dtype=np.complex)
for bpm in range(bpm_min, bpm_max): 
    thete = 2 * np.pi * (bpm/60) * (np.arange(0, x_len) / x_sr)
    M[bpm] = np.exp(-1j * thete)

# 各BPMとのマッチング度合い計算
#（複素正弦波行列とビート検出用信号との内積）
x_bpm = np.abs(np.dot(M, x))

# BPM　を算出
bpm = np.argmax(x_bpm)
print("bpm:",bpm)