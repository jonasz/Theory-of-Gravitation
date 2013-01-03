import utils
import math
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule
import levels

# Gravity changers listen to keyboard actions and update
# the world angle accordingly. This may be used in more general scope in future.
class GravityChangerBase:
    def __init__(self):
        self.world_angle = utils.SmoothChanger(0)

    def createControls(self):
        raise NotImplementedError

    def get(self):
        return self.world_angle.get()

    def step(self):
        self.world_angle.step()

class ConstantGravity(GravityChangerBase):
    def createControls(self):
        self.controls = ControlsCapsule()

class GravityChanger(GravityChangerBase):
    def __init__(self):
        self.world_angle = utils.SmoothChanger(0)

    def createControls(self):
        self.controls = ControlsCapsule ([
                CBInfo(
                    TOGEvent(code = CTRL.WORLD_LEFT),
                    cb = self.GravityLeft),
                CBInfo(
                    TOGEvent(code = CTRL.WORLD_RIGHT),
                    cb = self.GravityRight),
                CBInfo(
                    TOGEvent(code = CTRL.WORLD_UP),
                    cb = self.GravityUp),
                CBInfo(
                    TOGEvent(code = CTRL.WORLD_DOWN),
                    cb = self.GravityDown),
                ])

    def GravityLeft(self):
        self.world_angle.init_change(math.pi/2)

    def GravityRight(self):
        self.world_angle.init_change(-math.pi/2)

    def GravityUp(self):
        self.world_angle.init_change(math.pi)

    def GravityDown(self):
        self.world_angle.init_change(-math.pi)


# too expensive?
class ContinuousGravityChanger(GravityChangerBase):
    TIMEDELTA = 0.02 # ~ 50 times per sec
    DELTA = 0.04
    def __init__(self):
        self.world_angle = 0.
        self.GravityLeft = utils.ContinuousAction(
                levels.G_FS,
                fun = self.GravityLeftFun,
                interval = self.TIMEDELTA)
        self.GravityRight = utils.ContinuousAction(
                levels.G_FS,
                fun = self.GravityRightFun,
                interval = self.TIMEDELTA)

    def get(self):
        return self.world_angle

    def step(self):
        self.world_angle

    def GravityLeftFun(self):
        self.world_angle += self.DELTA

    def GravityRightFun(self):
        self.world_angle -= self.DELTA

    def createControls(self):
        self.controls = ControlsCapsule ([
                CBInfo(
                    ev = TOGEvent(code = CTRL.WORLD_LEFT),
                    cb = self.GravityLeft.start),
                CBInfo(
                    ev = TOGEvent(code = CTRL.WORLD_LEFT, pressed = False),
                    cb = self.GravityLeft.stop),

                CBInfo(
                    ev = TOGEvent(code = CTRL.WORLD_RIGHT),
                    cb = self.GravityRight.start),
                CBInfo(
                    ev = TOGEvent(code = CTRL.WORLD_RIGHT, pressed = False),
                    cb = self.GravityRight.stop),
                ])

