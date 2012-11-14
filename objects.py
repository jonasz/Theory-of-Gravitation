import Box2D as b2d
import pygame.image
import utils
import math

class Actor(object):
    body = None
    def __init__(self, world, **kwargs):
        self.world = world
        self.shape_attrs = {}

    def applyShapeAttrs(self, shape):
        for (k,v) in self.shape_attrs.items():
            print 'apply', k, v
            setattr(shape, k, v)
            print shape.restitution

    def createBody(self, **kwargs):
        bodyDef = b2d.b2BodyDef()

        for (k,v) in kwargs.items():
            if k in ['position', 'angle', 'fixedRotation']:
                setattr(bodyDef, k, v)
            else:
                self.shape_attrs[k] = v

        self.body = self.world.CreateBody(bodyDef)
        self.body.SetUserData(self)

    def draw(self, graphics): raise NotImplementedError

    def isMainCharacter(self):
        return False


class Ball(Actor):
    def __init__(self, world, radius, **kwargs):
        super(Ball, self).__init__(world)
        self.createBody(**kwargs)

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


class Box(Actor):
    def __init__(self, world, size, static=False, **kwargs):
        super(Box, self).__init__(world)
        self.createBody(**kwargs)
        self.size = size

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
