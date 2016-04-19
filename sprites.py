import pygame
#antialiasing
from pygame import gfxdraw
import random

class Beat(pygame.sprite.Sprite):
    #RGB numbers for white
    WHITE = (255, 255, 255)
    def __init__(self, x, y, color, ordinal):
        super(Beat, self).__init__()
        self.clock = 0
        self.radius = 50
        self.rOuter = self.radius * 5
        self.rRing = self.rOuter
        self.dRadius = self.rOuter // 60
        self.outline = 5
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - self.rOuter, self.y - self.rOuter,
                                2 * self.rOuter, 2 * self.rOuter)
        self.image = pygame.Surface((2 * self.rOuter, 2 * self.rOuter),
                                    pygame.SRCALPHA)
        self.image = self.image.convert_alpha()
        self.ord = ordinal
        self.color = color
        self.draw()

    def update(self):
        self.clock += 1
        self.rRing -= self.dRadius
        #Fills in white, with the fourth number being the alpha (transparent).
        self.image.fill((255,255,255,0))
        self.draw()

    def draw(self):
        pygame.draw.circle(self.image, Beat.WHITE, (self.rOuter, self.rOuter),
                        self.rRing, 3)
        pygame.gfxdraw.aacircle(self.image, self.rOuter, self.rOuter, 
                        self.radius, Beat.WHITE)
        pygame.gfxdraw.filled_circle(self.image, self.rOuter, self.rOuter,
                        self.radius, Beat.WHITE)
        pygame.gfxdraw.aacircle(self.image, self.rOuter, self.rOuter, 
                        self.radius-self.outline, self.color)
        pygame.gfxdraw.filled_circle(self.image, self.rOuter, self.rOuter,
                        self.radius-self.outline, self.color)

#Used for collision detection.
class MousePointer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(MousePointer, self).__init__()
        self.radius = 1
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                2 * self.radius, 2 * self.radius)