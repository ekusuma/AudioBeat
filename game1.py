import pygame
import os
import time
import random

from sprites import Beat, MousePointer
from audio import Song

#OOP Pygame framework from taken from:
#http://blog.lukasperaza.com/getting-started-with-pygame/

class PygameGame(object):
    def __init__(self, times, song, width=1500, height=850,fps=60, 
                    title="My Game"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.beats = pygame.sprite.Group()
        self.prevX = None
        self.prevY = None
        self.maxDist = 200
        self.minDist = 100

        self.songPath = os.path.normpath(song)
        self.times = times
        self.nextBeat = self.times.pop(0)

        self.playSong = True
        #Global delay of 300ms seems the best, as there is a noticeable delay
        #in pygame audio otherwise. 250ms may work as well.
        #Aside: allow user to customize delay?
        self.audioDelay = -0.30
        self.timeElapsed = 0 + self.audioDelay
        pygame.init()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        inGame = True

        self.play()

        while inGame:
            tick = clock.tick(self.fps) / 1000  #Convert to seconds
            self.timeElapsed += tick
            self.timerFired(self.timeElapsed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    inGame = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(event)
            screen.fill((255, 255, 255))
            self.beats.draw(screen)
            pygame.display.flip()
        
        pygame.quit()

    def mousePressed(self, event):
        (x, y) = event.pos
        click = MousePointer(x, y)
        for beat in self.beats:
            if (beat.clock >= 50 and 
                pygame.sprite.collide_circle(beat, click)):
                print("killed")
                beat.kill()

    def timerFired(self, time):
        if self.playSong:
            if time >= self.nextBeat:
                self.addBeat()
                if len(self.times) > 0:
                    self.nextBeat = self.times.pop(0)
                else:
                    self.playSong = False
        for beat in self.beats:
            beat.update()
            if beat.clock >= 60:
                beat.kill()

    def addBeat(self):
        radius = 50
        offsetWidth = self.width - radius
        offsetHeight = self.height - radius
        if (self.prevX == None) and (self.prevY == None):
            x = random.randint(0+radius, self.width-radius)
            y = random.randint(0+radius, self.height-radius)
        else:
            if (self.prevX < self.width // 4):
                xMult = 1
            elif (self.prevX > 3*(self.width // 4)):
                xMult = -1
            else:
                xMult = random.choice([-1, 1])
            if (self.prevY < self.height // 4):
                yMult = 1
            elif (self.prevY > 3*(self.height // 4)):
                yMult = -1
            else:
                yMult = random.choice([-1, 1])
            dx = random.randint(self.minDist, self.maxDist) * xMult
            dy = random.randint(self.minDist, self.maxDist) * yMult
            x = self.prevX + dx
            y = self.prevY + dy
        (self.prevX, self.prevY) = (x, y)
        beat = Beat(x, y, self.width, self.height)
        beat.add(self.beats)

    def play(self):
        pygame.mixer.music.load(self.songPath)
        pygame.mixer.music.play()

# track = Song("Songs/Bad Apple.mp3")
track = Song("Songs/Bonetrousle.ogg")
# track = Song("Songs/Dogsong.ogg")
# track = Song("Songs/Dummy!.ogg")
# track = Song("Songs/MEGALOVANIA.ogg")
# track = Song("Songs/Spear of Justice.ogg")
# track = Song("Songs/P3 FES.ogg")

times = track.getBeatTimes()
path = track.getPath()

game = PygameGame(times, path)

game.run()