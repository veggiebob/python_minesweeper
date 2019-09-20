import random

import pygame
from pygame.locals import *
pygame.init()
class Tile:
    def __init__ (self):
        self.flagged = False
        self.uncovered = False # init
        self.number = None # init
        self.hasNumber = False # init
        self.mine = None # init
        self.font = pygame.font.Font("classes/number_font.TTF", 20)
        self.vfont = pygame.font.Font("classes/number_font.TTF", 15)
        # self.flagImg = pygame.image.load("classes/flag_asset.png")
        self.colors = {}
        self.colors["BOARD_BACK"] = (230, 230, 255)
        self.colors["TILE_BACK"] = (128, 128, 128)
        self.colors["TILE_POP"] = (180, 180, 180)
        self.colors["TEXT_COLORS"] = (
            (0, 0, 255),
            (0, 255, 0),
            (255, 0, 0),
            (0, 255, 255),
            (0, 100, 255),
            (0, 0, 150),
            (100, 100, 255),
            (255, 100, 0),
            (150, 50, 0),

            (75, 175, 255),
            (0, 0, 150),
            (100, 255, 100),
            (150, 255, 150),
            (0, 0, 0),
            (255, 255, 255),
            (50, 50, 50),
            (100, 100, 100),
            (150, 150, 150),

            (200, 200, 200),
            (250, 250, 250),
            (255, 0, 255),
            (255, 50, 255),
            (255, 100, 255),
            (255, 150, 255),
            (255, 200, 255),
            (150, 0, 0),
        )
    def __str__ (self):
        return "uncovered:%s, mine:%s, has number:%s, number:%s, flagged:%s"%(self.uncovered, self.mine, self.hasNumber, self.number, self.flagged)
    def rand_init (self):
        self.uncovered = bool(random.randint(0, 1))
        self.flagged = bool(random.randint(0, 1))
        self.mine = bool(random.randint(0, 1))
        self.number = random.randint(0, 9)
        self.hasNumber = True

    def changeFontSize (self, ns):
        self.font = pygame.font.Font("classes/number_font.TTF", int(ns))
    def changeVFontSize (self, ns):
        self.vfont = pygame.font.Font("classes/number_font.TTF", int(ns))
    def getNumber (self):
        if not self.number is None:
            self.hasNumber = True
        return -1 if self.number == None or self.mine else self.number
    def getMine (self):
        return self.mine
    def getColor (self):
        n = self.getNumber()
        if n<0:
            return (0, 0, 0)
        c = self.colors["TEXT_COLORS"][n]
        return c
    def drawTextCenter (self, x, y, surface, col):
        n = "#" if self.number is None else "%d" % self.number
        if self.number==0: return
        tsurf = pygame.font.Font.render(self.font, n, True, col)
        w, h = self.font.size(n)
        surface.blit(tsurf, (x-w/2, y-h/2))

    def drawVTextCenter(self, x, y, surface, col):
        n = "#" if self.number is None else "%d" % self.number
        if self.number == 0: return
        tsurf = pygame.font.Font.render(self.vfont, n, True, col)
        w, h = self.vfont.size(n)
        surface.blit(tsurf, (x - w / 2, y - h / 2))

    def drawTile(self, surf, x, y, s):
        pygame.draw.rect(surf, self.colors["TILE_BACK"], (x, y, s, s), 0)
        if not self.uncovered:
            b = s * 0.03
            pygame.draw.rect(surf, self.colors["TILE_POP"], (x + b, y + b, s - b * 2, s - b * 2), 0)
        else:
            self.changeFontSize(s)
            self.drawTextCenter(x + s / 2, y + s / 2, surf, self.getColor())
