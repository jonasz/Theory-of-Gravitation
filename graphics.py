import pygame
import math
import utils
from levels import ContactType
import random
import time

class TransparentActor(object):
    def display(self): raise NotImplementedError

class DisplaySprite(TransparentActor):
    def __init__(self, sprite, position, siz, expire, graphics):
        self.sprite = sprite
        self.position = position
        self.siz = siz
        self.expire = expire
        self.graphics = graphics

    def display(self):
        self.graphics.putSprite(self.position, self.sprite, self.siz)
        return self.expire > time.time()

class Graphics:
    zoom = None
    loaded_sprites = None
    sprites = None

    def __init__(self, settings, level):
        self.settings = settings
        self.level = level
        self.zoom = utils.smoothChanger(-3)

        pygame.init()
        pygame.display.set_caption('Theory of Gravitation')

        self.screen = pygame.display.set_mode(settings.screen_size)

        level.subscribeToContacts(ContactType.add, self.crash)

        self.loadSprites()
        self.sprites = []

    def loadSprites(self):
        self.loaded_sprites = {}
        self.loaded_sprites['pow1'] = pygame.image.load('./sprites/pow1.png')
        self.loaded_sprites['pow2'] = pygame.image.load('./sprites/pow2.png')

    def showTransparentActors(self):
        cpy = self.sprites
        self.sprites = []
        for ac in cpy:
            if ac.display():
                self.sprites.append(ac)

    def addTransparentActor(self, ac):
        self.sprites.append(ac)

    def crash(self, point):
        if point.velocity.Length()<10: return
        o1 = point.shape1.GetBody().userData
        o2 = point.shape2.GetBody().userData
        #if not (o1.isMainCharacter() or o2.isMainCharacter()): return

        pos = point.position.copy()
        sprite = random.choice((
            self.loaded_sprites['pow1'],
            self.loaded_sprites['pow2']))
        self.addTransparentActor(
                DisplaySprite(sprite, pos, (3,3), time.time()+0.5, self))

    def zoomIn(self):
        self.zoom.init_change(1, 20)

    def zoomOut(self):
        self.zoom.init_change(-1,20)

    def circle(self, color, position, radius):
        #print position, self.screenCoord(position)
        #print radius, self.scaleLength(radius)
        pygame.draw.circle(
                self.screen,
                color,
                self.screenCoord(position),
                self.scaleLength(radius),
                0)

    def putSprite(self, position, sprite, (we, he), angle=0):
        x,y = self.screenCoord(position)
        we,he = self.scaleLength(we), self.scaleLength(he)
        sprite = pygame.transform.scale(sprite, (2*we, 2*he))

        angle *= 180. / math.pi
        if angle>90:
            sprite = pygame.transform.flip(sprite, True, False)
            angle = 180+angle
        sprite = pygame.transform.rotate(sprite, angle)

        w,h = sprite.get_size()
        x,y = x-w/2, y-h/2

        self.screen.blit(
                sprite,
                (x,y))

    def polygon(self, color, points):
        #print points
        points = map(self.screenCoord, points)
        pygame.draw.polygon(self.screen, color, points)

    def paintWorld(self):
        for obj in self.level.world.GetBodyList():
            #print obj
            if obj.userData:
                obj.userData.draw(self)
        self.showTransparentActors()

    def paint(self):
        self.zoom.step()
        self.screen.fill((0,0,0))
        self.paintWorld()
        pygame.display.flip()

    def getScale(self):
        sw,sh = self.settings.screen_size
        scale = 1. * sw / self.level.size[0] 
        scale *= self.settings.zoom_factor ** self.zoom.value
        return scale

    # world coordinates -> screen coordinates
    def screenCoord(self, vec):
        vec = vec.copy()
        camera = self.level.character.body.position
        #camera = self.level.getCenter()
        vec -= camera

        sw,sh = self.settings.screen_size
        vec = utils.rotate(
                vec,
                -self.level.world_angle.value)
 

        vec *= self.getScale()
        x,y = map(int,vec)
        y = sh - y
        x+=sw/2
        y -= sh/2
        return (x,y)

    def scaleLength(self, length):
        return int(length*self.getScale())
