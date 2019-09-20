import pygame, sys, time
from pygame.locals import *
from classes.board import Board3D
from classes.button import Button

pygame.init()

#formatting / layout control
WIDTH = 850
HEIGHT = 400
DIVIDER = 450
TOOLBAR_WIDTH = 50
ISO_WIDTH = DIVIDER-TOOLBAR_WIDTH
SLICE_WIDTH = WIDTH-DIVIDER

SQUARE_DIM = 5
BOARD_WIDTH = SQUARE_DIM
BOARD_HEIGHT = SQUARE_DIM
BOARD_DEPTH = SQUARE_DIM
mainBoard = Board3D(BOARD_DEPTH, BOARD_WIDTH, BOARD_HEIGHT)

# initialize some things
mainBoard.init() # initializes the board; no numbers generated (blank board)
def constrain (v, mi, mx):
    return min(max(v, mi), mx)

def alert (message):
    global frozen
    global warnButton
    global mousedown, click
    frozen = True
    click = False
    mousedown = False
    warnButton.text = message
def unfreeze ():
    global frozen
    global mousedown
    mousedown = False
    if mainBoard.won:
        reset()
    if mainBoard.lost:
        mainBoard.okLost = True
    frozen = False

def printTest ():
    print("test button ran")

def help ():
    alert("controls:\narrow up/down: change layer\nleft click to uncover\nright click to flag\ndrag to rotate")
def reset ():
    print("reset the board")
    global mainBoard
    global current_layer
    mainBoard = Board3D(BOARD_DEPTH, BOARD_WIDTH, BOARD_HEIGHT)
    current_layer = 0


def changeSize (ns):
    global BOARD_DEPTH
    global BOARD_WIDTH
    global BOARD_HEIGHT
    BOARD_DEPTH += ns
    BOARD_WIDTH += ns
    BOARD_HEIGHT += ns
    BOARD_DEPTH = constrain(BOARD_DEPTH, 1, 100)
    BOARD_WIDTH = constrain(BOARD_WIDTH, 1, 100)
    BOARD_HEIGHT = constrain(BOARD_HEIGHT, 1, 100)
    reset()

def increaseSize ():
    print("increasing the size")
    changeSize(1)

def decreaseSize ():
    print("decreasing the size")
    if (max(max(BOARD_DEPTH, BOARD_WIDTH), BOARD_HEIGHT)>2):
        changeSize(-1)

def flat ():
    global BOARD_DEPTH
    BOARD_DEPTH = 1
    reset()

def toCube ():
    global BOARD_DEPTH
    global BOARD_WIDTH
    global BOARD_HEIGHT
    dim = max(max(BOARD_DEPTH, BOARD_HEIGHT), BOARD_WIDTH)
    BOARD_DEPTH = dim
    BOARD_HEIGHT = dim
    BOARD_WIDTH = dim

def changeDensity (n):
    global MINE_DENSITY
    MINE_DENSITY += n
def decreaseDensity ():
    global MINE_DENSITY
    if MINE_DENSITY > 0.03:
        changeDensity(-0.015)
def increaseDensity ():
    global MINE_DENSITY
    changeDensity(0.015)
    if MINE_DENSITY>=1.0:
        MINE_DENSITY = 1.0

halfb = TOOLBAR_WIDTH / 2
fullb = TOOLBAR_WIDTH + 0
buttons = [
    # [ text, function, height ]
    ["test", printTest, fullb],
    ["Help", help, fullb],
    ["Reset", reset, fullb],
    ["size ^", increaseSize, halfb],
    ["size v", decreaseSize, halfb],
    ["flat", flat, halfb],
    ["to cube", toCube, halfb],
    ["density ^", increaseDensity, halfb]
]
buttonobj = []
buttonMargin = 2
buttonY = buttonMargin+0
for b in buttons:
    buttonobj.append(Button((buttonMargin, buttonY, TOOLBAR_WIDTH-buttonMargin*2, b[2]), b[1], b[0]))
    buttonY += b[2] + buttonMargin

