from enum import IntEnum
import taichi as ti
from datatypes import *
import rtutil
import scene
import colorful
from camera import RTCamera

class FrameState:
    def __init__(self, max_depth:int, spp:int) -> None:
        self.frame_count = 0
        self.max_depth = max_depth
        self.spp = spp
        self.current_spp = 1

width = 1280
height = 720

# ti.aot.start_recording("rt.yml")
ti.init(arch=ti.vulkan)
cam =  RTCamera(2, width, height, ti.Vector([0, 0, 1]), ti.Vector([0, 0, 0]), 360 / width)

frame_state = FrameState(5, 3)
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
def ray_trace(width:int, height:int, prev_count:int, frame_count_inv:float, max_depth:int, cam_param:vec13, spp:int):
    for i in range(width * height):
        px = i % width
        py = i // width
        new_avg_sample = vec4(0 ,0 ,0 ,0)
        for j in range(spp):
            x = px + ti.random(float)
            y = py + ti.random(float)

            r = get_ray(cam_param, x, y, width, height)
            new_avg_sample += rtutil.ray_color(r, bvh_field, geom_field, material_field, max_depth)
        new_avg_sample /=  spp
        pixels[px, py] = (pixels[px, py] * prev_count + new_avg_sample) * frame_count_inv

def clear(frame_state):
    frame_state.frame_count = 0
    frame_state.current_spp = 1
    pixels.fill(0)

class GestureState(IntEnum):
        INIT = 0
        RECOGNIZING = 1
        DRAGING = 1 << 1

        DRAG_START = 1 << 2
        '''
        final states, will be reset after consumed
        '''
        CLICK = 1 << 3
        DOUBLE_CLICK = 1 << 4
        DRAG_END = 1 << 5

        FINAL_STATES = CLICK | DOUBLE_CLICK | DRAG_END

class MouseGesture:
    def __init__(self, drag_thresh) -> None:
        self.start_mouse_pos = None
        self.last_mouse_pos = None
        self.state = GestureState.INIT
        self.drag_thresh = drag_thresh

    def on_left_button_pressed(self, mouse_pos):
        if self.state != GestureState.INIT:
            colorful.print_error(f"error gesture state!{self.state.name}")
        self.state = GestureState.RECOGNIZING
        self.start_mouse_pos = mouse_pos

    def on_mouse_position(self, mouse_pos):
        if self.state == GestureState.RECOGNIZING:
            if ti.abs(mouse_pos - self.start_mouse_pos).max() > self.drag_thresh:
                self.state = GestureState.DRAG_START

        delta = vec2(0)
        if self.last_mouse_pos != None:
            delta = mouse_pos - self.last_mouse_pos
        self.last_mouse_pos = mouse_pos

        return delta

    def on_left_button_released(self, mouse_pos):
        if self.state == GestureState.RECOGNIZING:
            self.state = GestureState.CLICK
        elif self.state == GestureState.DRAGING:
            self.state = GestureState.DRAG_END

    def consume_state(self):
        ret = self.state
        if self.state & GestureState.FINAL_STATES:
            self.state = GestureState.INIT
        elif self.state == GestureState.DRAG_START:
            self.state = GestureState.DRAGING
        return ret

gesture = MouseGesture(0.5)

while window.running:
    window.GUI.begin("info", 0, 0, 0.2, 0.2)
    window.GUI.text(f"frame count: {frame_state.frame_count}")
    window.GUI.text(f"max depth: {frame_state.max_depth}")
    window.GUI.text(f"spp: {frame_state.spp}")
    # is_clicked = window.GUI.button(name)
    # new_value = window.GUI.slider_float(name, old_value, min_value, max_value)
    # new_color = window.GUI.color_edit_3(name, old_color)
    window.GUI.end()

    mouse_pos = window.get_cursor_pos()
    mouse_pos_px = vec2(mouse_pos[0] * width, mouse_pos[1] * height)
    delta = gesture.on_mouse_position(mouse_pos_px)

    if window.get_event(ti.ui.PRESS):
        if window.event.key in [ti.ui.UP, ti.ui.DOWN, ti.ui.LEFT, ti.ui.RIGHT, 'q', 'e']:
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
            frame_state.spp -= 1
        elif window.event.key == 'e':
            frame_state.spp += 1

        if window.event.key == ti.ui.LMB:
            gesture.on_left_button_pressed(mouse_pos_px)

    if window.get_event(ti.ui.RELEASE):
        if window.event.key == ti.ui.LMB:
            gesture.on_left_button_released(mouse_pos_px)

    state = gesture.consume_state()
    # print(state.name)
    if state == GestureState.DRAG_START:
        cam.on_drag_begin(mouse_pos_px)
    elif state == GestureState.DRAGING:
        cam.on_drag(mouse_pos_px)
        clear(frame_state)
    elif state == GestureState.DRAG_END:
        cam.on_drag_end(mouse_pos_px)

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

    ray_trace(width, height, frame_state.frame_count, 1 / (frame_state.frame_count + 1), frame_state.max_depth, cam.dump(), frame_state.current_spp)
    canvas.set_image(pixels)
    window.show()
    frame_state.frame_count += 1
    frame_state.current_spp = frame_state.spp
