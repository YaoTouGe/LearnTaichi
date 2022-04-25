from __future__ import annotations
import taichi as ti
import copy

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
    int geometryIdx;
}
'''

vec7 = ti.types.vector(7, float)
vec4 = ti.types.vector(4, float)
vec3 = ti.types.vector(3, float)
vec2 = ti.types.vector(2, float)
bvhnode = ti.types.struct(min = vec3, max = vec3, leftChild = int, rightChild = int, geometryIdx = int)
sphere = ti.types.struct(center = vec3, radius = float)


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
    def __init__(self, obj_list, axis: int = 0) -> None:
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

def traversal_fill(geometries: ti.Field, treenodes: ti.Field, bvh :BVHNode):
    # only leaf node's obj is not None
    if bvh.obj != None:
        pass

def traversal_count(bvh: BVHNode):
    if bvh == None:
        return 0, 0
    # leaf node
    if bvh.obj != None:
        return 1, 1

    l_node, l_obj = traversal_count(bvh.leftChild)
    r_node, r_obj = traversal_count(bvh.leftChild)

    return l_node + r_node + 1, l_obj + r_obj

def build_bvh():
    scene_objs = []

    scene_objs.append(Sphere(vec3(0, -1, 0), 1))
    scene_objs.append(Sphere(vec3(0, 1, 0), 1))

    bvh = BVHNode(scene_objs)
    node_count, obj_count = traversal_count(bvh)

    print(node_count, obj_count)

if __name__ == "__main__":
    build_bvh()
