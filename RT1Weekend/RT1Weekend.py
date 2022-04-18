from turtle import shape
import taichi as ti

width = 1280
height = 720
camPos = ti.Vector([0, 0, 1])

vec3 = ti.types.vector(3, float)
vec2 = ti.types.vector(2, float)

ray = ti.types.struct(center = vec3, dir = vec3)
sphere = ti.types.struct(center = vec3, radius = float)
hit_record = ti.types.struct(hit_pos = vec3, normal = vec3)

ti.init(arch=ti.gpu)
pixels = vec3.field(shape=(width, height))
gui = ti.GUI("hello taichi", (width, height))

@ti.func
def intersct_sphere(ray, sphere, tMin, tMax, rec:ti.template()):
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

@ti.kernel
def ray_trace(width:int, height:int):
    center = ti.Vector([0, 0, -5])
    radius = 2
    aspect_ratio = float(width) / height
    rec = hit_record(hit_pos=vec3(0), normal=vec3(0))

    for i in range(width * height):
        x = i % width
        y = int(i / width)
        dir = (ti.Vector([(x / width - 0.5) * aspect_ratio, y / height - 0.5, 0]) - camPos).normalized()
        if intersct_sphere(ray(center=camPos, dir=dir), sphere(center=center, radius=radius), 0.001, 99999, rec) > 0:
            pixels[x, y] = rec.normal + vec3([0.5, 0.5, 0.5])
        else:
            pixels[x, y] = ti.Vector([0, 0, 0])

while gui.running:
    ray_trace(width, height)
    gui.set_image(pixels)
    gui.show()
