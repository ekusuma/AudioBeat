import pygame
import os
import random
import time

from sprites import Beat, MousePointer, Text, StText, Button
from audio import Song, Sound
from collections import deque

#OOP Pygame framework adapted from:
#http://blog.lukasperaza.com/getting-started-with-pygame/

#Centers the window, a function that is built in to os module.
#Solution from: http://goo.gl/PJVbeN
os.environ['SDL_VIDEO_CENTERED'] = '1'

###############################################################################
########################### Init code starts here #############################
###############################################################################
class PygameGame(object):
    def __init__(self, width=1500, height=850,fps=60, 
                    title="My Game"):
        (self.width, self.height) = (width, height)
        self.fps = fps
        self.title = title
        iconPath = os.path.normpath("Pictures/icon.png")
        self.icon = pygame.image.load(iconPath)

        self.initModes()
        self.initBeats()
        self.initTracking()

        #Create an event that will trigger when the song finishes.
        self.PLAYBACK_END = pygame.USEREVENT + 1

        #Global delay of 450ms seems the best, as there is a noticeable delay
        #in pygame audio otherwise.
        #Need to start time a second early because we add a beat a second early.
        self.audioDelay = -1.45
        self.timeElapsed = 0 + self.audioDelay
        self.endDelay = 2.0
        self.countdown = None

        #Preinitializing with this buffer value helps with audio lag.
        pygame.mixer.pre_init(buffer=1024)
        pygame.mixer.init()
        self.initSounds()
        pygame.display.set_icon(self.icon)
        pygame.init()
        pygame.font.init()

    def initTracking(self):
        self.combo = 0
        self.maxCombo = 0
        self.score = 0
        self.prevAddition = 0
        self.lastBeatHit = (0, 0)
        self.hits = pygame.sprite.Group()
        self.hitKill = 0.5

    def initModes(self):
        self.inGame = True
        self.inMenu = True
        self.songSelect = False
        self.instructions = False
        self.playSong = False
        self.scoreScreen = False
        self.paused = False

    def initMenu(self):
        #Menu picture from: https://goo.gl/bwppX2
        path = "Pictures/menu.png"
        path = os.path.normpath(path)
        self.menu = pygame.image.load(path)
        self.menu.convert()
        self.menuButtons = pygame.sprite.Group()
        self.initMenuButtons()

        path = "Pictures/loading.png"
        path = os.path.normpath(path)
        self.loadScreen = pygame.image.load(path)
        self.loadScreen.convert()

        path = "Pictures/paused.png"
        path = os.path.normpath(path)
        self.pauseScreen = pygame.image.load(path)
        self.pauseScreen.convert()

    def initMenuButtons(self):
        #All buttons and the logo were drawn by Edric Kusuma.
        (logoX, logoY) = (50, 275)
        (logoW, logoH) = (700, 300)
        logoPath = "Pictures/Logo.png"
        logo = Button(logoPath, logoX, logoY, logoW, logoH)

        (playX, playY) = (850, 210)
        (playW, playH) = (500, 200)
        playPath = "Pictures/Buttons/Play.png"
        self.playButton = Button(playPath, playX, playY, playW, playH)

        (howToX, howToY) = (850, 460)
        (howToW, howToH) = (500, 150)
        howToPath = "Pictures/Buttons/HowTo.png"
        self.howToButton = Button(howToPath, howToX, howToY, howToW, howToH)

        logo.add(self.menuButtons)
        self.playButton.add(self.menuButtons)
        self.howToButton.add(self.menuButtons)

    def initMenuMusic(self):
        #Menu music taken from: http://www.newgrounds.com/audio/listen/438759
        menuMusicPath = "SFX/menu.ogg"
        pygame.mixer.music.load(menuMusicPath)
        #Repeat menu music indefinitely.
        pygame.mixer.music.play(loops=-1)

    def initBeats(self):
        self.r = 50
        self.beats = pygame.sprite.Group()

        #Having a separate queue allows for indexing (so we can pull the most
        #recent beat)
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
        self.initScoring()

    def initScoring(self):
        self.scoreBad = 50
        self.scoreGood = 100
        self.scorePerfect = 300

        self.misses = 0
        self.bads = 0
        self.goods = 0
        self.perfects = 0

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

    def initSong(self, path):
        self.songPath = os.path.normpath(self.songPath)

        startTime = time.time()
        self.song = Song(self.songPath)
        self.times = self.song.getBeatTimes()
        self.nextBeat = self.times.pop(0)
        pygame.mixer.music.load(self.songPath)
        endTime = time.time()
        
        loadTime = abs(endTime - startTime)
        self.timeElapsed -= loadTime

    def initSounds(self):
        #hit sound from:
        #https://www.freesound.org/people/radiopassiveboy/sounds/219266/
        self.soundHit = Sound("SFX/hit.ogg")
        #mistake sound from:
        #https://www.freesound.org/people/zerolagtime/sounds/49238/
        self.soundMiss = Sound("SFX/miss.ogg")
        
    def initHowTo(self):
        self.howToItems = pygame.sprite.Group()

        (x, y) = (250, 100)
        (width, height) = (1200, 700)
        path = "Pictures/HowTo.png"
        howToPlay = Button(path, x, y, width, height)

        (x, y) = (260, 50)
        (width, height) = (600, 50)
        path = "Pictures/HowToHeader.png"
        howToHeader = Button(path, x, y, width, height)

        (x, y) = (50, 50)
        (width, height) = (175, 750)
        path = "Pictures/Buttons/Back.png"
        self.toMenu = Button(path, x, y, width, height)

        howToPlay.add(self.howToItems)
        howToHeader.add(self.howToItems)
        self.toMenu.add(self.howToItems)

    def initSongSelect(self):
        self.songSelItems = pygame.sprite.Group()
        spacing = 5 + 120

        (x, y0) = (950, 50)
        (width, height) = (500, 120)
        applePath = "Pictures/Song Select/badAppleBox.png"
        self.badAppleBox = Button(applePath, x, y0, width, height)
        self.badAppleBox.add(self.songSelItems)

        y1 = y0 + spacing
        bonePath = "Pictures/Song Select/bonetrousleBox.png"
        self.bonetrousleBox = Button(bonePath, x, y1, width, height)
        self.bonetrousleBox.add(self.songSelItems)

        y2 = y1 + spacing
        dummyPath = "Pictures/Song Select/dummyBox.png"
        self.dummyBox = Button(dummyPath, x, y2, width, height)
        self.dummyBox.add(self.songSelItems)

        self.initSongSelect2(x, width, height, y2, spacing)

    def initSongSelect2(self, x, width, height, y2, spacing):
        y3 = y2 + spacing
        megaPath = "Pictures/Song Select/megalovaniaBox.png"
        self.megalovaniaBox = Button(megaPath, x, y3, width, height)
        self.megalovaniaBox.add(self.songSelItems)

        y4 = y3 + spacing
        rhinePath = "Pictures/Song Select/rhinestoneBox.png"
        self.rhinestoneBox = Button(rhinePath, x, y4, width, height)
        self.rhinestoneBox.add(self.songSelItems)

        y5 = y4 + spacing
        goodPath = "Pictures/Song Select/feelgoodBox.png"
        self.feelgoodBox = Button(goodPath, x, y5, width, height)
        self.feelgoodBox.add(self.songSelItems)

        self.backSmallGrp = pygame.sprite.GroupSingle()
        (width, height) = (175, 175)
        (x, y) = (50, self.height - 50 - height)
        path = "Pictures/Buttons/BackSmall.png"
        self.backSmall = Button(path, x, y, width, height)
        self.backSmall.add(self.backSmallGrp)

    def run(self):
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.initMenu()
        self.initHowTo()
        self.initSongSelect()

        while self.inGame:
            self.mainLoop(clock)

        pygame.font.quit()
        pygame.mixer.quit()
        pygame.quit()

