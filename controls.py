import pygame
from pygame.locals import *
import utils
import graphics

# controller events
CTRL = utils.Enum(
        # keyboard
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
        'K1',
        'K2',
        'K3',
        'SHIFT',
        'CTRL',

        'DUMP',
        'LOAD',

        # mouse
        'LEFT_BUTTON',
        'MIDDLE_BUTTON',
        'RIGHT_BUTTON',
        'MOUSE_MOTION',
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
        K_1:        CTRL.K1,
        K_2:        CTRL.K2,
        K_3:        CTRL.K3,
        K_LSHIFT:   CTRL.SHIFT,
        K_LCTRL:    CTRL.CTRL,
        K_b:        CTRL.DUMP,
        K_n:        CTRL.LOAD,
        }

# TODO
PYGAME_POINTER_MAP = {
        1: CTRL.LEFT_BUTTON,
        2: CTRL.MIDDLE_BUTTON,
        3: CTRL.RIGHT_BUTTON,
        4: CTRL.ZOOM_IN,
        5: CTRL.ZOOM_OUT,
        }

# may be a controller event or a pointer event
# controller id may be added in future to allow multiplayer
class TOGEvent:
    # 'None' serves as a wildcard
    def __init__(self, code, position = None, pressed = True):
        self.code = code
        self.pressed = pressed

        # position is always expressed by world coordinates
        self.position = None
        if position:
            self.position = graphics.Graphics.instance.worldCoord(position)

    @property
    def released(self):
        return not pressed;

    def matches(self, ev2):
        if self.code != ev2.code: return False
        if (self.pressed is not None) and self.pressed != ev2.pressed:
            return False
        return True

# encapsulates an event and a callback
# 'withInfo' tells us if the callback should be called with TOGEvent as
# a paremeter
class CBInfo:
    def __init__(self, ev, cb, withInfo = False):
        self.event = ev
        self.callback = cb
        self.withInfo = withInfo

    def handle (self, togEvent):
        if self.event.matches(togEvent):
            if self.withInfo: self.callback(togEvent)
            else: self.callback()

class Controls:
    # SINGLETON class
    __metaclass__ = utils.Singleton

    def __init__(self):
        self.cbs = {}
        self.ids = (i for i in xrange(1,2*10**9)) # dirty

    def subscribeTo(self, cbInfo):
        ID = self.ids.next()
        self.cbs[ID] = cbInfo
        return ID

    def dispatchEvent_(self, togEvent):
        for cbInfo in self.cbs.values():
            cbInfo.handle(togEvent)

    def unsubscribe(self, callbackID):
        del self.cbs[callbackID]

    # loop through all the events provided by pygame.event
    # and call appropriate callbacks for every event
    def dispatchEvents(self):
        for event in pygame.event.get():
            position = None
            code = None
            pressed = False

            # creating TOGEevent
            if event.type in [KEYDOWN, KEYUP] and event.key in PYGAME_KB_MAP:
                pressed = event.type == KEYDOWN
                code = PYGAME_KB_MAP[event.key]

            elif event.type in [MOUSEBUTTONUP, MOUSEBUTTONDOWN] and \
                    event.button in PYGAME_POINTER_MAP:
                pressed = event.type == MOUSEBUTTONDOWN
                code = PYGAME_POINTER_MAP[event.button]
                position = event.pos

            elif event.type in [MOUSEMOTION]:
                code = CTRL.MOUSE_MOTION
                position = event.pos

            else:
                print event
                continue

            # dispatch
            self.dispatchEvent_(TOGEvent(
                code, pressed = pressed, position = position))


class ControlsCapsule:
    def __init__(self, callbacks = None):
        self.callbackIDs = []
        self.callbacks = []
        if callbacks:
            for cb in callbacks:
                self.addCallback(cb)

    def addCallback (self, cbInfo):
        self.callbacks.append(cbInfo)
        ID = Controls().subscribeTo(cbInfo)
        self.callbackIDs.append(ID)

    def subscribe(self):
        assert len(self.callbackIDs)==0
        callbacks = self.callbacks
        self.callbacks = []

        for x in callbacks:
            self.addCallback(x)

    def unsubscribe(self):
        for x in self.callbackIDs:
            Controls().unsubscribe(x)

        del self.callbackIDs[:]
