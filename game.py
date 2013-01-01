import pygame
from pygame.locals import *
import settings
import graphics
import Box2D as b2d
from levels import FirstLevel
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule

class Game:
    def __init__(self, level, settings, graph):
        self.level = level
        self.settings = settings
        self.graph = graph
        self.running = True

        self.createControls()


    def createControls(self):
        self.graph.createControls()

        self.controls = ControlsCapsule ([
            CBInfo(
                TOGEvent(code = CTRL.QUIT),
                cb = self.quit),
            ])


    def quit(self):
        self.running = False

    def start(self):
        self.level.constructWorld()
        clock = pygame.time.Clock()

        while self.running:
            Controls().dispatchEvents()
            self.level.updateWorld()
            self.graph.paint()
            clock.tick(self.settings.hz)
            #print clock.get_fps(), 'fps'

if __name__=='__main__':
    st = settings.Settings()
    fl = FirstLevel(st)
    gr = graphics.Graphics(st, fl)

    g = Game(fl, st, gr)
    g.start()
