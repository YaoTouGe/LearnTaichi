from enum import IntEnum
import taichi as ti
from datatypes import *
import rtutil
import scene
import colorful
from camera import RTCamera
import copy

class FrameState:
    def __init__(self, max_depth:int, spp:int) -> None:
        self.frame_count = 0
        self.max_depth = max_depth
        self.current_spp = spp

width = 1280
height = 720

# ti.aot.start_recording("rt.yml")
ti.init(arch=ti.gpu)
cam =  RTCamera(2, width, height, ti.Vector([0, 0, 1]), ti.Vector([0, 0, 0]), 360 / width)

frame_state = FrameState(5, 1)
pixels = vec4.field(shape=(width, height))

window = ti.ui.Window("RT1Weekend", (width, height))
canvas = window.get_canvas()

bvh_field, geom_field, material_field = scene.build_scene_bvh()
vis = vec4(0, 0, 1, 1)

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
def ray_trace(width:int, height:int, prev_count:int, frame_count_inv:float, max_depth:int, cam_param:vec13, spp:int, vis:vec4):
    for i in range(width * height):
        px = i % width
        py = i // width
        new_avg_sample = vec4(0 ,0 ,0 ,0)
        for j in range(spp):
            x = px + ti.random(float)
            y = py + ti.random(float)

            r = get_ray(cam_param, x, y, width, height)
            new_avg_sample += rtutil.ray_color(r, bvh_field, geom_field, material_field, max_depth, vis)
        new_avg_sample /=  spp
        pixels[px, py] = (pixels[px, py] * prev_count + new_avg_sample) * frame_count_inv

def clear(frame_state):
    frame_state.frame_count = 0
    pixels.fill(0)

old_vis = vec4(vis)
while window.running:
    window.GUI.begin("info", 0, 0, 0.2, 0.2)
    window.GUI.text(f"frame count: {frame_state.frame_count}")
    window.GUI.text(f"max depth: {frame_state.max_depth}")
    window.GUI.text(f"spp: {frame_state.current_spp}")
    vis[1] = window.GUI.slider_float("vis value start",vis[1], 0, 1)
    vis[2] = window.GUI.slider_float("vis value end", vis[2], vis[1] + 0.01, 1)
    vis[3] = vis[2] - vis[1]

    if (vis != old_vis).any() != 0:
    # if vis != old_vis:
        clear(frame_state)
        old_vis = copy.deepcopy(vis)
    window.GUI.end()

    mouse_pos = window.get_cursor_pos()
    mouse_pos_px = vec2(mouse_pos[0] * width, mouse_pos[1] * height)

    if cam.on_mouse_position(mouse_pos_px):
        clear(frame_state)

    if window.get_event(ti.ui.PRESS):
        if window.event.key in [ti.ui.UP, ti.ui.DOWN, ti.ui.LEFT, ti.ui.RIGHT, 'q', 'e', 'z', 'x', 'c']:
            clear(frame_state)

        if window.event.key == ti.ui.UP:
            frame_state.max_depth += 1
        elif window.event.key == ti.ui.DOWN:
            frame_state.max_depth -= 1
        elif window.event.key == ti.ui.LEFT:
            cam.focal_len -= 0.1
        elif window.event.key == ti.ui.RIGHT:
            cam.focal_len += 0.1
        elif window.event.key == 'q':
            frame_state.current_spp -= 1
        elif window.event.key == 'e':
            frame_state.current_spp += 1
        elif window.event.key == 'z':
            vis[0] = 0
        elif window.event.key == 'x':
            vis[0] = 1
        elif window.event.key == 'c':
            vis[0] = 2

        if window.event.key == ti.ui.LMB:
            cam.on_left_pressed(mouse_pos_px)

    if window.get_event(ti.ui.RELEASE):
        if window.event.key == ti.ui.LMB:
            cam.on_left_released(mouse_pos_px)

    if window.is_pressed('a'):
        cam.move(vec2(-0.1, 0))
        clear(frame_state)
    if window.is_pressed('d'):
        cam.move(vec2(0.1, 0))
        clear(frame_state)
    if window.is_pressed('w'):
        cam.move(vec2(0, 0.1))
        clear(frame_state)
    if window.is_pressed('s'):
        cam.move(vec2(0, -0.1))
        clear(frame_state)

    ray_trace(width, height, frame_state.frame_count, 1 / (frame_state.frame_count + 1), frame_state.max_depth, cam.dump(), frame_state.current_spp, vis)
    canvas.set_image(pixels)
    window.show()
    frame_state.frame_count += 1
