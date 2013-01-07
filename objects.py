import Box2D as b2d
import pygame.image
import utils
import math
import random

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

class Pow2(StaticSprite):
    def __init__(self, position, size=(3,3)):
        angle = random.randint(-40, 40)
        super(Pow2, self).__init__(position, size, './sprites/pow2.png', angle)

class MaterialActor(Actor):
    body = None
    def __init__(self, world, **kwargs):
        super(MaterialActor, self).__init__()
        self.world = world
        self.shape_attrs = {}
        self.createBody(**kwargs)

    def applyShapeAttrs(self, shape):
        for (k,v) in self.shape_attrs.items():
            setattr(shape, k, v)
            #print shape.restitution

    def createBody(self, **kwargs):
        bodyDef = b2d.b2BodyDef()
        print 'create body', kwargs

        for (k,v) in kwargs.items():
            if k in ['position', 'angle', 'fixedRotation']:
                setattr(bodyDef, k, v)
            else:
                self.shape_attrs[k] = v

        self.body = self.world.CreateBody(bodyDef)
        self.body.SetUserData(self)

    def poke(self, vec):
        massCenter = self.body.massData.center
        self.body.ApplyImpulse(vec, massCenter)

    def move(self, vec):
        self.body.position += vec

    def isPointInside(self, vec):
        for shape in self.body.shapeList:
            if shape.TestPoint(self.body.GetXForm(), vec):
                return True
        return False

    def cleanUp(self):
        self.world.DestroyBody(self.body)


class Ball(MaterialActor):
    def addCircleShape(self, radius):
        self.radius = radius
        shapeDef = b2d.b2CircleDef()
        shapeDef.density = 1
        shapeDef.restitution = 0.8
        shapeDef.radius = radius

        self.applyShapeAttrs(shapeDef)
        #print shapeDef.restitution

        shape=self.body.CreateShape(shapeDef)
        if not self.static:
            self.body.SetMassFromShapes()

    def __init__(self, world, radius, static, **kwargs):
        super(Ball, self).__init__(world, **kwargs)
        self.static = static
        self.addCircleShape(radius)

    def draw(self, graphics):
        color = (130,40,120)
        if self.static: 
            color = (100, 20, 100)
        graphics.circle(color, self.body.position, self.radius)

    #rotating a ball is easy
    def rotate(self, vec1, vec2): pass

    def resize(self, vec1, vec2):
        origin = self.body.position
        d1 = (vec1-origin).Length()
        d2 = (vec2-origin).Length()
        scale = d2 / d1

        shape = self.body.shapeList[0]
        self.body.DestroyShape(shape)

        newradius = self.radius*scale
        self.addCircleShape(newradius)


class Box(MaterialActor):
    def __init__(self, world, size, angle = 0, static=False, **kwargs):
        self.static = static
        super(Box, self).__init__(world, **kwargs)
        self.addRectShape(size, angle)

    def addRectShape(self, size, angle):
        self.size = size
        shapeDef = b2d.b2PolygonDef()
        shapeDef.SetAsBox(*size)
        shapeDef.density = 1
        shapeDef.restitution = 0.8

        self.applyShapeAttrs(shapeDef)
        self.body.CreateShape(shapeDef)
        self.body.angle = angle

        if not self.static:
            self.body.SetMassFromShapes()

    def resize(self, vec1, vec2):

        origin = self.body.position
        angle = self.body.angle
        w,h = self.size

        vec1 = utils.rotate(vec1-origin, -angle)
        vec2 = utils.rotate(vec2-origin, -angle)

        resize_angle = utils.angle_between(vec1, b2d.b2Vec2(0,1)) - angle
        try:
            w *= 1. * vec2[0] / vec1[0]
            h *= 1. * vec2[1] / vec1[1]
        except ZeroDivisionError:
            pass #whatever

        w = max(w, 0.1)
        h = max(h, 0.1)

        shape = self.body.shapeList[0]
        self.body.DestroyShape(shape)

        self.addRectShape((w,h), angle)

    def rotate(self, vec1, vec2):
        origin = self.body.position
        angle = self.body.angle

        angle_delta = utils.angle_between(vec1 - origin, vec2 - origin)

        shape = self.body.shapeList[0]
        self.body.DestroyShape(shape)

        self.addRectShape(self.size, angle + angle_delta)

    def draw(self, graphics):
        shape = self.body.GetShapeList()[0]
        points = map(self.body.GetWorldPoint, shape.getVertices_tuple())
        graphics.polygon((200,10,100), points)


class Helicopter(Ball):
    def __init__(self, level, world, radius, **kwargs):
        super(Helicopter, self).__init__(world, radius, static = False, **kwargs)
        self.level = level
        self.spr_name = './sprites/heli.png'

    def draw(self, graphics):
        #super(Helicopter, self).draw(graphics)
        right = utils.rotate(b2d.b2Vec2(-1,0), self.level.world_angle.get())
        if self.body.linearVelocity.Length()<0.1:
            angle = 0.
        else:
            angle = utils.angle_between(right, self.body.linearVelocity)
            angle = int(angle * 180 / math.pi)
        graphics.putSprite(
                self.body.position,
                self.spr_name,
                (self.radius, self.radius),
                angle=angle,
                flipY = abs(angle)>90)

    def isMainCharacter(self):
        return True
