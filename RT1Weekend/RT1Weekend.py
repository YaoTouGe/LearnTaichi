import taichi as ti
from datatypes import *
import rtutil
import scene

width = 1280
height = 720
ti.init(arch=ti.gpu)
camPos = ti.Vector([0, 0, 1])

pixels = vec4.field(shape=(width, height))

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

bvh_field, geom_field, material_field = scene.build_scene_bvh()

@ti.kernel
def ray_trace(width:int, height:int):
    aspect_ratio = float(width) / height

    for i in range(width * height):
        x = i % width
        y = int(i / width)
        dir = (ti.Vector([(x / width - 0.5) * aspect_ratio, y / height - 0.5, 0]) - camPos).normalized()
        r = ray(origin=camPos, dir=dir)
        pixels[x, y] = rtutil.ray_color(r, bvh_field, geom_field, material_field, 50, vec3(1, 0, 1))

while window.running:
    ray_trace(width, height)
    canvas.set_image(pixels)
    window.show()
