import taichi as ti
import rtutil

width = 1280
height = 720
ti.init(arch=ti.gpu)
camPos = ti.Vector([0, 0, 1])

vec4 = ti.types.vector(4, float)
vec3 = ti.types.vector(3, float)
vec2 = ti.types.vector(2, float)

ray = ti.types.struct(center = vec3, dir = vec3)
sphere = ti.types.struct(center = vec3, radius = float)
hit_record = ti.types.struct(hit_pos = vec3, normal = vec3)

pixels = vec4.field(shape=(width, height))

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
        if rtutil.intersct_sphere(ray(center=camPos, dir=dir), sphere(center=center, radius=radius), 0.001, 99999, rec) > 0:
            pixels[x, y] = vec4(rec.normal + vec3([0.5, 0.5, 0.5]), 1)
        else:
            pixels[x, y] = ti.Vector([0, 0, 0, 1])

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

while window.running:
    ray_trace(width, height)
    canvas.set_image(pixels)
    window.show()
