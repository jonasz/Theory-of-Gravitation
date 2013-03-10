import Box2D as b2d
import pygame.image
import utils
import math
import random
import levels
from controls import Controls, CBInfo, TOGEvent, CTRL, ControlsCapsule

class Actor(object):
    def draw(self, graphics): raise NotImplementedError

    def isMainCharacter(self):
        return False

    def rotate(self, vec1, vec2): raise NotImplementedError
    def resize(self, vec1, vec2): raise NotImplementedError

    def move(self, vec): raise NotImplementedError
    def isPointInside(self, vec): raise NotImplementedError

    # called after the actor is removed from the level
    def cleanUp(self): pass

    # returns true if event should be consumed
    def clashWith(self, actor2, pos): return False


class StaticSprite(Actor):
    def __init__(self, position, size, spr_name, angle = 0):
        super(StaticSprite, self).__init__()
        self.position = position
        self.size = size
        self.spr_name = spr_name
        self.angle = angle

    def draw(self, graphics):
        graphics.putSprite(self.position, self.spr_name, self.size, self.angle)

    def move(self, vec):
        self.position += vec


class Pow1(StaticSprite):
    def __init__(self, position, size=(3,3)):
        angle = random.randint(-40, 40)
        super(Pow1, self).__init__(position, size, './sprites/pow1.png', angle)

class Scored(StaticSprite):
    def __init__(self, position, size=(6,6)):
        angle = random.randint(-40, 40)
        super(Scored, self).__init__(position, size, './sprites/scored.png', angle)


class Pow2(StaticSprite):
    def __init__(self, position, size=(3,3)):
        angle = random.randint(-40, 40)
        super(Pow2, self).__init__(position, size, './sprites/pow2.png', angle)

class SaySomething(StaticSprite):
    def __init__(self, position, size=(4,4)):
        angle = random.randint(-40, 40)
        sprite = random.choice((
            './sprites/say1.png',
            './sprites/say2.png',
            './sprites/say3.png',
            './sprites/say4.png',
            './sprites/say5.png',
            ))
        super(SaySomething, self).__init__(position, size, sprite, angle)

class MaterialActor(Actor):
    body = None
    level = None

    #body
    position = None
    fixedRotation = False
    static = None
    angle = None
    restitution = None
    linearDamping = None

    #shape
    density = None

    def __init__(self,
            position = None,
            density = 1.,
            fixedRotation = False,
            static = False,
            angle = 0.,
            restitution = 0.5,
            linearDamping = 0):
        super(MaterialActor, self).__init__()
        self.density = density
        self.position = b2d.b2Vec2(position)
        self.fixedRotation = fixedRotation
        self.static = static
        self.angle = angle
        self.restitution = restitution
        self.linearDamping = linearDamping

    def create(self, level):
        self.level = level
        self.world = self.level.world
        self.createBody()

    def destroy(self):
        #for shape in self.body.shapeList:
            #self.body.DestroyShape(shape)
        self.world.DestroyBody(self.body)
        self.body = None
        self.world = None
        self.level = None

    def createBody(self):
        bodyDef = b2d.b2BodyDef()

        bodyDef.position = self.position
        bodyDef.fixedRotation = self.fixedRotation
        bodyDef.angle = self.angle
        bodyDef.linearDamping = self.linearDamping

        self.body = self.world.CreateBody(bodyDef)
        self.body.SetUserData(self)

    def poke(self, vec):
        massCenter = self.body.massData.center
        self.body.ApplyImpulse(vec, massCenter)

    def move(self, vec):
        self.position += vec
        self.body.position += vec

    def isPointInside(self, vec):
        for shape in self.body.shapeList:
            if shape.TestPoint(self.body.GetXForm(), vec):
                return True
        return False

    def cleanUp(self):
        self.destroy()


class Ball(MaterialActor):
    radius = None

    def __init__(self, radius = 2, **kwargs):
        super(Ball, self).__init__(**kwargs)
        self.radius = radius

    def create(self, level):
        super(Ball, self).create(level)

        shapeDef = b2d.b2CircleDef()

        shapeDef.density = self.density
        shapeDef.restitution = self.restitution
        shapeDef.radius = self.radius

        shape = self.body.CreateShape(shapeDef)

        if not self.static:
            self.body.SetMassFromShapes()

    def draw(self, graphics):
        color = (130,40,120)
        if self.static: 
            color = (100, 20, 100)
        graphics.circle(color, self.body.position, self.radius)

    #rotating a ball is easy
    def rotate(self, vec1, vec2): pass

    def resize(self, vec1, vec2):
        level = self.level
        self.destroy()

        d1 = (vec1-self.position).Length()
        d2 = (vec2-self.position).Length()
        self.radius *= float(d2)/d1

        self.create(level)


class Box(MaterialActor):
    size = None

    def __init__(self, size, **kwargs):
        super(Box, self).__init__(**kwargs)

        self.size = size

    def create(self, level):
        super(Box, self).create(level)

        shapeDef = b2d.b2PolygonDef()
        shapeDef.SetAsBox(*self.size)

        shapeDef.density = self.density #XXX
        shapeDef.restitution = self.restitution

        self.body.CreateShape(shapeDef)

        if not self.static:
            self.body.SetMassFromShapes()

    def resize(self, vec1, vec2):
        level = self.level
        self.destroy()

        w,h = self.size

        vec1 = utils.rotate(vec1 - self.position, -self.angle)
        vec2 = utils.rotate(vec2 - self.position, -self.angle)
        try:
            w *= 1. * vec2[0] / vec1[0]
            h *= 1. * vec2[1] / vec1[1]
        except ZeroDivisionError:
            pass #whatever

        w = max(w, 0.1)
        h = max(h, 0.1)
        self.size = (w,h)

        self.create(level)

    def rotate(self, vec1, vec2):
        level = self.level
        self.destroy()

        origin = self.position
        self.angle += utils.angle_between(vec1 - origin, vec2 - origin)

        self.create(level)

    def draw(self, graphics):
        shape = self.body.GetShapeList()[0]
        points = map(self.body.GetWorldPoint, shape.getVertices_tuple())
        graphics.polygon((200,10,100), points)

