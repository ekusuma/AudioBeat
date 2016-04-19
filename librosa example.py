import librosa
import time

audio_path = librosa.util.example_audio_file()
# audio_path = "C:\\Users\\Edric\\Documents\\Software\\TP Modules\\test.mp3"

time0 = time.time()
print("loading audio_path...")
y, sr = librosa.load(audio_path, sr=None)
print(audio_path)
time1 = time.time()
load = time1-time0
print("loading audio_path took", load, "seconds")

print("saving y_harmonic and y_percussive...")
time0 = time.time()
# y_harmonic, y_percussive = librosa.effects.hpss(y)
time1 = time.time()
load = time1-time0
print("saving took", load, "seconds")

print("saving tempo...")
time0 = time.time()
# tempo, beats = librosa.beat.beat_track(y=y_percussive, sr=sr)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
time1 = time.time()
load = time1-time0
print("saving tempo took", load, "seconds")

print('Estimated tempo:        %.2f BPM' % tempo)

# print('First 5 beat frames:   ', beats[:5])

# Frame numbers are great and all, but when do those beats occur?
# print('First 5 beat times:    ', librosa.frames_to_time(beats[:5], sr=sr))

# print(beats)
print(librosa.frames_to_time(beats, sr=sr))

# We could also get frame numbers from times by librosa.time_to_frames()