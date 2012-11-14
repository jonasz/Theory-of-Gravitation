import Box2D as b2d
import time
import math
import pygame.image

def memoized(fun):
    mem = {}
    def g(*args):
        try:
            return mem[args]
        except KeyError:
            x = fun(*args)
            mem[args] = x
            return x
    return g

@memoized
def get_bitmap_(path, w, h, flipX, flipY):
    surf = pygame.image.load(path)
    surf = pygame.transform.scale(surf, (w, h))
    if flipX or flipY:
        surf = pygame.transform.flip(surf, flipX, flipY)
    return surf

def get_bitmap(path, w, h, flipX=False, flipY=False):
    return get_bitmap_(path,w,h,flipX,flipY)

def rotate(vec, angle, center = b2d.b2Vec2(0,0)):
    res = vec.copy()
    res -= center
    res = b2d.b2Mul(b2d.b2Mat22(angle), res)
    res += center
    return res

def angle_between(vec1, vec2):
    vec1 = vec1.copy()
    vec2 = vec2.copy()
    cos = (vec1.dot(vec2) / vec1.Length() / vec2.Length())
    if cos<-1: cos = -1.
    if cos>1: cos = 1.
    angle = math.acos(cos)
    if vec1.cross(vec2)<0: return -angle
    else: return angle

class SmoothChanger:
    value_ = 0.

    old_value_ = 0.
    goal_value_ = 0.

    old_time_ = 0.
    goal_time_ = 0.

    def __init__(self, value):
        self.value_ = value
        self.goal_value_ = value

    def init_change(self, delta_value, delta_time = 0.5):
        self.old_value_ = self.value_
        self.goal_value_ += delta_value

        self.old_time_ = time.time()
        self.goal_time_ = self.old_time_ + delta_time

    def step(self):
        now = time.time()
        if now > self.goal_time_:
            self.value_ = self.goal_value_
            return

        perc = (now - self.old_time_) / (self.goal_time_ - self.old_time_)
        delta = self.goal_value_ - self.old_value_
        delta *= math.sin(math.pi/2 * perc)
        #delta *= perc
        self.value_ = self.old_value_ + delta

    def get(self, increment = False):
       if increment: self.step()
       return self.value_
