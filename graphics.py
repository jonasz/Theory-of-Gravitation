import pygame
import math
import utils
from levels import ContactType
import random
import time
from controls import CTRL, TOGEvent

class Graphics:
    zoom = None
    transparent_actors = None

    def __init__(self, settings, level):
        self.settings = settings
        self.level = level
        self.zoom = utils.SmoothChanger(-3)

        pygame.init()
        pygame.display.set_caption('Theory of Gravitation')

        self.screen = pygame.display.set_mode(settings.screen_size)

        self.transparent_actors = []


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

    def polygon(self, color, points):
        #print points
        points = map(self.screenCoord, points)
        pygame.draw.polygon(self.screen, color, points)

    def paintWorld(self):
        for actor in self.level.actors.values():
            actor.draw(self)

    def paint(self):
        self.zoom.step()
        self.screen.fill((0,0,0))
        self.paintWorld()
        pygame.display.flip()

    def getScale(self):
        sw,sh = self.settings.screen_size
        scale = 1. * sw / self.level.size[0] 
        scale *= self.settings.zoom_factor ** self.zoom.get()
        return scale

    # world coordinates -> screen coordinates
    def screenCoord(self, vec):
        vec = vec.copy()
        camera = self.level.character.body.position
        #camera = self.level.getCenter()
        vec -= camera

        sw,sh = self.settings.screen_size
        vec = utils.rotate(vec, -self.level.world_angle.get())
 

        vec *= self.getScale()
        x,y = map(int,vec)
        y = sh - y
        x+=sw/2
        y -= sh/2
        return (x,y)

    def scaleLength(self, length):
        return int(length*self.getScale())

    def subscribeToControls(self, ctrls):
        table = (
                (CTRL.ZOOM_OUT,   self.zoomOut),
                (CTRL.ZOOM_IN,    self.zoomIn),
        )

        for c,f in table:
            e = TOGEvent(code=c)
            ctrls.subscribeTo(e, f)
