from __future__ import annotations
import copy
from enum import IntEnum
from material import Material
from datatypes import *

class GeomType(IntEnum):
    SPHERE = 0
    AABB = 1
    XYRECT = 2
    XZRect = 3
    YZRect = 4

class AABB():
    def __init__(self, min: vec3, max:vec3) -> None:
        self.min = min
        self.max = max
        self.center = min + max / 2

    def combine(self, other:AABB):
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)
        self.center = self.min + self.max / 2

def combine_bbox(l:AABB, r:AABB):
    ret = copy.deepcopy(l)
    ret.combine(r)
    return ret

# hittable geometry data
class RectXY:
    def __init__(self, x0, y0, x1, y1, z) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.z = z

    def bbox(self):
        return AABB(vec3(self.x0, self.y0, self.z - 0.01), vec3(self.x1, self.y1, self.z + 0.01))

class RectXZ:
    def __init__(self, x0, z0, x1, z1, y) -> None:
        self.x0 = x0
        self.z0 = z0
        self.x1 = x1
        self.z1 = z1
        self.y = y

    def bbox(self):
        return AABB(vec3(self.x0, self.y - 0.01, self.z0), vec3(self.x1, self.y + 0.01, self.z1))

class RectYZ:
    def __init__(self, y0, z0, y1, z1, x) -> None:
        self.y0 = y0
        self.z0 = z0
        self.y1 = y1
        self.z1 = z1
        self.x = x

    def bbox(self):
        return AABB(vec3(self.x - 0.01, self.y0, self.z0), vec3(self.x + 0.01, self.y1, self.z1))

class Sphere:
    def __init__(self, origin: vec3, radius: float, material:Material) -> None:
        self.origin = origin
        self.radius = radius
        self.material = material.id()
    def bbox(self):
        return AABB(self.origin - self.radius, self.origin + self.radius)

    def transfer(self):
        return geometry(type=0, material=self.material, data=vec9(self.origin, self.radius, vec5(0)))

class RenderableAABB(AABB):
    def __init__(self, aabb) -> None:
        super().__init__(aabb.min, aabb.max)
    def bbox(self):
        return AABB(super().min, super().max)