# game variables
gameClock = pygame.time.Clock()
FPS = 60
FRAME = 0
MINE_DENSITY = 0.1 / 3
mouse = [0, 0]
dragSensitivity = 1/50
PI = 3.1415926535
current_layer = 0
click = False
button = -1
mousedown = False
gameover = False
hovertile = [-1, -1, -1]
zoom = 1.0
frozen = False
warnButton = Button((WIDTH/4, HEIGHT/4, WIDTH/2, HEIGHT/2), unfreeze, "no error?")

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
SLICEMAP = pygame.Surface((SLICE_WIDTH, HEIGHT))
ISOMAP = pygame.Surface((ISO_WIDTH, HEIGHT))
TOOLBAR = pygame.Surface((TOOLBAR_WIDTH, HEIGHT))
DISPLAYSURF.fill((0, 0, 0))
TOOLBAR.fill((255, 200, 200))

def updateSliceDisplay ():
    SLICEMAP.fill((100, 100, 255))
    hitTile = mainBoard.drawSlice(current_layer, SLICEMAP, (0, 0, SLICE_WIDTH, HEIGHT), [mouse[0]-DIVIDER, mouse[1]])
    global hovertile
    hovertile = hitTile[0]
    if hitTile[2] and click and mouse[0]>DIVIDER:
        mainBoard.click(hitTile[0], MINE_DENSITY) if button == 0 else mainBoard.flag(hitTile[0])
    DISPLAYSURF.blit(SLICEMAP, (DIVIDER, 0))
def updateIsoDisplay ():
    global hovertile
    ISOMAP.fill((128, 128, 128))
    ISOMAP.blit(mainBoard.draw3D(SLICE_WIDTH, HEIGHT, hovertile, current_layer, zoom), (0, 0))
    DISPLAYSURF.blit(ISOMAP, (0, 0))
def updateToolbar ():
    m = [mouse[0]-ISO_WIDTH, mouse[1]]
    inToolbar = 0<=m[0]<=TOOLBAR_WIDTH and 0<=m[1]<=HEIGHT
    for b in buttonobj:
        b.run(TOOLBAR, m, mousedown and inToolbar, click)
    DISPLAYSURF.blit(TOOLBAR, (ISO_WIDTH, 0))
while True:
    mrel = [0, 0]
    button = -1
    click = False
    for event in pygame.event.get():
        if event.type == QUIT or gameover:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mrel = event.rel
            button = 0 if event.buttons[0]>0 else (1 if event.buttons[1]>0 else (2 if event.buttons[2]>0 else -1))
            mouse = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            button = event.button-1
            mouse = event.pos
            click = True
            mousedown = True
        elif event.type == MOUSEBUTTONUP:
            mousedown = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                current_layer += 1
            elif event.key == K_DOWN:
                current_layer -= 1
            current_layer = constrain(current_layer, 0, BOARD_DEPTH-1)
    if mouse[0]<ISO_WIDTH:
        if button == 0: # left mouse button
            mainBoard.rotate(mrel[0]*dragSensitivity, mrel[1]*dragSensitivity)
        elif button == 2: # right mouse button
            mainBoard.resetNodes()
            if not click:
                mainBoard.rotate((mouse[0]-ISO_WIDTH/2)/ISO_WIDTH*PI*2, 0)
                mainBoard.rotate(0, (mouse[1]-HEIGHT/2)/HEIGHT*PI)
    if not frozen:
        updateSliceDisplay()
        updateToolbar()
        updateIsoDisplay()
        if mainBoard.won:
            print("you have won the game")
            alert("You have won!")
        if mainBoard.lost and not mainBoard.okLost:
            print("you have lost the game")
            alert("You lost")
    else:
        warnButton.run(DISPLAYSURF, mouse, mousedown, click)
    pygame.display.update()
    gameClock.tick(FPS)
    FRAME += 1
