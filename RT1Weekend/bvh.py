from geom import *
import colorful

'''
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
    // next bvh node id for back tracing
    int next;
    // parent index
    int parent
}
'''

bvhnode = ti.types.struct(min = vec3, max = vec3, leftChild = int, rightChild = int, geometryIdx = int, next = int, parent = int)

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
    def __init__(self, obj_list, axis: int = 0, parent = None) -> None:
        self.leftChild = None
        self.rightChild = None
        self.bbox = None
        self.obj = None
        next_axis = (axis + 1) % 3
        self.parent = parent

        length = len(obj_list)
        if length == 0:
            return
        elif length == 1:
            self.obj = obj_list[0]
            self.bbox = self.obj.bbox()
            return
        elif length == 2:
            self.leftChild = BVHNode([obj_list[0]], next_axis, self)
            self.rightChild = BVHNode([obj_list[1]], next_axis, self)
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

            self.leftChild = BVHNode(left_obj, next_axis, self)
            self.rightChild = BVHNode(right_obj, next_axis, self)
        self.bbox = combine_bbox(self.leftChild.bbox, self.rightChild.bbox)
