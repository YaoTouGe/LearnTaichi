from matplotlib.pyplot import draw_if_interactive
import taichi as ti
from datatypes import *

@ti.func
def reflect(input_dir, normal):
    out = input_dir.dot(normal) * 2 - input_dir
    return out.normalized()

@ti.func
def test_AABB(ray, min, max, t_min:float, t_max:float):
    dir_inv = 1 / ray.dir
    min_ts = (min - ray.origin) * dir_inv
    max_ts = (max - ray.origin) * dir_inv
    return ti.max(min_ts.max(),t_min) < ti.min(max_ts.min(), t_max)

@ti.func
def intersect_AABB(ray, aabb, t_min:float, t_max:float, rec: ti.template()):
    pass

@ti.func
def intersect_sphere(r, sphere, t_min:float, t_max:float, rec: ti.template()):
    oc = r.origin - sphere.center
    a = r.dir.dot(r.dir)
    half_b = r.dir.dot(oc)
    c = oc.dot(oc) - sphere.radius * sphere.radius

    discriminant = half_b * half_b - a * c
    ret = True
    if discriminant < 0:
        ret = False

    discrimSqrt = ti.sqrt(discriminant)
    t = (-half_b - discrimSqrt) / a
    if (t < t_min or t > t_max):
        t = (-half_b + discrimSqrt) / a
        if (t < t_min or t > t_max):
            ret = False
    
    rec.hit_pos = r.origin + r.dir * t
    rec.normal = (rec.hit_pos - sphere.center).normalized()
    rec.material = sphere.material
    rec.is_front = rec.normal.dot(r.dir) > 0 
    rec.t = t
    return ret

@ti.func
def extract_sphere(geom):
    return sphere(center=geom.data[0:3], radius=geom.data[3], material=geom.material)

@ti.func
def intersect_geom(r, geom, t_min:float, t_max:float, rec: ti.template()):
    # TODO: switch geometry type
    return intersect_sphere(r, extract_sphere(geom),t_min, t_max, rec)

@ti.func
def random_float(min, max):
    return min + ti.random(float) * (max - min + 0.000001)

@ti.func
def random_in_unit_sphere():
    dir = vec3(0)
    while True:
        x = random_float(-1, 1)
        y = random_float(-1, 1)
        z = random_float(-1, 1)

        dir = vec3(x, y, z)
        if dir.dot(dir) <= 1:
            break
    return dir

@ti.func
def random_on_unit_sphere():
    return random_in_unit_sphere().normalized()

@ti.func
def material_scatter(r, rec, material_field, scatter_dir:ti.template(), color:ti.template()):
    # TODO: switch material type
    mat = material_field[rec.material]
    color = mat.color

    scatter_dir = rec.normal + random_on_unit_sphere()

@ti.func
def ray_color(r, bvh_field, geom_field, material_field, max_depth:int, bg_color):
    ret = vec3(1, 1, 1)

    depth = 0
    while depth < max_depth:
        rec = hit_record(0)
        # intersect bvh
        if not bvh_intersect(r, bvh_field, geom_field, 0.0001, 999999, rec):
            ret = bg_color
            break
        
        # material response
        scattered = vec3(0)
        attenuation = vec3(0)
        material_scatter(r, rec, material_field, scattered, attenuation)
        # color accumulate
        ret = ret * attenuation
        r = ray(origin = rec.hit_pos, dir = scattered)
        depth += 1

    if depth >= max_depth:
        ret = vec3(0, 0, 0)
    
    return vec4(ret, 1)

@ti.func
def bvh_intersect(r, bvh_field, geom_field, t_min, t_max, rec: ti.template()):
    # start from root node
    ret = False
    cur_node = 0
    while cur_node >= 0:
        node = bvh_field[cur_node]

        if not test_AABB(r, node.min, node.max, t_min, t_max):
            cur_node = node.next
            continue
        
        # leaf node, intersect with geometry
        if node.geometryIdx != -1:
            local_rec = hit_record(0)
            if intersect_geom(r, geom_field[node.geometryIdx], t_min, t_max, local_rec):
                ret = True
                if local_rec.t < t_max:
                    rec = local_rec
                    t_max = local_rec.t

            cur_node = node.next
        else:
            cur_node = node.leftChild

    return ret
