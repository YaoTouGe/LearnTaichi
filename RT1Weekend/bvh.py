from matplotlib.pyplot import axis
from geom import *

class BVHNode:
    def __init__(self, obj_list, parent = None) -> None:
        self.leftChild = None
        self.rightChild = None
        self.bbox = None
        self.obj = None
        self.parent = parent

        length = len(obj_list)
        if length == 0:
            return
        elif length == 1:
            self.obj = obj_list[0]
            self.bbox = self.obj.bbox()
            return
        elif length == 2:
            self.leftChild = BVHNode([obj_list[0]], self)
            self.rightChild = BVHNode([obj_list[1]], self)
        else:
            # find longest axis
            total_bound = obj_list[0].bbox()
            for o in obj_list:
                total_bound.combine(o.bbox())
            size = total_bound.size()

            axis = 0
            max_len = size[0]
            for i in range(1, 3):
                if size[i] > max_len:
                    max_len = size[i]
                    axis = i
                    

            key_func = lambda o: o.center.x
            if axis == 1:
                key_func = lambda o: o.center.y
            elif axis == 2:
                key_func = lambda o: o.center.z

            sorted_list = sorted(obj_list, key=key_func)
            mid = length // 2

            left_obj = sorted_list[0:mid]
            right_obj = sorted_list[mid:]

            self.leftChild = BVHNode(left_obj, self)
            self.rightChild = BVHNode(right_obj, self)
        self.bbox = combine_bbox(self.leftChild.bbox, self.rightChild.bbox)
