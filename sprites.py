import pygame
import os
#antialiasing
from pygame import gfxdraw
import random

class Beat(pygame.sprite.Sprite):
    #RGB numbers for white
    WHITE = (255, 255, 255)
    def __init__(self, x, y, color, ordinal):
        super(Beat, self).__init__()
        #Due to timing imprecisions with pygame, a global offset on beats need
        #to be implemented, so self.clock is initialized to 0.1 seconds.
        self.clock = 0.1
        self.radius = 50
        self.rOuter = self.radius * 5
        self.rRing = self.rOuter
        self.ringWidth = 3
        self.dRadius = self.rOuter // 60
        self.outline = 4
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - self.rOuter, self.y - self.rOuter,
                                2 * self.rOuter, 2 * self.rOuter)
        self.image = pygame.Surface((2 * self.rOuter, 2 * self.rOuter),
                                    pygame.SRCALPHA)
        self.image = self.image.convert_alpha()
        self.ord = ordinal
        self.fontSize = 50
        self.color = color
        self.draw()

    def update(self, tick):
        self.clock += tick
        if (self.rRing > self.radius):
            self.rRing -= self.dRadius
        #Fills in white, with the fourth number being the alpha (transparent).
        self.image.fill((255,255,255,0))
        self.draw()

    def draw(self):
        pygame.draw.circle(self.image, Beat.WHITE, (self.rOuter, self.rOuter),
            self.rRing, self.ringWidth)
        radius = 2 * self.radius
        outline = 2 * self.outline
        surface = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA)
        surface = surface.convert_alpha()
        pygame.draw.circle(surface, Beat.WHITE, (radius, radius),
                        radius)
        pygame.draw.circle(surface, self.color, (radius, radius),
                        radius-outline)
        (width, height) = (2 * self.radius, 2 * self.radius)
        surface = pygame.transform.smoothscale(surface, (width, height))
        startPoint = self.rOuter - self.radius
        self.image.blit(surface, (startPoint,startPoint))
        self.drawText()

    def drawText(self):
        font = pygame.font.Font(None, self.fontSize)
        text = font.render(str(self.ord), 1, Beat.WHITE)
        pos = text.get_rect()
        pos.centerx = self.image.get_rect().centerx
        pos.centery = self.image.get_rect().centery
        self.image.blit(text, pos)

    def getPos(self):
        return (self.x, self.y)

#Used for collision detection.
class MousePointer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(MousePointer, self).__init__()
        self.radius = 1
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                2 * self.radius, 2 * self.radius)

class Text(pygame.sprite.Sprite):
    WHITE = (255, 255, 255)
    def __init__(self, surface, text, size, x, y, anchor="nw", 
                                                color=WHITE):
        super(Text, self).__init__()
        (self.x, self.y) = (x, y)
        self.text = text
        self.anchor = anchor
        self.color = color
        self.clock = 0

        #Font downloaded from http://google.com/fonts
        fontType = os.path.normpath("Fonts/Nunito-Regular.ttf")
        self.font = pygame.font.Font(fontType, size)

        (self.width, self.height) = self.font.size(self.text)
        self.initPos()
        self.rect = pygame.Rect(self.rectX, self.rectY, 
                        self.width, self.height)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw()
        self.target = surface
        self.target.blit(self.image, (self.rectX, self.rectY))

    def initPos(self):
        if (self.anchor == "nw"):
            self.rectX = self.x
            self.rectY = self.y
        elif (self.anchor == "ne"):
            self.rectX = self.x - self.width
            self.rectY = self.y
        elif (self.anchor == "sw"):
            self.rectX = self.x
            self.rectY = self.y - self.height
        elif (self.anchor == "se"):
            self.rectX = self.x - self.width
            self.rectY = self.y - self.height
        elif (self.anchor == "center"):
            self.rectX = self.x - self.width//2
            self.rectY = self.y - self.height//2

    def draw(self):
        text = self.font.render(self.text, 1, self.color)
        self.image.blit(text, (0, 0))

    def update(self, tick=0):
        self.clock += tick
        self.draw()
        self.target.blit(self.image, (self.rectX, self.rectY))

#Button uses an image for the visuals.
class Button(pygame.sprite.Sprite):
    BLUE = (0, 102, 255)
    WHITE = (0, 0, 0)
    def __init__(self, path, x, y, width, height):
        super(Button, self).__init__()
        (self.x, self.y) = (x, y)
        (self.width, self.height) = (width, height)
        self.image = pygame.image.load(os.path.normpath(path))
        self.image = self.image.convert_alpha()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)