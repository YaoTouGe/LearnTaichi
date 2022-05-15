from bvh import *
import taichi as ti
import rtutil
import bvh

width = 1280
height = 720
ti.init(arch=ti.gpu)
camPos = ti.Vector([0, 0, 1])

ray = ti.types.struct(center = vec3, dir = vec3)
hit_record = ti.types.struct(hit_pos = vec3, normal = vec3)

pixels = vec4.field(shape=(width, height))

@ti.kernel
def ray_trace(width:int, height:int, bvh_field, geom_field):
    center = ti.Vector([0, 0, -5])
    radius = 2
    aspect_ratio = float(width) / height
    rec = hit_record(hit_pos=vec3(0), normal=vec3(0))

    for i in range(width * height):
        x = i % width
        y = int(i / width)
        dir = (ti.Vector([(x / width - 0.5) * aspect_ratio, y / height - 0.5, 0]) - camPos).normalized()
        r = ray(center=camPos, dir=dir)

        if rtutil.intersct_sphere(r, sphere(center=center, radius=radius), 0.001, 99999, rec) > 0:
            pixels[x, y] = vec4(rec.normal + vec3([0.5, 0.5, 0.5]), 1)
        else:
            pixels[x, y] = ti.Vector([0, 0, 0, 1])

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

bvh_field, geom_field = bvh.build_scene_bvh()

while window.running:
    ray_trace(width, height, bvh_field, geom_field)
    canvas.set_image(pixels)
    window.show()
