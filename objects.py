import Box2D as b2d
import pygame.image
import utils
import math
import random

class Actor(object):
    actor_id_generator = (i for i in xrange(10**9))

    def __init__(self):
        self.id = self.actor_id_generator.next()

    def draw(self, graphics): raise NotImplementedError

    def isMainCharacter(self):
        return False

class StaticSprite(Actor):
    def __init__(self, position, size, spr_name, angle = 0):
        super(StaticSprite, self).__init__()
        self.position = position
        self.size = size
        self.spr_name = spr_name
        self.angle = angle

    def draw(self, graphics):
        graphics.putSprite(self.position, self.spr_name, self.size, self.angle)

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
            print shape.restitution

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


class Ball(MaterialActor):
    def __init__(self, world, radius, **kwargs):
        super(Ball, self).__init__(world, **kwargs)

        self.radius = radius
        shapeDef = b2d.b2CircleDef()
        shapeDef.density = 1
        shapeDef.restitution = 0.8
        shapeDef.radius = radius

        self.applyShapeAttrs(shapeDef)
        print shapeDef.restitution

        shape=self.body.CreateShape(shapeDef)
        self.body.SetMassFromShapes()

    def draw(self, graphics):
        graphics.circle((130,40,120), self.body.position, self.radius)


class Box(MaterialActor):
    def __init__(self, world, size, static=False, **kwargs):
        super(Box, self).__init__(world, **kwargs)

        shapeDef = b2d.b2PolygonDef()
        shapeDef.SetAsBox(*size)
        shapeDef.density = 1
        shapeDef.restitution = 0.8

        self.applyShapeAttrs(shapeDef)

        shape = self.body.CreateShape(shapeDef)

        if not static:
            self.body.SetMassFromShapes()



    def draw(self, graphics):
        shape = self.body.GetShapeList()[0]
        points = map(self.body.GetWorldPoint, shape.getVertices_tuple())
        graphics.polygon((200,10,100), points)


class Helicopter(Ball):
    def __init__(self, level, world, radius, **kwargs):
        super(Helicopter, self).__init__(world, radius, **kwargs)
        self.level = level
        self.spr_name = './sprites/heli.png'

    def draw(self, graphics):
        #super(Helicopter, self).draw(graphics)
        right = utils.rotate(b2d.b2Vec2(-1,0), self.level.world_angle.get())
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
