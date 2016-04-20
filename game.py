import pygame
import os
import random

from sprites import Beat, MousePointer, Text
from audio import Song, Sound
from collections import deque

#OOP Pygame framework adapted from:
#http://blog.lukasperaza.com/getting-started-with-pygame/

class PygameGame(object):
    def __init__(self, times, song, width=1500, height=850,fps=60, 
                    title="My Game"):
        (self.width, self.height) = (width, height)
        self.fps = fps
        self.title = title
        # self.inGame = True
        self.initBeats()

        self.songPath = os.path.normpath(song)
        self.times = times
        self.nextBeat = self.times.pop(0)

        self.combo = 0
        self.score = 0
        self.prevAddition = 0
        self.lastBeatHit = (0, 0)
        self.hits = pygame.sprite.Group()
        self.hitKill = 0.5

        self.inGame = True
        self.playSong = False
        self.PLAYBACK_END = pygame.USEREVENT + 1
        #Global delay of 300ms seems the best, as there is a noticeable delay
        #in pygame audio otherwise. 250ms may work as well.
        #Need to start time a second early because we add a beat a second early.
        self.audioDelay = -1.35
        self.timeElapsed = 0 + self.audioDelay

        pygame.mixer.pre_init(buffer=1024)
        pygame.mixer.init()
        self.initSounds()
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
        self.beatApproach = 1.0
        self.windowWidth = 0.06

        self.goodLate = self.beatApproach + self.windowWidth
        self.badLate = self.goodLate + self.windowWidth
        self.missLate = self.badLate + self.windowWidth
        self.beatKill = self.missLate + self.windowWidth

        self.perfectEarly = self.beatApproach - self.windowWidth
        self.goodEarly = self.perfectEarly - self.windowWidth
        self.badEarly = self.goodEarly - self.windowWidth
        self.missEarly = self.badEarly - self.windowWidth

    def initSounds(self):
        #hit sound from:
        #https://www.freesound.org/people/radiopassiveboy/sounds/219266/
        self.soundHit = Sound("SFX/hit.ogg")
        #mistake sound from:
        #https://www.freesound.org/people/zerolagtime/sounds/49238/
        self.soundMiss = Sound("SFX/miss.ogg")

    def run(self):
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        # self.play()
        pygame.mixer.music.load(self.songPath)

        self.playSong = True

        while self.inGame:
            if self.playSong:
                pygame.mixer.music.set_endevent(self.PLAYBACK_END)
                pygame.mixer.music.play()

            while self.playSong:
                self.songLoop(clock)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.inGame = False

            BLACK = (0, 0, 0)
            self.screen.fill(BLACK)
            pygame.display.flip()

        pygame.font.quit()
        pygame.mixer.quit()
        pygame.quit()

    def songLoop(self, clock):
        #tick_busy_loop is more expensive (more accurate too) than just
        #clock.tick, but this is necessary in a rhythm game.
        tick = clock.tick_busy_loop(self.fps) / 1000 #Convert to seconds
        self.timeElapsed += tick
        self.gameTimerFired(self.timeElapsed, tick)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False
                self.playSong = False
            elif ((event.type == pygame.MOUSEBUTTONDOWN) and 
                                                (event.button == 1)):
                self.beatPressed()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_z or event.key == pygame.K_x):
                    self.beatPressed()
            elif event.type == self.PLAYBACK_END:
                self.playSong = False

        self.songLoopUpdate()

    def songLoopUpdate(self):
        BLACK = (0, 0, 0)
        self.screen.fill(BLACK)
        self.hits.draw(self.screen)
        self.beats.draw(self.screen)
        self.printText()
        pygame.display.flip()

    def beatPressed(self):
        if (len(self.beatQueue) == 0):
            return
        (x, y) = pygame.mouse.get_pos()
        click = MousePointer(x, y)
        beat = self.beatQueue[0]
        if (pygame.sprite.collide_circle(beat, click)):
            mistake = self.addScore(beat.clock, beat)
            if (mistake == None):
                return
            elif mistake:
                self.mistake(beat)
            else:
                self.soundHit.play()
                self.combo += 1
            beat.kill()
            self.beatQueue.popleft()
            self.addHit(beat)

    #Returns True if a mistake is made, None if player clicks early, and 
    #increments score otherwise.
    def addScore(self, time, beat):
        mult = self.getComboMult()
        if (time >= self.missLate):
            return True
        elif (time >= self.badLate):
            addition = self.scoreBad
        elif (time >= self.goodLate):
            addition = self.scoreGood
        elif (time >= self.perfectEarly):
            addition = self.scorePerfect
        elif (time >= self.goodEarly):
            addition = self.scoreGood
        elif (time >= self.badEarly):
            addition = self.scoreBad
        elif (time >= self.missEarly):
            return True
        else:
            return None
        self.score = int(self.score + (addition * mult))
        self.prevAddition = addition
        return False

    def getComboMult(self):
        return (1 + self.combo/25)

    def gameTimerFired(self, time, tick):
        if (time + self.beatApproach) >= self.nextBeat:
            if len(self.times) > 0:
                self.addBeat()
                self.nextBeat = self.times.pop(0)

        for beat in self.beats:
            beat.update(tick)
            if beat.clock >= self.beatKill:
                beat.kill()
                self.beatQueue.remove(beat)
                self.mistake(beat)
        for hit in self.hits:
            hit.update(tick)
            if hit.clock >= self.hitKill:
                hit.kill()

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

    def mistake(self, beat):
        if (self.combo >= 10):
            self.soundMiss.play()
        self.combo = 0
        xColor = (255, 0, 0)
        (x, y) = beat.getPos()
        text = "x"
        size = 100
        missText = Text(self.screen, text, size, x, y, "center", xColor)
        missText.add(self.hits)

    def shuffleColor(self):
        newColor = random.choice(self.colorChoices)
        while (newColor == self.beatColor):
            newColor = random.choice(self.colorChoices)
        self.beatColor = newColor

    def printText(self):
        (width, height) = self.screen.get_size()
        textScore = str(self.score)
        (xScore, yScore) = (width-10, 0)
        scoreSize = 60
        scoreText = Text(self.screen, textScore, scoreSize, xScore, yScore, "ne")
        
        textCombo = str(self.combo) + "x"
        (xCombo, yCombo) = (10, height)
        comboSize = 75
        comboText = Text(self.screen, textCombo, comboSize, xCombo, yCombo, "sw")

    def addHit(self, beat):
        colorPerfect = (125, 200, 255)
        colorGood = (88, 255, 88)
        colorBad = (255, 226, 125)

        (x, y) = beat.getPos()
        text = str(self.prevAddition)
        if (self.prevAddition == self.scorePerfect):
            color = colorPerfect
        elif (self.prevAddition == self.scoreGood):
            color = colorGood
        elif (self.prevAddition == self.scoreBad):
            color = colorBad
        else: return
        size = 50
        hitText = Text(self.screen, text, size, x, y, "center", color)
        hitText.add(self.hits)

# track = Song("Songs/Bad Apple.mp3")
track = Song("Songs/Bonetrousle.ogg")
# track = Song("Songs/Dogsong.ogg")
# track = Song("Songs/Dummy!.ogg")
# track = Song("Songs/MEGALOVANIA.ogg")
# track = Song("Songs/Spear of Justice.ogg")
# track = Song("Songs/P3 FES.ogg")
# track = Song("Songs/Rainbow Road.ogg")

times = track.getBeatTimes()
path = track.getPath()

game = PygameGame(times, path, title="AudioBeat")

game.run()