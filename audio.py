import librosa
import pygame
import os

class Song(object):
    def __init__(self, path):
        self.path = os.path.normpath(path)
        self.tempo = None
        self.beats = None
        self.times = None
        self.analyze()

    def analyze(self):
        audio_path = self.path
        y, sr = librosa.load(audio_path, sr=None)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        self.tempo = tempo
        self.beats = list(beats)
        self.times = list(librosa.frames_to_time(beats, sr=sr))

    def getTempo(self):
        return self.tempo

    def getBeatFrames(self):
        return self.beats

    def getBeatTimes(self):
        return self.times

    def getPath(self):
        return self.path

class Sound(pygame.mixer.Sound):
    def __init__(self, path):
        self.path = os.path.normpath(path)
        super(Sound, self).__init__(file=self.path)