import pygame
import math
import time
import utils
import random
import itertools
import Box2D as b2d
from levels import ContactType
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule

class Graphics:
    __metaclass__ = utils.Singleton

    zoom = None

    def __init__(self, settings, level):
        self.settings = settings
        self.level = level
        self.zoom = utils.SmoothChanger(5)

        pygame.init()
        pygame.display.set_caption('Theory of Gravitation')

        flags = 0
        if settings.fullscreen:
            flags |= pygame.FULLSCREEN
            flags |= pygame.HWSURFACE
            flags |= pygame.DOUBLEBUF

        self.screen = pygame.display.set_mode(settings.screen_size, flags)


    def zoomIn(self):
        self.zoom.init_change(1)

    def zoomOut(self):
        self.zoom.init_change(-1)

    def circle(self, color, position, radius):
        #print position, self.screenCoord(position)
        #print radius, self.scaleLength(radius)
        pygame.draw.circle(
                self.screen,
                color,
                self.screenCoord(position),
                self.scaleLength(radius),
                0)

    def putSprite(self, position, spr_name, (we, he), angle=0, **kwargs):
        x,y = self.screenCoord(position)
        we,he = self.scaleLength(we), self.scaleLength(he)
        sprite = utils.get_bitmap(spr_name, 2*we, 2*he, **kwargs)
        if angle:
            sprite = pygame.transform.rotate(sprite, angle)
        w,h = sprite.get_size()
        x,y = x-w/2, y-h/2

        self.screen.blit(
                sprite,
                (x,y))

    def putText(self, text, position, color = (20,240,30)):
        font = pygame.font.Font(pygame.font.match_font('dejavusansmono', bold=True), 70)
        text = font.render(text, 1, color)
        textpos = text.get_rect(center = position)
        self.screen.blit(text, textpos)

    def printStats(self):
        W,H = self.settings.screen_size
        self.putText(str(self.level.timeLeft()), (80,50))
        self.putText(str(self.level.score), (W-80,50))

        if self.level.timeLeft() <= 0.01:
            y = (time.time()*150) % H
            self.putText("GAME OVER LOL", (W/2,y), color = (250, 110, 110))

    def polygon(self, color, points):
        #print points
        points = map(self.screenCoord, points)
        pygame.draw.polygon(self.screen, color, points)

    def paintWorld(self):
        for actor in self.level.actors.values():
            actor.draw(self)
        self.printStats()

    def paintBackground(self):
        self.screen.fill((0,0,0))
        W,H = self.level.size
        w,h = 30,30
        for x in range(0,W,w*2):
            for y in range(0,H,h*2):
                self.putSprite((x+w/2,y+w/2), './sprites/cogwheel.png', (w/2,h/2))
        

    def paint(self):
        self.zoom.step()
        self.paintBackground()
        self.paintWorld()
        pygame.display.flip()

    def getScale(self):
        sw,sh = self.settings.screen_size
        scale = 1. * sw / self.level.size[0] 
        scale *= self.settings.zoom_factor ** self.zoom.get()
        return scale

    # screen coordinates -> world coordinates
    def worldCoord(self, vec):
        sw,sh = self.settings.screen_size

        x,y = map(float, vec)
        y += sh/2
        x -= sw/2
        y = sh-y

        vec = b2d.b2Vec2(x,y)
        vec *= 1./self.getScale()
        vec = utils.rotate(vec, self.level.world_angle.get())

        vec += self.level.getCameraPosition()
        return vec

    # world coordinates -> screen coordinates
    def screenCoord(self, vec):
        if type(vec)==tuple: vec = b2d.b2Vec2(*vec)
        vec = vec.copy()
        vec -= self.level.getCameraPosition()

        sw,sh = self.settings.screen_size
        vec = utils.rotate(vec, -self.level.world_angle.get())

        vec *= self.getScale()
        x,y = map(int,vec)
        y = sh - y
        x += sw/2
        y -= sh/2
        return (x,y)

    def scaleLength(self, length):
        return int(length*self.getScale())

    def createControls(self):
        self.controls = ControlsCapsule ([
            CBInfo(
                ev = TOGEvent(code = CTRL.ZOOM_OUT),
                cb = self.zoomOut),

            CBInfo(
                ev = TOGEvent(code = CTRL.ZOOM_IN),
                cb = self.zoomIn),
            ])
