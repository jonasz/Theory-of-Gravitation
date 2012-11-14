import pygame
from pygame.locals import *

class Controls:
    def __init__(self, level):
        self.level = level

        self.keyb = {
                K_w: level.GravityUp,
                K_s: level.GravityDown,
                K_d: level.GravityLeft,
                K_a: level.GravityRight,
                K_LEFT: level.moveLeft,
                K_RIGHT: level.moveRight,
                K_UP: level.jump,
                }

    def dispatch(self, table, key):
        if key in table:
            table[key]()
            return True
        else:
            return False

    def addKeybCallback(self, key, callback):
        assert key not in self.keyb, 'key ' + str(key) + ' already in use'
        self.keyb[key] = callback

    def dispatchEvents_(self, events):
        for event in events:
            if event.type==QUIT: return False
            if event.type==KEYDOWN:
                if not self.dispatch(self.keyb, event.key):
                    print 'unknown key: %s (%d)' % (event.unicode, event.key)

    def checkPressedKeys(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        for k in [K_LEFT, K_RIGHT, K_UP]:
            if keys[k]: self.keyb[k]()

    def dispatchEvents(self):
        self.dispatchEvents_(pygame.event.get())
        self.checkPressedKeys()
