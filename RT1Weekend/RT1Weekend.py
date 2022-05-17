import taichi as ti
from datatypes import *
import rtutil
import scene

width = 2560
height = 1440
ti.init(arch=ti.gpu)
camPos = ti.Vector([0, 0, 1])

pixels = vec4.field(shape=(width, height))

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

bvh_field, geom_field, material_field = scene.build_scene_bvh()

@ti.kernel
def ray_trace(width:int, height:int, prev_count:int, frame_count_inv:float):
    aspect_ratio = float(width) / height

    for i in range(width * height):
        
        x = i % width + ti.random(float)
        y = int(i / width)  + ti.random(float)

        dir = (ti.Vector([(x / width - 0.5) * aspect_ratio, y / height - 0.5, 0]) - camPos).normalized()
        r = ray(origin=camPos, dir=dir)

        # bg color
        t = 0.5 * (dir.y + 1)
        bg_color = (1.0-t)*vec3(1.0, 1.0, 1.0) + t*vec3(0.5, 0.7, 1.0)

        new_sample = rtutil.ray_color(r, bvh_field, geom_field, material_field, 50, bg_color)
        pixels[x, y] = (pixels[x, y] * prev_count + new_sample) * frame_count_inv

frame_count = 0
while window.running:
    ray_trace(width, height, frame_count, 1 / (frame_count + 1))
    canvas.set_image(pixels)
    window.show()
    frame_count += 1
