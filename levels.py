import Box2D as b2d
import objects
import math
import utils
import time
import random
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule
import gravity_changers
import pickle

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
    W = 80
    H = 80
    size = (W, H)
    character = None
    world_angle = None
    original_gravity = b2d.b2Vec2(0, -30)
    contactCallbackList = None
    actors = {}
    controls = None
    actor_id_generator = (i for i in xrange(10**9))

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

        self.subscribeToContacts(ContactType.add, self.clash)
        self.changeGravityChanger(gravity_changers.ConstantGravity())

    def addActor(self, actor):
        actor.id = 0
        while actor.id in self.actors.keys():
            actor.id = self.actor_id_generator.next()

        self.actors[actor.id] = actor
        return actor.id

    def removeActor(self, actor_id):
        actor = self.actors.pop(actor_id)
        actor.cleanUp()

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

    def pickClosestCandy(self, pos, radius):
        aabb = b2d.b2AABB()
        x,y = pos

        aabb.lowerBound = (x-radius, y-radius)
        aabb.upperBound = (x+radius, y+radius)

        num, shapes = self.world.Query(aabb, 20)
        if num == 0: return

        res = None
        res_dist = 10e20
        for shape in shapes:
            actor = shape.GetBody().userData
            if not isinstance(actor, objects.Candy): continue
            dist = (actor.body.position - pos).Length()
            if res_dist > dist:
                res = actor
                res_dist = dist
        return res

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

    def constructFrame(self):
        frame = [
            objects.Box(
                    size = (self.W/2,1),
                    position = (self.W/2, 0),
                    static=True,
                    restitution = 0),
            objects.Box(
                    size = (self.W/2,1),
                    position = (self.W/2, self.H),
                    static=True,
                    restitution = 0),
            objects.Box(
                    size = (1,self.H/2),
                    position = (0, self.H/2),
                    static=True,
                    restitution = 0),
            objects.Box(
                    size = (1,self.H/2),
                    position = (self.W, self.H/2),
                    static=True,
                    restitution = 0),
            ]
        for x in frame:
            x.create(self)
            self.addActor(x)

    def constructWorld(self):
        doSleep = False

        worldAABB=b2d.b2AABB()
        worldAABB.lowerBound = (-20, -20)
        worldAABB.upperBound = (self.size[0]+20, self.size[1]+20)
        self.world = b2d.b2World(worldAABB, self.original_gravity, doSleep)

        self.contactListener = ContactListener(self)
        self.world.SetContactListener(self.contactListener)


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

    # pickling
    def loadPickledData(self, filename = 'pickle.data'):
        print 'LOAD'
        with open(filename, 'rb') as f:
            self.actors = pickle.load(f)

            for actor in self.actors.values():
                print actor
                actor.create(self)

                if isinstance(actor, objects.Helicopter):
                    self.character = actor

    def dumpPickledData(self, filename = 'pickle.data'):
        print 'DUMP'
        with open(filename, 'w') as f:
            # we don't want to pickle the whole b2 world
            for actor in self.actors.values():
                actor.destroy()

            try:
                pickle.dump(self.actors, f)
            except Exception, s:
                print 'Pickling failed: ', s
                return

            for actor in self.actors.values():
                actor.create(self)

class PickledLevel(Level):
    filename = None

    def __init__(self, filename, *args, **kwargs):
        super(PickledLevel, self).__init__(*args, **kwargs)
        self.filename = filename

        wa = gravity_changers.GravityChanger()
        #wa = gravity_changers.ContinuousGravityChanger()
        self.changeGravityChanger(wa)

    def constructWorld(self):
        super(PickledLevel, self).constructWorld()
        self.loadPickledData(self.filename)

    def createControls(self):
        super(PickledLevel, self).createControls()
        self.character.createControls()

    def getCameraPosition(self):
        return self.character.body.position
