import Box2D as b2d
import objects
import math
import utils
import time
import random
from controls import CTRL, TOGEvent

class ContactType:
    add = 0
    persist = 1
    remove = 2

# Box2D contact listener
class ContactListener(b2d.b2ContactListener):
    def __init__(self, level):
        super(ContactListener, self).__init__()
        self.level = level

    def Add(self, point):
        self.level.contactCallbacks(ContactType.add, point)

    def Persist(self, point):
        self.level.contactCallbacks(ContactType.persist, point)

    def Remove(self, point):
        self.level.contactCallbacks(ContactType.remove, point)


G_FS = utils.FunsctionScheduler()


class Level(object):
    world = None
    W = 30
    H = 30
    size = (W, H)
    character = None
    world_angle = None
    original_gravity = b2d.b2Vec2(0, -10)
    contactCallbackList = None
    actors = {}

    def getCenter(self):
        return b2d.b2Vec2(self.W, self.H)/2.


    def getOriginalVec(self, *args):
        vec = b2d.b2Vec2(*args)
        return utils.rotate(vec, self.world_angle.get())

    def __init__(self, settings, ctrls, world_angle):
        self.world_angle = world_angle
        self.settings = settings
        self.contactCallbackList = {
                ContactType.add: [],
                ContactType.remove: [],
                ContactType.persist: [],
                }
        self.ctrls = ctrls

        self.subscribeToControls()
        self.subscribeToContacts(ContactType.add, self.clash)

    def addActor(self, actor):
        self.actors[actor.id] = actor
        return actor.id

    def removeActor(self, actor_id):
        self.actors.pop(actor_id)

    def subscribeToControls(self):
        self.world_angle.subscribeToControls(self.ctrls)

        # create ContinuousActions that will move the main character
        self.moveUp = utils.ContinuousAction(G_FS,
                fun = lambda: self.character.poke(self.getOriginalVec(0,30)),
                interval = 0.02)
        self.moveLeft = utils.ContinuousAction(G_FS,
                fun = lambda: self.character.poke(self.getOriginalVec(-30,0)),
                interval = 0.02)
        self.moveRight = utils.ContinuousAction(G_FS,
                fun = lambda: self.character.poke(self.getOriginalVec(30,0)),
                interval = 0.02)

        # subscribe to them
        table = (
                (CTRL.ARROW_LEFT,   True,    self.moveLeft.start),
                (CTRL.ARROW_RIGHT,  True,    self.moveRight.start),
                (CTRL.ARROW_UP,     True,    self.moveUp.start),

                (CTRL.ARROW_LEFT,   False,   self.moveLeft.stop),
                (CTRL.ARROW_RIGHT,  False,   self.moveRight.stop),
                (CTRL.ARROW_UP,     False,   self.moveUp.stop),
        )

        for c, pressed, f in table:
            e = TOGEvent(code=c, pressed=pressed)
            self.ctrls.subscribeTo(e, f)


    def updateWorld(self):
        G_FS.work()
        self.world_angle.step()
        gravity = utils.rotate(self.original_gravity, self.world_angle.get())
        self.world.SetGravity(gravity)
        self.world.Step(
                self.settings.time_step,
                self.settings.vel_iters,
                self.settings.pos_iters)
        #print self.world_angle.get()
    
    def subscribeToContacts(self, ctype, cb):
        self.contactCallbackList[ctype].append(cb)

    def contactCallbacks(self, ctype, point):
        for cb in self.contactCallbackList[ctype]:
            cb(point)

    def constructWorld(self):
        doSleep = False

        worldAABB=b2d.b2AABB()
        worldAABB.lowerBound = (-20, -20)
        worldAABB.upperBound = (self.size[0]+20, self.size[1]+20)
        self.world = b2d.b2World(worldAABB, self.original_gravity, doSleep)

        self.contactListener = ContactListener(self)
        self.world.SetContactListener(self.contactListener)

        self.constructFrame()

    def constructFrame(self):
        frame = [
            objects.Box(self.world,
                    (self.W/2,1),
                    position = (self.W/2, 0),
                    static=True,
                    restitution = 0),
            objects.Box(self.world,
                    (self.W/2,1),
                    position = (self.W/2, self.H),
                    static=True,
                    restitution = 0),
            objects.Box(self.world,
                    (1,self.H/2),
                    position = (0, self.H/2),
                    static=True,
                    restitution = 0),
            objects.Box(self.world,
                    (1,self.H/2),
                    position = (self.W, self.H/2),
                    static=True,
                    restitution = 0),
            ]
        for x in frame: self.addActor(x)


    # displays "POW!" actor when the main character collides with an obstacle
    def clash(self, point):
        if point.velocity.Length()<10: return
        o1 = point.shape1.GetBody().userData
        o2 = point.shape2.GetBody().userData
        if not (o1.isMainCharacter() or o2.isMainCharacter()): return

        pos = point.position.copy()
        actor = random.choice((objects.Pow1, objects.Pow2))(pos)
        actorId = self.addActor(actor)

        G_FS.addAction(
            fun = lambda: self.removeActor(actorId),
            delay = 0.2)


# Gravity changers listen to keyboard actions and update
# the world angle accordingly. This may be used in more general scope in future.
class GravityChangerBase:
    def __init__(self):
        self.world_angle = utils.SmoothChanger(0)

    def subscribeToControls(self, ctrls):
        raise NotImplementedError

    def get(self):
        return self.world_angle.get()

    def step(self):
        self.world_angle.step()


class GravityChanger(GravityChangerBase):
    def __init__(self):
        self.world_angle = utils.SmoothChanger(0)

    def subscribeToControls(self, ctrls):
        table = (
                (CTRL.WORLD_LEFT,   True,    self.GravityLeft),
                (CTRL.WORLD_RIGHT,  True,    self.GravityRight),
                (CTRL.WORLD_UP,     True,    self.GravityUp),
                (CTRL.WORLD_DOWN,     True,  self.GravityDown),
            )

        for c, pressed, f in table:
            e = TOGEvent(code=c, pressed=pressed)
            ctrls.subscribeTo(e, f)

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
                G_FS,
                fun = self.GravityLeftFun,
                interval = self.TIMEDELTA)
        self.GravityRight = utils.ContinuousAction(
                G_FS,
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

    def subscribeToControls(self, ctrls):
        table = (
                (CTRL.WORLD_LEFT,   True,    self.GravityLeft.start),
                (CTRL.WORLD_RIGHT,  True,    self.GravityRight.start),

                (CTRL.WORLD_LEFT,   False,   self.GravityLeft.stop),
                (CTRL.WORLD_RIGHT,  False,   self.GravityRight.stop),
            )

        for c, pressed, f in table:
            e = TOGEvent(code=c, pressed=pressed)
            ctrls.subscribeTo(e, f)


class FirstLevel(Level):
    def __init__(self, *args, **kwargs):
        wa = ContinuousGravityChanger()
        #wa = GravityChanger()
        super(FirstLevel,  self).__init__(*args, world_angle = wa, **kwargs)

    def constructWorld(self):
        super(FirstLevel, self).constructWorld()

        self.addActor( objects.Ball(self.world, 2, position = (15,25)) )
        self.addActor( objects.Ball(self.world, 2, position = (15,25)) )
        self.addActor( objects.Box(self.world, (3,3), position = (15,25)) )

        self.character = objects.Helicopter(
                self,
                self.world,
                3,
                position = (16,25),
                angle = 1.,
                restitution = 0.1,
                fixedRotation = True)

        self.addActor(self.character)


if __name__=='__main__':
    fl = FirstLevel()
    fl.constructWorld()
