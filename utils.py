import Box2D as b2d
import time
import math
import pygame.image
import heapq

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

class Enum:
    def __init__(self, *args):
        num = 0
        for val in args:
            setattr(self, val, num)
            num += 1

class PriorityQueue:
    def __init__(self, elems = []):
        self.elems = elems[:]
        heapq.heapify(self.elems)
    def empty(self):
        return len(self.elems)==0
    def push(self, elem):
        heapq.heappush(self.elems, elem)
    def top(self):
        return self.elems[0]
    def pop(self):
        return heapq.heappop(self.elems)
    def size(self):
        return len(self.elems)


class RepeatingAction_:
    next_id = (i for i in xrange(10**9))
    id = None
    nextTime = None
    interval = None
    callsLeft = None
    fun = None
    def __init__(self, nextTime, interval, callsLeft, fun):
        self.id = self.next_id.next()
        self.nextTime = nextTime
        self.interval = interval
        self.callsLeft = callsLeft
        self.fun = fun

    def performOnce(self):
        if self.callsLeft == 0: return
        self.nextTime += self.interval
        if self.callsLeft > 0: self.callsLeft -= 1
        self.fun()

    def __le__(self, rh):
        return self.nextTime < rh.nextTime


# A lazy function scheduler
# (one has to call 'work' in order to perform every scheduled job)
class FunsctionScheduler:
    def __init__(self):
        self.actions = PriorityQueue()

    def addRepeatingAction_(self, action):
        self.actions.push(action)

    def addAction(self, fun, delay = 0, interval = 1, callsNo = 1):
        a = RepeatingAction_(
                nextTime = time.time() + delay,
                interval = interval,
                callsLeft = callsNo,
                fun = fun)
        self.addRepeatingAction_(a)
        return a.id

    def work(self):
        toPerform = []
        now = time.time()

        while (not self.actions.empty()) and self.actions.top().nextTime < now:
            toPerform.append(self.actions.pop())

        for action in toPerform:
            while action.callsLeft != 0 and action.nextTime < now:
                action.performOnce()
            if action.callsLeft != 0:
                self.addRepeatingAction_(action)

    # this should be optimized if we want to keep a large number of action
    # inside the scheduler
    def cancel(self, actionId):
        found = False
        for action in self.actions.elems:
            if action.id == actionId:
                action.fun = lambda: None
                action.callsLeft = 0
                found = True
                break

        if not found:
            print 'warning, trying to delete non-existing action',actionId


# A utility class to allow simple job starting and stopping.
# Useful for example for an action that happens continuously between
# KEYDOWN and KEYUP events
class ContinuousAction:
    actionId = None
    def __init__(self, repeater, fun, interval = 1.):
        self.repeater = repeater
        self.fun = fun
        self.interval = interval

    def start(self):
        assert not self.actionId
        self.actionId = self.repeater.addAction(
                fun = self.fun, interval = self.interval, callsNo = -1)

    def stop(self):
        self.repeater.cancel(self.actionId)
        self.actionId = None


class Singleton(type):
    def __init__(cls, *args):
        super(Singleton, cls).__init__(*args)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance
