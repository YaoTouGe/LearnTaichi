from functools import singledispatch
from __future__ import annotations
import taichi as ti

class Vec3:
    def __init__(self, other:Vec3) -> None:
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def __init__(self, x = 0, y = 0, z = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    @singledispatch
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    @singledispatch
    def __add__(self, other: float):
        return Vec3(self.x + other, self.y + other, self.z + other)

    @singledispatch
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    @singledispatch
    def __sub__(self, other: float):
        return Vec3(self.x - other, self.y - other, self.z - other)

    @singledispatch
    def __mul__(self, other):
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    @singledispatch
    def __mul__(self, other:float):
        return Vec3(self.x * other, self.y * other, self.z * other)

    @singledispatch
    def __truediv__(self, other):
        return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)

    @singledispatch
    def __truediv__(self, other: float):
        return Vec3(self.x / other, self.y / other, self.z / other)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
        
    def cross(self, other):
        return Vec3(self.y * other.z - other.y - self.z, -(self.x * other.z - other.x * self.z), self.x * other.y - other.x - self.y)

def minVec3(v1: Vec3, v2: Vec3):
    return Vec3(min(v1.x, v2.x), min(v1.y, v2.y), min(v1.z, v2.z))

def maxVec3(v1: Vec3, v2: Vec3):
    return Vec3(max(v1.x, v2.x), max(v1.y, v2.y), max(v1.z, v2.z))

class AABB:
    def __init__(self, other:AABB) -> None:
        self.min = other.min
        self.max = other.max
        self.center = other.center

    def __init__(self, min: Vec3 = Vec3(), max:Vec3 = Vec3()) -> None:
        self.min = min
        self.max = max
        self.center = min + max / 2

    def combine(self, other:AABB):
        self.min = minVec3(self.min, other.min)
        self.max = maxVec3(self.max, other.max)
        self.center = self.min + self.max / 2

def combine_bbox(l, r):
    ret = AABB(l)
    return ret.combine(r)

def objcmp_x(l, r):
    if l.center.x < r.center.x:
        return -1
    if l.center.x > r.center.x:
        return 1
    return 0

def objcmp_y(l, r):
    if l.center.y < r.center.y:
        return -1
    if l.center.y > r.center.y:
        return 1
    return 0

def objcmp_z(l, r):
    if l.center.z < r.center.z:
        return -1
    if l.center.z > r.center.z:
        return 1
    return 0

class BVHNode:
    def __init__(self, obj_list, axis: int) -> None:
        self.leftChild = None
        self.rightChild = None
        self.bbox = None

        self.obj = None

        next_axis = (axis + 1) % 3

        length = len(obj_list)
        if length == 0:
            return
        elif length == 1:
            self.obj = obj_list[0]
            self.bbox = self.obj.bbox()
            return
        elif length == 2:
            self.leftChild = BVHNode([obj_list[0]], next_axis)
            self.rightChild = BVHNode([obj_list[1]], next_axis)
        else:
            cmp = objcmp_x
            if axis == 1:
                cmp = objcmp_y
            elif axis == 2:
                cmp = objcmp_z

            sorted_list = sorted(obj_list, cmp)
            mid = length // 2

            left_obj = sorted_list[0:mid]
            right_obj = sorted_list[mid + 1:]

            self.leftChild = BVHNode(left_obj, next_axis)
            self.rightChild = BVHNode(right_obj, next_axis)
        self.bbox = combine_bbox(self.leftChild.bbox, self.rightChild.bbox)

# hittable geometry data
class RectXY:
    def __init__(self, x0, y0, x1, y1, z) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.z = z

    def bbox(self):
        return AABB(Vec3(self.x0, self.y0, self.z - 0.01), Vec3(self.x1, self.y1, self.z + 0.01))

class RectXZ:
    def __init__(self, x0, z0, x1, z1, y) -> None:
        self.x0 = x0
        self.z0 = z0
        self.x1 = x1
        self.z1 = z1
        self.y = y

    def bbox(self):
        return AABB(Vec3(self.x0, self.y - 0.01, self.z0), Vec3(self.x1, self.y + 0.01, self.z1))

class RectYZ:
    def __init__(self, y0, z0, y1, z1, x) -> None:
        self.y0 = y0
        self.z0 = z0
        self.y1 = y1
        self.z1 = z1
        self.x = x

    def bbox(self):
        return AABB(Vec3(self.x - 0.01, self.y0, self.z0), Vec3(self.x + 0.01, self.y1, self.z1))

class Sphere:
    def __init__(self, origin, radius) -> None:
        self.origin = origin
        self.radius = radius
    def bbox(self):
        return AABB(self.origin - self.radius, self.origin + self.radius)

class RenderableAABB(AABB):
    def __init__(self, aabb) -> None:
        super().__init__(aabb)
    def bbox(self):
        return AABB(super())

'''
naive design of BVH

geometry type layout:
// vec7
struct
{
    float type; // 0 sphere 1 AABB 2 XYRect 3 XZRect 4 YZRect
    union
    {
        // sphere
        struct
        {
            vec4; // vec3 center float radius 
        };

        // AABB
        struct
        {
            vec6; // vec3 min vec3 max
        };

        // XY/XZ/YZ Rect
        struct
        {
            vec5; // vec2 min vec2 max float axis 
        };
    };
};

material type layout:
// materials
struct
{
    int type; // material type: 0 diffuse 1 specular 2 dielect 3 light
}

BVH node layout:
struct
{
    // bounding box
    vec3 min;
    vec3 max;

    // child node id in node array
    int leftChild;
    int rightChild;
    // geometry id in geometry array
    int geometry;
}
'''
def build_bvh(geometries: ti.field, treenodes: ti.Field):
    scene_objs = []

    scene_objs.append(Sphere(Vec3(0, -1, 0), 1))
    scene_objs.append(Sphere(Vec3(0, 1, 0), 1))

    return scene_objs