class Candy(Ball):
    spr_name = './sprites/candy.png'
    grabbed = False

    def draw(self, graphics):
        graphics.putSprite(
                self.body.position,
                self.spr_name,
                (self.radius, 4./3.*self.radius),
                angle=self.body.angle*180/math.pi)

    def rotate(self, vec1, vec2):
        level = self.level
        self.destroy()

        origin = self.position
        self.angle += utils.angle_between(vec1 - origin, vec2 - origin)

        self.create(level)

    def grab(self):
        self.grabbed = True

    def release(self):
        self.grabbed = False

    def canStoreInTheHut(self):
        return not self.grabbed

class GorillaHut(Box):
    spr_name = './sprites/gorilla_hut.png'

    def draw(self, graphics):
        w,h = self.size
        graphics.putSprite(
                self.body.position,
                self.spr_name,
                (w*1.3, h*1.3),
                angle = self.level.getOriginalHorAngle()*180/math.pi)

    def clashWith(self, actor2, pos):
        if type(actor2) != Candy: return False

        if actor2.canStoreInTheHut():
            print 'jazda z ', actor2
            self.level.removeActor(actor2)
            self.level.increaseScore()
            self.level.putStaticActor(Scored(pos), 0.2)
            return True
        else:
            return False


class Gorilla(Ball):
    grabJoint = None
    spr_name = './sprites/monkey.png'
    happy_spr_name = './sprites/happy_monkey.png'
    grab_spr_name = './sprites/grab.png'
    candy = None

    def __init__(self, **kwargs):
        kwargs['linearDamping'] = 0.7
        super(Gorilla, self).__init__(**kwargs)

    def create(self, level):
        super(Gorilla, self).create(level)

    def drawHand(self, graphics):
        if not self.grabJoint: return

        a = self.grabJoint.GetAnchor1()
        b = self.grabJoint.GetAnchor2()
        pos = (a+b)/2.
        h = (a-b).Length()/2.
        w = h/4.
        right = utils.rotate(b2d.b2Vec2(-10,0), self.level.world_angle.get())
        angle = utils.angle_between(right, b-a)*180/math.pi-90

        graphics.putSprite(
                pos,
                self.grab_spr_name,
                (w,h),
                angle=angle)

    def draw(self, graphics):
        #super(Gorilla, self).draw(graphics)
        right = utils.rotate(b2d.b2Vec2(-10,0), self.level.world_angle.get())
        if self.body.linearVelocity.Length()<1:
            angle = 0.
        else:
            angle = utils.angle_between(right, self.body.linearVelocity-right)
            angle = int(angle * 180 / math.pi)

        if self.hasCandy(): sprite = self.happy_spr_name
        else: sprite = self.spr_name
        graphics.putSprite(
                self.body.position,
                sprite,
                (self.radius, self.radius),
                angle=angle,
                flipX = True,
                flipY = abs(angle)>90)

        self.drawHand(graphics)

    def hasCandy(self):
        return self.candy is not None

    def startGrab(self):
        assert not self.grabJoint
        candy = self.level.pickClosestCandy(self.body.position, 2*self.radius)
        if not candy: return

        self.candy = candy
        self.candy.grab()

        djd = b2d.b2DistanceJointDef()
        djd.body1 = self.body
        djd.body2 = candy.body
        djd.localAnchor1 = (0,0)
        djd.localAnchor2 = (0,0)
        djd.length = self.radius*2
        self.grabJoint = self.level.world.CreateJoint(djd)


    def stopGrab(self):
        if self.grabJoint:
            self.level.world.DestroyJoint(self.grabJoint)
            self.grabJoint = None

            offs = b2d.b2Vec2(self.radius*1.5, self.radius*1.5)
            offs = utils.rotate(offs, self.level.world_angle.get())
            saypos = self.body.position + offs
            self.level.putStaticActor(SaySomething(saypos), removeAfter = 1)

            self.candy.release()
            self.candy = None


    def isMainCharacter(self):
        return True


    def createControls(self):
        self.controls = ControlsCapsule()

        # create ContinuousActions that will move the main character
        self.moveUp = utils.ContinuousAction(levels.G_FS,
                fun = lambda: self.poke(self.level.getOriginalVec(0,240)),
                interval = 0.02)
        self.moveDown = utils.ContinuousAction(levels.G_FS,
                fun = lambda: self.poke(self.level.getOriginalVec(0,-140)),
                interval = 0.02)
        self.moveLeft = utils.ContinuousAction(levels.G_FS,
                fun = lambda: self.poke(self.level.getOriginalVec(-200,0)),
                interval = 0.02)
        self.moveRight = utils.ContinuousAction(levels.G_FS,
                fun = lambda: self.poke(self.level.getOriginalVec(200,0)),
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
                TOGEvent(code = CTRL.ARROW_DOWN),
                cb = self.moveDown.start))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_LEFT, pressed = False),
                cb = self.moveLeft.stop))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_RIGHT, pressed = False),
                cb = self.moveRight.stop))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_UP, pressed = False),
                cb = self.moveUp.stop))
        
        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.ARROW_DOWN, pressed = False),
                cb = self.moveDown.stop))


        # grab
        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.GRAB),
                cb = self.startGrab))

        self.controls.addCallback(CBInfo(
                TOGEvent(code = CTRL.GRAB, pressed = False),
                cb = self.stopGrab))
