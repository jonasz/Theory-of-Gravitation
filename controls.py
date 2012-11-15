import pygame
from pygame.locals import *
from utils import Enum

# controller events
CTRL = Enum(
        'ARROW_LEFT',
        'ARROW_DOWN',
        'ARROW_RIGHT',
        'ARROW_UP',
        'WORLD_LEFT',
        'WORLD_DOWN',
        'WORLD_RIGHT',
        'WORLD_UP',
        'ZOOM_IN',
        'ZOOM_OUT',
        'SPACE',
        'QUIT',
        )

# pointer events
POINTER = Enum(
        'LEFT_BUTTON',
        'MIDDLE_BUTTON',
        'RIGHT_BUTTON',
        )


PYGAME_KB_MAP = {
        K_LEFT:     CTRL.ARROW_LEFT,
        K_DOWN:     CTRL.ARROW_DOWN,
        K_RIGHT:    CTRL.ARROW_RIGHT,
        K_UP:       CTRL.ARROW_UP,
        K_a:        CTRL.WORLD_LEFT,
        K_s:        CTRL.WORLD_DOWN,
        K_d:        CTRL.WORLD_RIGHT,
        K_w:        CTRL.WORLD_UP,
        K_SPACE:    CTRL.SPACE,
        K_q:        CTRL.QUIT,
        K_MINUS:    CTRL.ZOOM_OUT,
        K_EQUALS:   CTRL.ZOOM_IN,
        }

# may be a controller event or a pointer event
# controller id may be added in future to allow multiplayer
class TOGEvent:
    def __init__(self, code, position = None, pressed = True):
        self.code = code
        self.position = position
        self.pressed = pressed

    @property
    def released(self):
        return not pressed;

    def matches(self, ev2):
        if self.code != ev2.code: return False
        if self.pressed != ev2.pressed: return False
        return True

class Controls:
    def __init__(self):
        self.cbs = []

    def subscribeTo(self, togEvent, callback):
        self.cbs.append((togEvent, callback, False))

    def subscribeWithInfoTo(self, togEvent, callback):
        self.cbs.append((togEvent, callback, True))

    def dispatchEvent_(self, togEvent):
        for ev, cb, info in self.cbs:
            if ev.matches(togEvent):
                if info: cb(togEvent)
                else: cb()

    def dispatchEvents(self):
        for event in pygame.event.get():
            if event.type in [KEYDOWN, KEYUP] and event.key in PYGAME_KB_MAP:
                pressed = event.type == KEYDOWN
                code = PYGAME_KB_MAP[event.key]

            elif event.type in [MOUSEBUTTONUP, MOUSEBUTTONDOWN] and \
                    event.key in PYGAME_POINTER_MAP:
                pressed = event.type == MOUSEBUTTONDOWN
                code = PYGAME_POINTER_MAP[event.key]
                print pressed

            else:
                print 'unknown event:', event
                continue

            self.dispatchEvent_(TOGEvent(code, pressed = pressed))
