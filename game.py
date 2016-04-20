import pygame
import os
import time
import random

from sprites import Beat, MousePointer
from audio import Song
from collections import deque

#OOP Pygame framework adapted from:
#http://blog.lukasperaza.com/getting-started-with-pygame/

class PygameGame(object):
    def __init__(self, times, song, width=1500, height=850,fps=60, 
                    title="My Game"):
        (self.width, self.height) = (width, height)
        self.fps = fps
        self.title = title
        self.initBeats()

        self.songPath = os.path.normpath(song)
        self.times = times
        self.nextBeat = self.times.pop(0)

        self.combo = 0
        self.score = 0

        self.playSong = True
        #Global delay of 300ms seems the best, as there is a noticeable delay
        #in pygame audio otherwise. 250ms may work as well.
        #Aside: allow user to customize delay?
        #Need to start time a second early because we add a beat a second early.
        self.audioDelay = -1.30
        self.timeElapsed = 0 + self.audioDelay
        pygame.init()
        pygame.font.init()

    def initBeats(self):
        self.r = 50
        self.beats = pygame.sprite.Group()
        self.beatQueue = deque()
        #Choices of color for beats: Red, Blue, Green, Orange
        self.colorChoices = [(255,0,0),(0,0,255),(24,226,24),(247,162,15)]
        self.beatColor = (0, 0, 0)
        self.shuffleColor()
        self.prevX = None
        self.prevY = None
        self.maxDist = 200
        self.minDist = 100
        self.beatNum = 1
        self.beatNumMax = 4
        self.initBeatTiming()

        self.scoreBad = 50
        self.scoreGood = 100
        self.scorePerfect = 300

    def initBeatTiming(self):
        self.beatApproach = 60
        self.windowWidth = 5

        self.goodLate = self.beatApproach + self.windowWidth
        self.badLate = self.goodLate + self.windowWidth
        self.missLate = self.badLate + self.windowWidth
        self.beatKill = self.missLate + self.windowWidth

        self.perfectEarly = self.beatApproach - self.windowWidth
        self.goodEarly = self.perfectEarly - self.windowWidth
        self.badEarly = self.goodEarly - self.windowWidth
        self.missEarly = self.badEarly - self.windowWidth

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        inGame = True

        self.play()

        while inGame:
            #tick_busy_loop is more expensive (more accurate too) than just
            #clock.tick, but this is necessary in a rhythm game.
            tick = clock.tick_busy_loop(self.fps) / 1000  #Convert to seconds
            self.timeElapsed += tick
            self.timerFired(self.timeElapsed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    inGame = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed()
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_z or event.key == pygame.K_x):
                        self.mousePressed()
            BLACK = (0, 0, 0)
            screen.fill(BLACK)
            self.beats.draw(screen)
            pygame.display.flip()
        
        pygame.font.quit()
        pygame.quit()

    def mousePressed(self):
        (x, y) = pygame.mouse.get_pos()
        click = MousePointer(x, y)
        beat = self.beatQueue[0]
        if (pygame.sprite.collide_circle(beat, click)):
            print(beat.clock, end="")
            if (beat.clock >= self.missLate):
                self.mistake()
                print("you fucked up")
            elif (beat.clock >= self.badLate):
                self.score += self.scoreBad
                print("bad")
            elif (beat.clock >= self.goodLate):
                self.score += self.scoreGood
                print("good")
            elif (beat.clock >= self.perfectEarly):
                self.score += self.scorePerfect
                print("perfect")
            elif (beat.clock >= self.goodEarly):
                self.score += self.scoreGood
                print("good")
            elif (beat.clock >= self.badEarly):
                self.score += self.scoreBad
                print("bad")
            elif (beat.clock >= self.missEarly):
                self.mistake()
                print("you fucked up")
            else:
                return
            beat.kill()
            self.beatQueue.popleft()

    def timerFired(self, time):
        if self.playSong:
            if (time + 1) >= self.nextBeat:
                self.addBeat()
                if len(self.times) > 0:
                    self.nextBeat = self.times.pop(0)
                else:
                    self.playSong = False
        for beat in self.beats:
            beat.update()
            if beat.clock >= self.beatKill:
                beat.kill()
                self.beatQueue.remove(beat)
                self.mistake()

    def addBeat(self):
        (offsetW, offsetH) = (self.width-self.r, self.height-self.r)
        if (self.prevX == None) and (self.prevY == None):
            x = random.randint(0+self.r, offsetW)
            y = random.randint(0+self.r, offsetH)
        else:
            if (self.prevX < self.width // 4): xMult = 1
            elif (self.prevX > 3*(self.width // 4)): xMult = -1
            else: xMult = random.choice([-1, 1])

            if (self.prevY < self.height // 4): yMult = 1
            elif (self.prevY > 3*(self.height // 4)): yMult = -1
            else: yMult = random.choice([-1, 1])

            dx = random.randint(self.minDist, self.maxDist) * xMult
            dy = random.randint(self.minDist, self.maxDist) * yMult
            (x, y) = (self.prevX + dx, self.prevY + dy)
        (self.prevX, self.prevY) = (x, y)
        beat = Beat(x, y, self.beatColor, self.beatNum)
        beat.add(self.beats)
        self.beatQueue.append(beat)
        self.updateOrdinal()

    def updateOrdinal(self):
        self.beatNum += 1
        if self.beatNum > self.beatNumMax:
            self.beatNum = 1
            self.shuffleColor()

    def play(self):
        pygame.mixer.music.load(self.songPath)
        pygame.mixer.music.play()

    def mistake(self):
        pass

    def shuffleColor(self):
        newColor = random.choice(self.colorChoices)
        while (newColor == self.beatColor):
            newColor = random.choice(self.colorChoices)
        self.beatColor = newColor

track = Song("Songs/Bad Apple.mp3")
# track = Song("Songs/Bonetrousle.ogg")
# track = Song("Songs/Dogsong.ogg")
# track = Song("Songs/Dummy!.ogg")
# track = Song("Songs/MEGALOVANIA.ogg")
# track = Song("Songs/Spear of Justice.ogg")
# track = Song("Songs/P3 FES.ogg")
# track = Song("Songs/Rainbow Road.ogg")

times = track.getBeatTimes()
path = track.getPath()

game = PygameGame(times, path)

game.run()