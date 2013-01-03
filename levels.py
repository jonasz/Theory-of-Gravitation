import Box2D as b2d
import objects
import math
import utils
import time
import random
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule
import gravity_changers

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


# global function scheduler
# maybe there's a better place for it then the module namespace
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
    controls = None

    def getCenter(self):
        return b2d.b2Vec2(self.W, self.H)/2.

    def getCameraPosition(self):
        return self.getCenter()

    def getOriginalVec(self, *args):
        vec = b2d.b2Vec2(*args)
        return utils.rotate(vec, self.world_angle.get())

    def changeGravityChanger(self, newChanger):
        if self.world_angle: self.world_angle.controls.unsubscribe()
        self.world_angle = newChanger
        self.world_angle.createControls()

    def __init__(self, settings):
        self.settings = settings
        self.contactCallbackList = {
                ContactType.add: [],
                ContactType.remove: [],
                ContactType.persist: [],
                }

        self.createControls()
        self.subscribeToContacts(ContactType.add, self.clash)
        self.changeGravityChanger(gravity_changers.ConstantGravity())

    def addActor(self, actor):
        self.actors[actor.id] = actor
        return actor.id

    def removeActor(self, actor_id):
        #TODO: the physical body needs to be removed from b2d world
        self.actors.pop(actor_id)

    # returns an arbitrary actor that contains the given point
    def pickActor(self, pos):
        aabb = b2d.b2AABB()
        x,y = pos

        eps = 1e-5
        aabb.lowerBound = (x-eps, y-eps)
        aabb.upperBound = (x+eps, y+eps)

        num, shapes = self.world.Query(aabb, 10)
        if num == 0: return

        for shape in shapes:
            actor = shape.GetBody().userData
            if actor.isPointInside(pos): return actor

    def createControls(self):
        self.controls = ControlsCapsule()

    def physicsStep_(self):
        gravity = utils.rotate(self.original_gravity, self.world_angle.get())
        self.world.SetGravity(gravity)
        self.world.Step(
                self.settings.time_step,
                self.settings.vel_iters,
                self.settings.pos_iters)

    def updateWorld(self):
        G_FS.work()
        self.world_angle.step()
        self.physicsStep_()
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



class FirstLevel(Level):
    def __init__(self, *args, **kwargs):
        super(FirstLevel,  self).__init__(*args, **kwargs)
        #wa = gravity_changers.ContinuousGravityChanger()
        wa = gravity_changers.GravityChanger()
        self.changeGravityChanger(wa)

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

    def createControls(self):
        super(FirstLevel, self).createControls()

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
        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_LEFT),
                cb = self.moveLeft.start))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_RIGHT),
                cb = self.moveRight.start))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_UP),
                cb = self.moveUp.start))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_LEFT, pressed = False),
                cb = self.moveLeft.stop))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_RIGHT, pressed = False),
                cb = self.moveRight.stop))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_UP, pressed = False),
                cb = self.moveUp.stop))

    def getCameraPosition(self):
        return self.character.body.position


if __name__=='__main__':
    fl = FirstLevel()
    fl.constructWorld()
