"""
Hold a number key and use the left mouse button to place an actor.
(at the time of writing: use 1 for a ball, 2 for a rectangle)
You can interact with the objects by holding LSHIFT / LCTRL and using
your mouse.
"""
import Box2D as b2d
import settings
import graphics
import objects
from levels import Level
from game import Game
from controls import Controls, CBInfo, TOGEvent, CTRL, CTRL, ControlsCapsule
import pickle


class MouseControlled(object):
    def __init__(self, buttons):
        if isinstance(buttons, int):
            buttons = (buttons,)
        self.buttons = buttons

    def mouseUp(self, togEvent): pass
    def mouseDown(self, togEvent): pass
    def mouseMotion(self, togEvent): pass

    def createControls(self):
        self.controls = ControlsCapsule()
        for button in self.buttons:
            self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = button),
                cb = self.mouseDown,
                withInfo = True))
            self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = button, pressed = False),
                cb = self.mouseUp,
                withInfo = True))

        self.controls.addCallback(CBInfo(
            ev = TOGEvent(code = CTRL.MOUSE_MOTION, pressed = None),
            cb = self.mouseMotion,
            withInfo = True))



class CandyBuilder(MouseControlled):
    def __init__(self, level, radius = 2):
        super(CandyBuilder, self).__init__(CTRL.LEFT_BUTTON)
        self.level = level
        self.radius = radius

    def mouseDown(self, togEvent):
        pos = togEvent.position
        actor = objects.Candy(
                radius = self.radius,
                position = pos,
                restitution = 0.50,
                density = 0.7,
                static = False)
        actor.create(self.level)
        self.level.addActor(actor)



class RectBuilder(MouseControlled):
    def getClass(self):
        return self.cl

    def __init__(self, level, cl = objects.Box, size = (1,10)):
        super(RectBuilder, self).__init__(CTRL.LEFT_BUTTON)
        self.level = level
        self.cl = cl
        self.size = size

    def mouseDown(self, togEvent):
        pos = togEvent.position
        actor = self.getClass()(
                size = self.size,
                position = pos,
                restitution = 0,
                static = True)
        actor.create(self.level)
        self.level.addActor(
                actor)


class GorillaBuilder(MouseControlled):
    def __init__(self, level):
        super(GorillaBuilder, self).__init__(CTRL.LEFT_BUTTON)
        self.level = level

    def mouseDown(self, togEvent):
        pos = togEvent.position

        if self.level.character:
            self.level.removeActor(self.level.character)

        self.level.character = objects.Gorilla(
                radius = 6,
                position = pos,
                density = 0.5,
                angle = 1.,
                restitution = 0.1,
                fixedRotation = True)
        self.level.character.create(self.level)

        self.level.addActor(self.level.character)

#TODO: This needs improvement
# The feeling is far from smooth, probably because
# graphics.worldCoordinate is using level.getCameraPosition while
# we're messing with it
class CameraUpdater(MouseControlled):
    position = (0,0)
    origin = None

    def __init__(self, level):
        super(CameraUpdater, self).__init__(CTRL.MIDDLE_BUTTON)
        self.level = level
        self.position = level.getCenter()

    def mouseDown(self, togEv):
        pos = togEv.position
        self.origin = pos

    def mouseUp(self, togEv):
        self.origin = None

    def mouseMotion(self, togEv):
        if self.origin:
            delta = togEv.position - self.origin
            self.position -= delta
            self.origin = togEv.position

    def get(self):
        return self.position



class Mover(MouseControlled):
    actor = None
    origin = None

    def __init__(self, level):
        super(Mover, self).__init__(CTRL.LEFT_BUTTON)
        self.level = level

    def mouseDown(self, togEv):
        pos = togEv.position
        self.actor = self.level.pickActor(pos)
        self.origin = pos

    def mouseUp(self, togEv):
        self.actor = None

    def mouseMotion(self, togEv):
        if self.actor:
            pos = togEv.position
            self.actor.move(pos - self.origin)
            self.origin = pos



class Resizer(MouseControlled):
    actor = None
    origin = None
    shouldRotate = False

    def __init__(self, level):
        super(Resizer, self).__init__((CTRL.LEFT_BUTTON, CTRL.RIGHT_BUTTON))
        self.level = level

    def mouseDown(self, togEv):
        pos = togEv.position
        self.actor = self.level.pickActor(pos)
        self.origin = pos
        self.shouldRotate = togEv.code == CTRL.LEFT_BUTTON

    def mouseUp(self, togEv):
        self.actor = None

    def mouseMotion(self, togEv):
        if self.actor:
            pos = togEv.position
            if self.shouldRotate:
                self.actor.rotate(self.origin, pos)
            else:
                self.actor.resize(self.origin, pos)
            self.origin = pos


class EditorLevel(Level):
    currentBuilder = None
    cameraPosition = None

    def timeLeft(self):
        return 1

    #disabling physics
    def physicsStep_(self):
        pass

    def __init__(self, *args, **kwargs):
        self.cameraPosition = CameraUpdater(self)
        super(EditorLevel,  self).__init__(*args, **kwargs)

    def constructWorld(self):
        super(EditorLevel, self).constructWorld()
        self.constructFrame()

    def getCameraPosition(self):
        return self.cameraPosition.get()

    def updateWorld(self):
        super(EditorLevel, self).updateWorld()

    def setBuilder(self, builder):
        if self.currentBuilder:
            self.currentBuilder.controls.unsubscribe()
        self.currentBuilder = builder
        self.currentBuilder.createControls()
    
    def startCandyBuilder(self): self.setBuilder(CandyBuilder(self))
    def startRectBuilder(self): self.setBuilder(RectBuilder(self))
    def startHutBuilder(self): self.setBuilder(RectBuilder(self, objects.GorillaHut,(10,10)))
    def startGorillaBuilder(self): self.setBuilder(GorillaBuilder(self))
    def startMover(self): self.setBuilder(Mover(self))
    def startResizer(self): self.setBuilder(Resizer(self))

    def stopBuilder(self):
        if self.currentBuilder:
            self.currentBuilder.controls.unsubscribe()
            self.currentBuilder = None


    def createControls(self):
        super(EditorLevel, self).createControls()
        self.cameraPosition.createControls()


        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.K1),
                cb = self.startCandyBuilder))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.K2),
                cb = self.startRectBuilder))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.K3),
                cb = self.startGorillaBuilder))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.K4),
                cb = self.startHutBuilder))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.SHIFT),
                cb = self.startMover))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.CTRL),
                cb = self.startResizer))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.DUMP),
                cb = self.dumpPickledData))

        self.controls.addCallback(CBInfo(
                ev = TOGEvent(code = CTRL.LOAD),
                cb = self.loadPickledData))

        # releasing a key disposes the current builder
        for key in (CTRL.K1, CTRL.K2, CTRL.SHIFT, CTRL.CTRL):
            self.controls.addCallback(CBInfo(
                    ev = TOGEvent(code = key, pressed = False),
                    cb = self.stopBuilder))

if __name__=='__main__':
    st = settings.Settings()
    lvl = EditorLevel(st)
    gr = graphics.Graphics(st, lvl)

    g = Game(lvl, st, gr)
    g.start()
