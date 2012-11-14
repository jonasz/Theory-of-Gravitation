import pygame
import pygame.locals
import settings
import graphics
import controls
import Box2D as b2d
from levels import FirstLevel

class Game:
    def __init__(self, level, settings, user_input, graph):
        self.level = level
        self.settings = settings
        self.user_input = user_input
        self.graph = graph
        self.running = True

        self.user_input.addKeybCallback(pygame.locals.K_q, self.quit)
        self.user_input.addKeybCallback(pygame.locals.K_MINUS, graph.zoomOut)
        self.user_input.addKeybCallback(pygame.locals.K_EQUALS, graph.zoomIn)


    def quit(self):
        self.running = False

    def start(self):
        self.level.constructWorld()
        clock = pygame.time.Clock()

        while self.running:
            self.user_input.dispatchEvents()
            self.level.updateWorld()
            self.graph.paint()
            clock.tick(self.settings.hz)
            #print clock.get_fps(), 'fps'

if __name__=='__main__':
    st = settings.Settings()
    fl = FirstLevel(st)
    ui = controls.Controls(fl)
    gr = graphics.Graphics(st, fl)

    g = Game(fl, st, ui, gr)
    g.start()
