import copy
import math
import random

import pygame

from classes.tile import Tile


class Board2D:
    def __init__ (self, w, h):
        self.width = w
        self.height = h
        self.size = [self.width, self.height]
        self.board = []
        for i in range(self.height):
            self.board.append([])
            for j in range(self.width):
                self.board[i].append(Tile())
    def draw (self, w, h):
        # return a surface
        surf = pygame.Surface((w, h))
        bx = w/self.width
        by = h/self.height
        for i in range(self.height):
            for j in range(self.width):
                x = bx*j
                y = by*i
                self.board[i][j].drawTile(surf, x, y, min(bx, by))
        return surf

class Point3D:
    def __init__ (self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    def __str__ (self):
        return "<%d, %d, %d>"%(self.x, self.y, self.z)
    @staticmethod
    def rotate2d (x, y, theta):
        return [x * math.cos(theta) - y * math.sin(theta), y * math.cos(theta) + x * math.sin(theta)]
    def prefRotate (self, xz, yz):
        self.y, self.z = self.rotate2d(self.y, self.z, yz)
        self.x, self.z = self.rotate2d(self.x, self.z, xz)
    def mult (self, n):
        return Point3D(self.x*n, self.y*n, self.z*n)
    def sub (a, b):
        return Point3D(
            a.x-b.x,
            a.y-b.y,
            a.z-b.z
        )
    def length (self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def normalize (self):
        return self.mult(1/self.length())
    def translate (self, n):
        return Point3D(self.x+n.x, self.y+n.y, self.z+n.z)
    def dot (a, b):
        return a.x*b.x + a.y*b.y + a.z*b.z
    def cross (a, b):
        return Point3D(
            a.y*b.z - a.z*b.y,
            a.z*b.x - a.x*b.z,
            a.x*b.y - a.y*b.x
        )
    def pos2d(self):
        return (int(self.x), int(self.y))

class Node: # data class
    def __init__ (self, point, id, display):
        self.point = point
        self.averageZ = point.z
        self.id = id # [layer, i, j]
        self.display = display
    # def __init__ (self, face):
    #     self.point = face.point
    #     self.averageZ = face.point.z
    #     self.id = face.id
    #     self.display = face.display
    def rotate (self, xz, yz):
        self.point.prefRotate(xz, yz)
        self.averageZ = self.point.z
    def draw3D (self, surf, tile, w, h, zoom, highlight_level):
        pos = Point3D.pos2d(
            Point3D.translate(
                Point3D.mult(self.point, w / 2 * zoom),
                Point3D(w / 2, h / 2)
            )
        )
        s = int(w * 0.15 * zoom)
        col = (120, 120, 120)  # teal if not uncovered and not mine
        rad = s
        draw_circle = True
        if tile.uncovered:
            col = (0, 100, 255)
            rad = s
            if tile.getNumber() > 0:
                col = tile.getColor()
                rad = s
                draw_circle = False
            if tile.mine:
                col = (255, 0, 0)
                rad = int(s*1.2)
            if tile.getNumber() == 0:
                return
        else:
            if tile.flagged:
                col = (0, 0, 0)
                rad = s

        if draw_circle:
            pygame.draw.circle(
                surf,  # surface
                col,  # color
                pos,  # center
                rad,  # radius
                0  # fill type
            )
        else:
            tile.drawVTextCenter(pos[0], pos[1], surf, col)
        if tile.mine and tile.uncovered:
            return
        if highlight_level==2: # hovering
            pygame.draw.circle(
                surf,  # surface
                (0, 0, 255),  # color
                pos,  # center
                rad,  # radius
                2  # fill type
            )
        elif highlight_level==1: # on level
            pygame.draw.circle(
                surf,  # surface
                (255, 255, 255),  # color
                pos,  # center
                rad,  # radius
                1  # fill type
            )
class Line(Node): # data class
    def __init__ (self, point1, point2, id, display):
        self.point1 = point1
        self.point2 = point2
        Node.__init__(self, point1, id, display)
        self.averageZ = (self.point2.z + self.point1.z) / 2
    def rotate (self, xz, yz):
        self.point1.prefRotate(xz, yz)
        self.point.prefRotate(xz, yz)
        self.point2.prefRotate(xz, yz)
        self.averageZ = (self.point2.z + self.point1.z) / 2
    def draw3D (self, surf, tile, w, h, zoom, highlight_level):
        pos1 = Point3D.pos2d(
            Point3D.translate(
                Point3D.mult(self.point1, w / 2 * zoom),
                Point3D(w / 2, h / 2)
            )
        )
        pos2 = Point3D.pos2d(
            Point3D.translate(
                Point3D.mult(self.point2, w / 2 * zoom),
                Point3D(w / 2, h / 2)
            )
        )
        thick = 1
        col = (255, 255, 255)
        pygame.draw.line(surf, col, pos1, pos2, thick)
class Face(Node): # face class of nodes
    def __init__ (self, centerpoint, color, vertices, faces, id, display):
        #Node.__init__(self, centerpoint, id, display)
        self.display = display
        self.id = id
        self.point = centerpoint
        self.vertices = vertices # [ Point3D, Point3D, Point3D, ... ]
        self.faces = faces # [ [id0, id1, id2, id3 . . .], [id0, id1, id2, id3 . . .], ]
        self.color = color
        self.averageZ = 0
        resize = 0.5 * 0.8
        for v in self.vertices:
            # v = Point3D.mult(v, 0.5)
            # v = Point3D.translate(v, self.point)
            v.x *= resize
            v.y *= resize
            v.z *= resize
            v.x += self.point.x
            v.y += self.point.y
            v.z += self.point.z
            self.averageZ += v.z
        self.averageZ /= len(self.vertices)

    def rotate (self, xz, yz):
        self.averageZ = 0
        for v in self.vertices:
            v.prefRotate(xz, yz)
            self.averageZ += v.z
        self.averageZ /= len(self.vertices)
    # @staticmethod
    def constrain(self, n, mn, mx):
        return min(max(n, mn), mx)
    def shadeColor (self, col, n, s=[0, 0, 0]):
        return [self.constrain(col[i]*n+s[i], 0, 255) for i in range(len(col))]
    def draw3D (self, surf, tile, w, h, zoom, highlight_level):
        lightDirection = Point3D(1.0, 0.5, 0.0)
        vv = []
        for v in self.vertices:
            vv.append(
                Point3D.pos2d(
                    Point3D.translate(
                        Point3D.mult(v, w / 2 * zoom),
                        Point3D(w / 2, h / 2)
                    )
                )
            )
        ff = []
        """
            [
                [ 
                    [ coordinate, coord, coord ], 
                    [ color ], 
                    averageZ 
                ],
                ...
            ]
        """
        for f in self.faces:
            vs = [self.vertices[i] for i in f]
            normal = Point3D.cross(
                Point3D.sub(vs[1], vs[0]),
                Point3D.sub(vs[len(vs)-1], vs[0])
            )
            diffuse = Point3D.dot(normal, lightDirection)
            dv = [(vv[i][0], vv[i][1]) for i in f]
            col = self.shadeColor([255, 255, 255], diffuse*0.1, self.color)
            avgz = 0
            for i in vs:
                avgz += i.z
            avgz /= len(vs)
            ff.append([dv, col, avgz])
            # pygame.draw.polygon(
            #     surf,
            #     self.shadeColor(col, diffuse),
            #     dv
            # )
        ff.sort(key=lambda e:e[2], reverse=True)
        for f in ff:
            pygame.draw.polygon(
                surf,
                f[1],
                f[0]
            )
            if highlight_level > 0:
                pygame.draw.polygon(
                    surf,
                    (0, 0, 255) if highlight_level == 2 else (255, 255, 255),
                    f[0],
                    2 if highlight_level == 2 else 1
                )



class Board3D:
    def __init__ (self, layers, w, h): # initialize the instance
        self.size = (layers, w, h)
        self.board = [Board2D(w, h) for i in range(self.size[0])]
        self.checkRel = [[int(i/9)-1, int((i%9)/3)-1, int(i%3)-1] for i in range(0, 27) if i!=13] # generate relative coordinates to check
        self.initialized = False
        self.nodes = []
        self.won = False
        self.lost = False
        self.okLost = False
        self.cube = [
            [
                Point3D(-1, -1, -1),
                Point3D(-1, -1, 1),
                Point3D(-1, 1, -1),
                Point3D(-1, 1, 1),
                Point3D(1, -1, -1),
                Point3D(1, -1, 1),
                Point3D(1, 1, -1),
                Point3D(1, 1, 1),
            ],
            [
                [0, 2, 3, 1],
                [4, 5, 7, 6],
                [0, 1, 5, 4],
                [2, 3, 7, 6],
                [0, 2, 6, 4],
                [1, 3, 7, 5]
            ]
        ]
        self.loop(lambda e, z, i, j:e.changeVFontSize(int(1/max(max(self.size[0], self.size[1]), self.size[2])*100)))
        self.resetNodes()

    def init (self):
        for l in range(self.size[0]):
            board = self.board[l]
            for i in range(board.height):
                for j in range(board.width):
                    ti = board.board[i][j]
                    ti.mine = False
                    ti.uncovered = False
                    ti.number = None
                    ti.hasNumber = False

    def start (self, id=[0, 0, 0], mineDensity=0.9): # initialize the board, with the ID point as the first point
        clicked = self.board[id[0]].board[id[1]][id[2]]
        clicked.uncovered = True
        clicked.number = 0
        clicked.mine = False
        clicked.hasNumber = True
        totalTiles = 0
        for l in self.board:
            totalTiles += l.width*l.height
        minedTiles = 0
        retries = 0
        # estimatedMines = int(mineDensity*totalTiles)
        while float(minedTiles/totalTiles)<mineDensity:
            z = random.randint(0, self.size[0]-1)
            x = random.randint(0, self.board[z].width-1)
            y = random.randint(0, self.board[z].height-1)
            ti = self.board[z].board[y][x]
            if z == id[0] and y == id[1] and x == id[2]:
                continue
            if ti.mine is None or ti.mine is False:
                ti.mine = True # set mines
                minedTiles += 1
            else:
                retries += 1
            if retries>100:
                break

        for l in range(self.size[0]):
            board = self.board[l]
            for i in range(board.height):
                for j in range(board.width):
                    if l == id[0] and i == id[1] and j == id[2]:
                        continue
                    ti = board.board[i][j]
                    if ti.mine is None:
                        ti.mine = False # set mine
                    ti.uncovered = False # set uncovered
                    if ti.mine:
                        ti.hasNumber = False
                    else:
                        ti.number = self.getTileNumberByID([l, i, j])
        clicked.number = self.getTileNumberByID(id)
        self.initialized = True
                    
    def inBounds (self, id):
        return 0<=id[0]<self.size[0] and 0<=id[1]<self.size[1] and 0<=id[2]<self.size[2]
    def resetNodes (self):
        self.nodes = []
        z = 0
        for l in self.board:
            h = l.height
            w = l.width
            for i in range(h):
                for j in range(w):
                    ti = l.board[i][j]
                    centerp = Point3D(
                                j-w/2 + 0.5,
                                i-h/2 + 0.5,
                                z-self.size[0]/2 + 0.5
                            )
                    if False and ti.mine or ti.flagged:
                        self.nodes.append(Node(
                            centerp,
                            [z, i, j],
                            True
                        ))
                    else:
                        self.nodes.append(Face(
                            centerp,
                            [100, 100, 100],
                                [
                                    Point3D(-1, -1, -1),
                                    Point3D(-1, -1, 1),
                                    Point3D(-1, 1, -1),
                                    Point3D(-1, 1, 1),
                                    Point3D(1, -1, -1),
                                    Point3D(1, -1, 1),
                                    Point3D(1, 1, -1),
                                    Point3D(1, 1, 1),
                                ],
                                [
                                    [0, 2, 3, 1],
                                    [4, 5, 7, 6],
                                    [0, 1, 5, 4],
                                    [2, 3, 7, 6],
                                    [0, 2, 6, 4],
                                    [1, 3, 7, 5]
                                ],
                            [z, i, j],
                            True
                        ))
            z += 1
        self.cleanNodes()
        ### add a test line
        # self.nodes.append(Line(
        #     Point3D(0, 0, 0),
        #     Point3D(1, 1, 1),
        #     [0, 0, 0], # not a tile
        #     True
        # ))

        # add a test cube
        # for i in cube[0]: i = i.mult(5)
        # self.nodes.append(Face(
        #     Point3D(0, 0, 0),
        #     color,
        #     cube[0],
        #     cube[1],
        #     [0, 0, 0],
        #     True
        # ))
    def checkWon (self):
        self.won = False
        for l in self.board:
            for i in l.board:
                for j in i:
                    if not j.uncovered and not j.mine:
                        return False
        self.won = True
        return True

    def click (self, id, mineDensity=0.1):
        if not self.inBounds(id):
            return
        ti = self.board[id[0]].board[id[1]][id[2]]
        if ti.uncovered or ti.flagged:
            return
        if not self.initialized:
            self.start(id, mineDensity)#todo: finish this thingy
        else:
            ti.uncovered = True
        if ti.mine:
            self.lost = True
            for i in self.board:
                for j in i.board:
                    for k in j:
                        if k.mine:
                            k.uncovered = True
        self.cleanNodes()
        self.checkWon()
        if ti.number == 0 and not ti.mine:
            for c in self.checkRel:
                nid = [id[0]+c[0], id[1]+c[1], id[2]+c[2]]
                if not self.inBounds(nid):
                    continue
                nti = self.board[nid[0]].board[nid[1]][nid[2]]
                self.click(nid)
    def flag (self, id):
        ti = self.board[id[0]].board[id[1]][id[2]]
        if ti.uncovered: return
        ti.flagged = not ti.flagged
        self.cleanNodes()

    def getTileNumberByID (self, id):
        # ti = self.board[id[0]].board[id[1]][id[2]] # get tile
        n = 0 # number of mines around
        for r in self.checkRel:
            c = [r[0]+id[0], r[1]+id[1], r[2]+id[2]]
            if c[0]<0 or c[1]<0 or c[2]<0 or c[0]>=self.size[0] or c[1]>=self.size[1] or c[2]>=self.size[2]:
                continue
            ct = self.board[c[0]].board[c[1]][c[2]]
            if ct.mine:
                n += 1
        return n
    def loop (self, func):
        z = -1
        for l in self.board:
            z += 1
            for i in range(l.height):
                for j in range(l.width):
                    func(l.board[i][j], z, i, j)

    def rotate (self, xz, yz):
        for node in self.nodes:
            node.rotate(xz, yz)

    def cleanNodes (self):
        index = -1
        for n in self.nodes:
            index += 1
            t = self.board[n.id[0]].board[n.id[1]][n.id[2]]
            if isinstance(n, Face):  # convert to node
                if t.uncovered:
                    ogpos = Point3D()
                    for p in n.vertices:
                        ogpos.x += p.x
                        ogpos.y += p.y
                        ogpos.z += p.z
                    sc = 1 / len(n.vertices)
                    ogpos.x *= sc
                    ogpos.y *= sc
                    ogpos.z *= sc
                    self.nodes[index] = Node(ogpos, n.id, n.display)
                else:
                    n.color = (0, 0, 0) if t.flagged else (100, 100, 100)

    def draw3D (self, w, h, htile=[-1, -1, -1], current_layer=-1, zoom=1):
        #draw something
        surf = pygame.Surface((w, h))
        surf.fill((50, 150, 255))
        self.nodes.sort(key=lambda e:e.averageZ, reverse=True)
        for n in self.nodes:
            if not n.display:
                continue
            t = self.board[n.id[0]].board[n.id[1]][n.id[2]] # get the tile
            #(self, surf, pos, tile, s, highlight_level)
            spEciAl = n.id[0] == htile[0] and n.id[1] == htile[1] and n.id[2] == htile[2]
            onLayer = n.id[0] == current_layer
            highlight_level = 2 if spEciAl else (1 if onLayer else 0)
            zoomScale = 1.0 / max(max(self.size[0], self.size[1]), self.size[2]) * zoom
            n.draw3D(surf, t, w, h, zoomScale, highlight_level)

        return surf

    def drawSlice (self, layer, surface, bounds, mouse=(-1, -1)):
        bounds = pygame.Rect(bounds)
        board = self.board[layer].board
        tilesX = len(board[0])
        tilesY = len(board)
        border = 3
        tborder = 2
        bx = (bounds.w-border*2)/tilesX
        by = (bounds.h-border*2)/tilesY
        tw = bx-tborder
        th = by-tborder
        surface.fill(Tile().colors["BOARD_BACK"], bounds)
        hitTile = [[-1, -1, -1], Tile(), False] # [i, j, tile]
        for i in range(0, tilesY):
            for j in range(0, tilesX):
                x = bounds.x + bx*j + border + tborder
                y = bounds.y + by*i + border + tborder
                ti = board[i][j]
                ti.drawTile(surface, x, y, min(bx, by)-tborder)
                if x <= mouse[0] <= x+tw and y <= mouse[1] <= y + th:
                    hitTile = [[layer, i, j], ti, True]
        return hitTile
