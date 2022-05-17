import taichi as ti
import bvh

@ti.func
def reflect(input_dir, normal):
    out = input_dir.dot(normal) * 2 - input_dir
    return out.normalized()

@ti.func
def test_AABB(ray, min, max):
    pass

@ti.func
def intersect_AABB(ray, min, max, rec: ti.template()):
    pass

@ti.func
def intersct_sphere(ray, sphere, tMin, tMax, rec: ti.template()):
    oc = ray.center - sphere.center
    a = ray.dir.dot(ray.dir)
    half_b = ray.dir.dot(oc)
    c = oc.dot(oc) - sphere.radius * sphere.radius

    discriminant = half_b * half_b - a * c
    ret = True
    if discriminant < 0:
        ret = False

    discrimSqrt = ti.sqrt(discriminant)
    t = (-half_b - discrimSqrt) / a
    if (t < tMin or t > tMax):
        t = (-half_b + discrimSqrt) / a
        if (t < tMin or t > tMax):
            ret = False
    rec.hit_pos = ray.center + ray.dir * t
    rec.normal = (rec.hit_pos - sphere.center).normalized()
    return ret

@ti.func
def ray_color(ray, bvh_field, gem_field, max_depth):
    stack_top = 0
    stack_data = bvh.vec3.field()
    pass

@ti.func
def bvh_intersect(ray, bvh_field, gem_field, t_min, t_max, rec: ti.template()):
    pass
