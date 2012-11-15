import pygame
from pygame.locals import *
import settings
import graphics
import Box2D as b2d
from levels import FirstLevel
from controls import CTRL, TOGEvent, Controls

class Game:
    def __init__(self, level, settings, ctrls, graph):
        self.level = level
        self.settings = settings
        self.ctrls = ctrls
        self.graph = graph
        self.running = True

        self.subscribeToControls()


    def subscribeToControls(self):
        self.graph.subscribeToControls(self.ctrls)
        table = (
                (CTRL.QUIT,             self.quit),
        )

        for c,f in table:
            e = TOGEvent(code=c)
            self.ctrls.subscribeTo(e, f)


    def quit(self):
        self.running = False

    def start(self):
        self.level.constructWorld()
        clock = pygame.time.Clock()

        while self.running:
            self.ctrls.dispatchEvents()
            self.level.updateWorld()
            self.graph.paint()
            clock.tick(self.settings.hz)
            #print clock.get_fps(), 'fps'

if __name__=='__main__':
    st = settings.Settings()
    ui = Controls()
    fl = FirstLevel(st, ui)
    gr = graphics.Graphics(st, fl)

    g = Game(fl, st, ui, gr)
    g.start()
