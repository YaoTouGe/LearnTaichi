from random import random, seed
from material import *
from bvh import *
import colorful

def traversal_count(bvh: BVHNode):
    if bvh == None:
        return 0, 0
    # leaf node
    if bvh.obj != None:
        return 1, 1

    l_node, l_obj = traversal_count(bvh.leftChild)
    r_node, r_obj = traversal_count(bvh.rightChild)

    return l_node + r_node + 1, l_obj + r_obj

def build_bvh_array(bvh, bvh_node_field, node_idx, geometry_field, geo_idx, parent_idx):
    if bvh == None:
        return

    bvh_node_data = bvhnode(min=bvh.bbox.min, max=bvh.bbox.max, leftChild=-1, rightChild=-1, geometryIdx=-1, next=-1, parent = parent_idx)
    idx = node_idx[0]
    node_idx[0] += 1
    
    if bvh.obj != None:
        geometry_field[geo_idx[0]] = bvh.obj.transfer()
        bvh_node_data.geometryIdx = geo_idx[0]
        geo_idx[0]+=1
        bvh_node_field[idx] = bvh_node_data
        return

    if bvh.leftChild != None:
        bvh_node_data.leftChild = node_idx[0]
        build_bvh_array(bvh.leftChild, bvh_node_field, node_idx, geometry_field, geo_idx, idx)

    if bvh.rightChild != None:
        bvh_node_data.rightChild = node_idx[0]
        build_bvh_array(bvh.rightChild, bvh_node_field, node_idx, geometry_field, geo_idx, idx)
    bvh_node_field[idx] = bvh_node_data

def get_next(bvh_field, cur):
    ret = -1

    while cur != -1:
        bvh_data = bvh_field[cur]
        if bvh_data.parent != -1:
            if bvh_field[bvh_data.parent].rightChild != cur:
                ret = bvh_field[bvh_data.parent].rightChild
                break

        cur = bvh_data.parent
    return ret

def fill_bvh_next(bvh_field, cur):
    if cur == -1:
        return
    bvh_data = bvh_field[cur]
    bvh_field[cur].next = get_next(bvh_field, cur)

    fill_bvh_next(bvh_field, bvh_data.leftChild)
    fill_bvh_next(bvh_field, bvh_data.rightChild)

def build_scene_bvh():
    colorful.print_header("======build bvh data========")
    scene_objs = []

    mat_table = MaterialTable(10)

    gray = Material(MaterialType.DIFFUSE, vec3(0.7, 0.7, 0.7), mat_table)
    green = Material(MaterialType.DIFFUSE, vec3(0.2, 0.5, 0.2), mat_table)
    red = Material(MaterialType.DIFFUSE, vec3(0.5, 0.2, 0.2), mat_table)
    blue = Material(MaterialType.DIFFUSE, vec3(0.2, 0.2, 0.5), mat_table)

    scene_objs.append(Sphere(vec3(0, -202, -10), 200, gray))
    # scene_objs.append(Sphere(vec3(0, 0, -10), 2, green))
    
    seed(450468524)
    color_list = [blue, green, red, gray]
    for i in range(500):
        x = random() * -100 + 50
        z = random() * -100
        y = random() * 6 - 3

        color = int(random() * 10 // 3)
        mat = color_list[color]
        scene_objs.append(Sphere(vec3(x, y, z), 1.5, mat))


    bvh = BVHNode(scene_objs)
    node_count, obj_count = traversal_count(bvh)

    colorful.print_bold(f"node count: {node_count}, geometry count: {obj_count}\nflatten bvh data")

    # after counting, build bvh data
    bvh_field = bvhnode.field(shape=(node_count,))
    geometry_field = geometry.field(shape=(obj_count,))
    build_bvh_array(bvh, bvh_field, [0], geometry_field, [0], -1)
    fill_bvh_next(bvh_field, 0)

    return bvh_field, geometry_field, mat_table.data()

if __name__ == "__main__":
    ti.init(arch=ti.gpu)
    build_scene_bvh()
