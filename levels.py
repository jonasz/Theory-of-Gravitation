import Box2D as b2d
import objects
import math
import utils

class ContactType:
    add = 0
    persist = 1
    remove = 2

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

class Level(object):
    world = None
    W = 30
    H = 30
    size = (W, H)
    character = None
    world_angle = None
    original_gravity = b2d.b2Vec2(0, -20)
    contactCallbackList = None

    def getCenter(self):
        return b2d.b2Vec2(self.W, self.H)/2.

    def __init__(self, settings):
        self.world_angle = utils.SmoothChanger(0)
        self.settings = settings
        self.contactCallbackList = {
                ContactType.add: [],
                ContactType.remove: [],
                ContactType.persist: [],
                }

    def updateWorld(self):
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

        #frame
        objects.Box(self.world,
                (self.W/2,1),
                position = (self.W/2, 0),
                static=True,
                restitution = 0)
        objects.Box(self.world,
                (self.W/2,1),
                position = (self.W/2, self.H),
                static=True,
                restitution = 0)
        objects.Box(self.world,
                (1,self.H/2),
                position = (0, self.H/2),
                static=True,
                restitution = 0)
        objects.Box(self.world,
                (1,self.H/2),
                position = (self.W, self.H/2),
                static=True,
                restitution = 0)

    def GravityLeft(self):
        self.world_angle.init_change(math.pi/2)

    def GravityRight(self):
        self.world_angle.init_change(-math.pi/2)

    def GravityUp(self):
        self.world_angle.init_change(math.pi)

    def GravityDown(self):
        self.world_angle.init_change(-math.pi)


class FirstLevel(Level):

    def constructWorld(self):
        super(FirstLevel, self).constructWorld()

        objects.Ball(self.world, 2, position = (15,25))
        objects.Ball(self.world, 2, position = (15,25))

        self.character = objects.Helicopter(
                self,
                self.world,
                3,
                position = (16,25),
                angle = 1.,
                restitution = 0.1,
                fixedRotation = False)

    def poke_character(self, x, y):
        vec = b2d.b2Vec2(x,y)
        b = self.character.body
        b.ApplyImpulse(
                utils.rotate(vec, self.world_angle.get()),
                b.GetWorldPoint(b.massData.center))

    def moveLeft(self):
        self.poke_character(-30,0)

    def moveRight(self):
        self.poke_character(30,0)

    def jump(self):
        self.poke_character(0, 30)


if __name__=='__main__':
    fl = FirstLevel()
    fl.constructWorld()