###############################################################################
########################### Loop code starts here #############################
###############################################################################
    def mainLoop(self, clock):
        if not pygame.mixer.music.get_busy():
                self.initMenuMusic()

        while self.inMenu:
            self.menuLoop(clock)

        while self.instructions:
            self.instructionLoop(clock)

        while self.songSelect:
            self.songSelectLoop(clock)

        if self.playSong:
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(self.PLAYBACK_END)

        while self.playSong:
            self.songLoop(clock)

        while self.scoreScreen:
            self.scoreScreenLoop(clock)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False

        self.mainLoopUpdate()

    def menuLoop(self, clock):
        clock.tick(self.fps)

        self.screen.blit(self.menu, (0, 0))
        self.menuButtons.draw(self.screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False
                self.inMenu = False
            elif ((event.type == pygame.MOUSEBUTTONDOWN) and 
                    (event.button == 1)):
                self.mousePressed()

    def instructionLoop(self, clock):
        clock.tick(self.fps)

        self.screen.blit(self.menu, (0, 0))
        self.howToItems.draw(self.screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False
                self.instructions = False
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    self.soundMiss.play()
                    self.instructions = False
                    self.inMenu = True
            elif ((event.type == pygame.MOUSEBUTTONDOWN) and
                    (event.button == 1)):
                self.mousePressed()

    def songSelectLoop(self, clock):
        clock.tick(self.fps)

        self.screen.blit(self.menu, (0, 0))
        self.backSmallGrp.draw(self.screen)
        self.songSelItems.draw(self.screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False
                self.songSelect = False
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    self.soundMiss.play()
                    self.songSelect = False
                    self.inMenu = True
            elif ((event.type == pygame.MOUSEBUTTONDOWN) and
                    (event.button == 1)):
                self.mousePressed()

    def songLoop(self, clock):
        #tick_busy_loop is more expensive (more accurate too) than just
        #clock.tick, but this is necessary in a rhythm game.
        tick = clock.tick_busy_loop(self.fps) / 1000 #Convert to seconds
        if not self.paused:
            pygame.mixer.music.unpause()
            self.timeElapsed += tick
            self.gameTimerFired(self.timeElapsed, tick)

        for event in pygame.event.get():
            self.actEvent(event)

        if self.paused:
            pygame.mixer.music.pause()

        if self.countdown != None:
            self.countdown -= tick
            if self.countdown <= 0:
                self.playSong = False
                self.scoreScreen = True

        self.songLoopUpdate()

    def scoreScreenLoop(self, clock):
        clock.tick(self.fps)

        if not pygame.mixer.music.get_busy():
                self.initMenuMusic()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.inGame = False
                self.scoreScreen = False
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    self.soundMiss.play()
                    self.scoreScreen = False
                    self.songSelect = True
                    self.reset()
            elif ((event.type == pygame.MOUSEBUTTONDOWN) and
                    (event.button == 1)):
                self.mousePressed()

        self.screen.blit(self.menu, (0, 0))
        self.scoreItems.draw(self.screen)
        self.printScoreText()
        pygame.display.flip()

    def mainLoopUpdate(self):
        BLACK = (0, 0, 0)
        self.screen.fill(BLACK)
        pygame.display.flip()

    def songLoopUpdate(self):
        if not self.paused:
            BLACK = (0, 0, 0)
            self.screen.fill(BLACK)
            self.printText()
            self.hits.draw(self.screen)
            self.beats.draw(self.screen)
            if self.countdown != None:
                fadeOut = pygame.Surface((self.width, self.height))
                BLACK = (0, 0, 0)
                fadeOut.fill(BLACK)
                alpha = int((1 - self.countdown/self.endDelay) * 255)
                alpha = max(alpha, 0)
                fadeOut.set_alpha(alpha)
                self.screen.blit(fadeOut, (0,0))
        if self.paused:
            self.screen.blit(self.pauseScreen, (0,0))

        pygame.display.flip()

    def actEvent(self, event):
        if event.type == pygame.QUIT:
            self.inGame = False
            self.playSong = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.paused = not self.paused
            if self.paused:
                if event.key == pygame.K_r:
                    self.reset()
                    self.songSelect = True
                    return
            elif not self.paused:
                if (event.key == pygame.K_z or event.key == pygame.K_x):
                    self.beatPressed()
        if not self.paused:
            if event.type == pygame.MOUSEBUTTONDOWN: self.beatPressed()
            elif event.type == self.PLAYBACK_END:
                if (self.combo > self.maxCombo): self.maxCombo = self.combo
                self.initScoreScreen()
                self.countdown = self.endDelay

    def mousePressed(self):
        (x, y) = pygame.mouse.get_pos()
        click = MousePointer(x, y)

        if self.inMenu:
            self.checkMenuCollision(click)
        elif self.instructions:
            self.checkHowToCollision(click)
        elif self.songSelect:
            self.checkSongSelCollision(click)
        elif self.scoreScreen:
            self.checkScoreCollision(click)

    def checkMenuCollision(self, click):
        if pygame.sprite.collide_rect(self.playButton, click):
            self.soundHit.play()
            self.songSelect = True
            self.inMenu = False
        elif pygame.sprite.collide_rect(self.howToButton, click):
            self.soundHit.play()
            self.instructions = True
            self.inMenu = False

    def checkHowToCollision(self, click):
        if pygame.sprite.collide_rect(self.toMenu, click):
            self.soundMiss.play()
            self.instructions = False
            self.inMenu = True

    def checkSongSelCollision(self, click):
        if pygame.sprite.collide_rect(self.badAppleBox, click):
            self.songPath = "Songs/Bad Apple.mp3"
        elif pygame.sprite.collide_rect(self.bonetrousleBox, click):
            self.songPath = "Songs/Bonetrousle.ogg"
        elif pygame.sprite.collide_rect(self.dummyBox, click):
            self.songPath = "Songs/Dummy!.ogg"
        elif pygame.sprite.collide_rect(self.megalovaniaBox, click):
            self.songPath = "Songs/MEGALOVANIA.ogg"
        elif pygame.sprite.collide_rect(self.rhinestoneBox, click):
            self.songPath = "Songs/Rhinestone Eyes.ogg"
        elif pygame.sprite.collide_rect(self.feelgoodBox, click):
            self.songPath = "Songs/Feel Good Inc.ogg"

        if pygame.sprite.collide_rect(self.backSmall, click):
            self.soundMiss.play()
            self.songSelect = False
            self.inMenu = True

        if pygame.sprite.spritecollideany(click, self.songSelItems):
            self.soundHit.play()
            self.play()

    def checkScoreCollision(self, click):
        if pygame.sprite.collide_rect(self.backScore, click):
            self.soundMiss.play()
            self.scoreScreen = False
            self.songSelect = True
            self.reset()

    def initScoreScreen(self):
        self.scoreItems = pygame.sprite.Group()

        (x, y) = (50, 50)
        (width, height) = (1400, 650)
        path = "Pictures/Score.png"
        howToPlay = Button(path, x, y, width, height)

        (x, y) = (50, 720)
        (width, height) = (1400, 80)
        path = "Pictures/Buttons/BackScore.png"
        self.backScore = Button(path, x, y, width, height)

        howToPlay.add(self.scoreItems)
        self.backScore.add(self.scoreItems)

    def printScoreText(self):
        (width, height) = self.screen.get_size()

        textScore = str(self.score)
        (xScore, yScore) = (1390, 90)
        scoreSize = 70
        scoreText = StText(self.screen, textScore, scoreSize, xScore, yScore, "ne")
        
        textCombo = str(self.maxCombo) + "x"
        (xCombo, yCombo) = (110, 240)
        comboSize = 80
        comboText = StText(self.screen, textCombo, comboSize, xCombo, yCombo)

        self.printTimingText()

    def printTimingText(self):
        textScore = str(self.perfects)
        (xScore, yScore) = (620, 445)
        scoreSize = 50
        scoreText = StText(self.screen, textScore, scoreSize, xScore, yScore)

        textScore = str(self.goods)
        (xScore, yScore) = (1190, 445)
        scoreSize = 50
        scoreText = StText(self.screen, textScore, scoreSize, xScore, yScore)

        textScore = str(self.bads)
        (xScore, yScore) = (620, 540)
        scoreSize = 50
        scoreText = StText(self.screen, textScore, scoreSize, xScore, yScore)

        textScore = str(self.misses)
        (xScore, yScore) = (1190, 540)
        scoreSize = 50
        scoreText = StText(self.screen, textScore, scoreSize, xScore, yScore)

    def play(self):
        self.screen.blit(self.loadScreen, (0, 0))
        pygame.display.flip()

        pygame.mixer.music.stop()
        self.initSong(self.songPath)
        self.songSelect = False
        self.playSong = True

    def reset(self):
        pygame.mixer.music.stop()

        self.countdown = None
        self.playSong = False
        self.paused = False

        self.combo = 0
        self.maxCombo = 0
        self.score = 0
        self.prevAddition = 0
        self.lastBeatHit = (0, 0)
        self.hits = pygame.sprite.Group()
        self.timeElapsed = 0 + self.audioDelay
        self.beats = pygame.sprite.Group()
        self.beatQueue = deque()
        self.beatNum = 1
        self.initScoring()

        pygame.mixer.music.set_endevent()


###############################################################################
########################### Game code starts here #############################
###############################################################################
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
            beat.dying()
            self.beatQueue.popleft()
            self.addHit(beat)

    #Returns True if a mistake is made, None if player clicks early, and 
    #increments score otherwise.
    def addScore(self, time, beat):
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

        self.scoreTrack(addition)

        return False

    def scoreTrack(self, addition):
        mult = self.getComboMult()
        self.score = int(self.score + (addition * mult))
        self.prevAddition = addition

        if (addition == self.scoreBad):
            self.bads += 1
        elif (addition == self.scoreGood):
            self.goods += 1
        elif (addition == self.scorePerfect):
            self.perfects += 1

    #Based off how osu! calculates this, taken from: https://osu.ppy.sh/wiki/Score
    def getComboMult(self):
        return (1 + self.combo/25)

    def gameTimerFired(self, time, tick):
        if (time + self.beatApproach) >= self.nextBeat:
            if len(self.times) > 0:
                self.addBeat()
                self.nextBeat = self.times.pop(0)

        for beat in self.beats:
            beat.update(tick)
            if ((beat.killClock == None) and (beat.clock >= self.beatKill)):
                beat.dying()
                self.beatQueue.remove(beat)
                self.mistake(beat)
        for hit in self.hits:
            hit.update(tick)
            if ((hit.killClock == None) and (hit.clock >= self.hitKill)):
                hit.dying()

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

    def mistake(self, beat):
        if (self.combo > self.maxCombo): self.maxCombo = self.combo
        if (self.combo >= 10):
            self.soundMiss.play()

        self.combo = 0

        xColor = (255, 0, 0)
        (x, y) = beat.getPos()
        text = "x"
        size = 100
        missText = Text(self.screen, text, size, x, y, "center", xColor)
        missText.add(self.hits)

        self.misses += 1

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
        scoreText = Text(self.screen, textScore, scoreSize, xScore, yScore,"ne")
        
        textCombo = str(self.combo) + "x"
        (xCombo, yCombo) = (10, height)
        comboSize = 75
        comboText = Text(self.screen, textCombo, comboSize, xCombo, yCombo,"sw")

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


taglines = ["Tap to the Beat!", "Just Beat it!", "Tap or die!",
            "Play your own songs!", "WUBWUBWUBWUBWUBWUB",
            "Randomized taglines!", "Algo-rhythmic!"]

title = "AudioBeat" + " - " + random.choice(taglines)

game = PygameGame(title=title)

game.run()