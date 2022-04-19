import taichi as ti

@ti.func
def reflect(input_dir, normal):
    out = input_dir.dot(normal) * 2 - input_dir
    return out.normalized()


@ti.func
def intersct_sphere(ray, sphere, tMin, tMax, rec: ti.template()):
    oc = ray.center - sphere.center
    a = ray.dir.dot(ray.dir)
    half_b = ray.dir.dot(oc)
    c = oc.dot(oc) - sphere.radius * sphere.radius

    discriminant = half_b * half_b - a * c
    ret = 1
    if discriminant < 0:
        ret = 0

    discrimSqrt = ti.sqrt(discriminant)
    t = (-half_b - discrimSqrt) / a
    if (t < tMin or t > tMax):
        t = (-half_b + discrimSqrt) / a
        if (t < tMin or t > tMax):
            ret = 0
    rec.hit_pos = ray.center + ray.dir * t
    rec.normal = (rec.hit_pos - sphere.center).normalized()
    return ret
