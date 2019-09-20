import pygame
class Button:
    def __init__ (self, rect, func, txt):
        self.border = pygame.Rect(rect)
        self.pressed = False
        self.pressedColor = (200, 200, 200)
        self.unpressedColor = (255, 255, 255)
        self.hoveringColor = (230, 230, 230)
        self.font = pygame.font.Font("classes/number_font.TTF", 15)
        self.hovering = False
        self.func = func
        self.text = txt
    def drawTextCenter (self, x, y, surface, col):
        tfont = self.text.split("\n")
        if len(tfont)>1:
            print("we have a multiline")
            print(tfont)
            surfs = []
            tmaxwidth = 0
            theight = 0
            for i in tfont:
                surfs.append(pygame.font.Font.render(self.font, i, True, col))

        tsurf = pygame.font.Font.render(self.font, self.text, True, col)
        w, h = self.font.size(self.text)
        surface.blit(tsurf, (x-w/2, y-h/2))
    def press(self):
        if self.hovering:
            self.pressed = True
    def depress (self):
        self.pressed = False
    def setpress (self, p):
        self.pressed = p
    def click (self):
        if self.hovering:
            self.func()
    def toggle(self):
        if self.hovering:
            self.pressed = not self.pressed
    def hover (self, mouse):
        # self.hovering = (self.border.collidepoint(mouse))
        self.hovering = mouse[0]>self.border.x and mouse[1]>self.border.y and mouse[1]<self.border.bottom and mouse[0]<self.border.right
    def draw (self, surf):
        c = self.pressedColor if self.pressed and self.hovering else (self.hoveringColor if self.hovering else self.unpressedColor)
        pygame.draw.rect(surf, c, self.border, 0)
        # pygame.draw.rect(surf, (0, 0, 0), self.border, 1)
        self.drawTextCenter(self.border.centerx, self.border.centery, surf, (0, 0, 0))
    def run (self, surf, mouse, md=-1, cl=False):
        if md!=-1:
            self.setpress(md)
        if cl:
            self.click()
        self.hover(mouse)
        self.draw(surf)