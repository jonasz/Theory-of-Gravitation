import Box2D as b2d
import math

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
    return math.acos(cos)

class smoothChanger:
    value_ = 0.
    old_value_ = 0.
    goal_value_ = 0.
    steps_done_ = 0
    steps_ = 10

    @property
    def value(self):
        return self.value_

    def __init__(self, value):
        self.value_ = value
        self.goal_value_ = value

    def init_change(self, delta_value, steps):
        self.steps_ = steps
        self.steps_done_ = 0
        self.old_value_ = self.value_
        self.goal_value_ += delta_value

    def step(self):
        if self.steps_done_ == self.steps_:
            self.value_ = self.goal_value_
            return

        self.steps_done_ += 1

        delta = self.goal_value_ - self.old_value_
        delta *= math.sin(math.pi/2 * self.steps_done_ / self.steps_)
        #delta *= 1.*self.steps_done_ / self.steps_
        self.value_ = self.old_value_ + delta
