import taichi as ti
from datatypes import *
import rtutil
import scene
from camera import RTCamera

class FrameState:
    def __init__(self, max_depth:int) -> None:
        self.frame_count = 0
        self.max_depth = max_depth

width = 1280
height = 720

# ti.aot.start_recording("rt.yml")
ti.init(arch=ti.vulkan)
cam =  RTCamera(2, width, height, ti.Vector([0, 0, 1]), ti.Vector([0, 0, 0]))

frame_state = FrameState(10)
pixels = vec4.field(shape=(width, height))

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

bvh_field, geom_field, material_field = scene.build_scene_bvh()

@ti.func
def get_ray(cam_param, x, y, width, height):
    aspect_ratio = float(width) / height
    focal_len = cam_param[0]
    cam_pos = cam_param[1:4]
    forward = cam_param[4:7]
    right = cam_param[7:10]
    up = cam_param[10:13]

    u = (x / width * 2 - 1) * aspect_ratio
    v = y / height * 2 - 1
    ray_dir = (forward * focal_len + u * right + v * up).normalized()
    return ray(origin=cam_pos, dir=ray_dir)

@ti.kernel
def ray_trace(width:int, height:int, prev_count:int, frame_count_inv:float, max_depth:int, cam_param:vec13):
    for i in range(width * height):
        px = i % width
        py = i // width

        x = px + ti.random(float)
        y = py + ti.random(float)

        r = get_ray(cam_param, x, y, width, height)

        # bg color
        t = 0.5 * (r.dir.y + 1)
        bg_color = (1.0-t)*vec3(1.0, 1.0, 1.0) + t*vec3(0.5, 0.7, 1.0)

        new_sample = rtutil.ray_color(r, bvh_field, geom_field, material_field, max_depth, bg_color)
        pixels[px, py] = (pixels[px, py] * prev_count + new_sample) * frame_count_inv

def clear(frame_state):
    frame_state.frame_count = 0
    pixels.fill(0)

while window.running:
    window.GUI.begin("info", 0, 0, 0.2, 0.2)
    window.GUI.text(f"frame count: {frame_state.frame_count}")
    window.GUI.text(f"max depth: {frame_state.max_depth}")
    # is_clicked = window.GUI.button(name)
    # new_value = window.GUI.slider_float(name, old_value, min_value, max_value)
    # new_color = window.GUI.color_edit_3(name, old_color)
    window.GUI.end()

    if window.get_event(ti.ui.PRESS):
        if window.event.key in [ti.ui.UP, ti.ui.DOWN, ti.ui.LEFT, ti.ui.RIGHT, 'a', 'd', 'w', 's']:
            clear(frame_state)

        if window.event.key == ti.ui.UP:
            frame_state.max_depth += 1
        elif window.event.key == ti.ui.DOWN:
            frame_state.max_depth -= 1
        elif window.event.key == ti.ui.LEFT:
            cam.focal_len -= 0.1
        elif window.event.key == ti.ui.RIGHT:
            cam.focal_len += 0.1
        elif window.event.key == 'a':
            cam.move(vec2(-0.1, 0))
        elif window.event.key == 'd':
            cam.move(vec2(0.1, 0))
        elif window.event.key == 'w':
            cam.move(vec2(0, 0.1))
        elif window.event.key == 's':
            cam.move(vec2(0, -0.1))

    ray_trace(width, height, frame_state.frame_count, 1 / (frame_state.frame_count + 1), frame_state.max_depth, cam.dump())
    canvas.set_image(pixels)
    window.show()
    frame_state.frame_count += 1
