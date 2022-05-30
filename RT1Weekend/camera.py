import math
import copy
import taichi as ti
from datatypes import *
from scipy.spatial.transform import Rotation as R
import numpy
import colorful as colorful
from enum import IntEnum

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

class Camera:
    '''
        Base camera, handle camera orientation, in OpenGL coordinates
    '''
    def __init__(self, cam_pos, look_at, rotate_scale):
        
        self.cam_pos = cam_pos
        self.look_at = look_at

        self.forward = (look_at - cam_pos).normalized()
        self._update_axises()

        self.start_axises = None
        self.rotate_scale = rotate_scale
        
        self.min_y_rotate = None
        self.max_y_rotate = None

        self.gesture = MouseGesture(0.5)

    def _update_axises(self):
        if ti.abs(self.forward.y) < 0.9:
            self.up = vec3(0, 1, 0)
            self.right = self.forward.cross(self.up).normalized()
            self.up = self.right.cross(self.forward)
        else:
            self.right = vec3(1, 0, 0)
            self.up = self.right.cross(self.forward).normalized()
            self.right = self.forward.cross(self.up).normalized()

        self.look_at = self.cam_pos + self.forward

    # vec2 dir, move on forward right plane
    def move(self, move:vec2):
        self.cam_pos = self.cam_pos + move.x * self.right + move.y * self.forward
        self.look_at = self.cam_pos + self.forward

        # rotate dir radian around axis 
    def _rotate(self, target, a, axis:vec3):
        sin_half = ti.sin(a/2)
        quaterion = [axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half, ti.cos(a / 2)]
        r = R.from_quat(quaterion)
        return ti.Vector(r.apply(target)).normalized()

    def _on_drag_begin(self, mouse_pos):
        self.drag_start_mouse = mouse_pos
        self.start_axises = [copy.deepcopy(self.right), copy.deepcopy(self.up), copy.deepcopy(self.forward)]
        self.min_y_rotate = -ti.acos(vec3(0, -1, 0).dot(self.forward))
        self.max_y_rotate = ti.acos(vec3(0, 1, 0).dot(self.forward))

    def _on_drag(self, mouse_pos):
        move = mouse_pos - self.drag_start_mouse
        if (ti.abs(move) < vec2(0.001, 0.001)).all():
            return
        # print(move)
        rotate_radian = vec2(math.radians(-move.x * self.rotate_scale), math.radians(move.y * self.rotate_scale))
        rotate_radian.y = numpy.clip(rotate_radian.y, self.min_y_rotate, self.max_y_rotate)

        self.forward = self._rotate(self.start_axises[2], rotate_radian.x, self.start_axises[1])
        self._update_axises()
        self.forward = self._rotate(self.forward, rotate_radian.y, self.right)
        self._update_axises()

    def _on_drag_end(self, mouse_pos):
        pass

    def on_mouse_position(self, mouse_pos):
        self.gesture.on_mouse_position(mouse_pos)
        state = self.gesture.consume_state()
        # print(state.name)
        if state == GestureState.DRAG_START:
            self._on_drag_begin(mouse_pos)
        elif state == GestureState.DRAGING:
            self._on_drag(mouse_pos)
            return True
        elif state == GestureState.DRAG_END:
            self._on_drag_end(mouse_pos)
        return False

    def on_left_pressed(self, mouse_pos):
        self.gesture.on_left_button_pressed(mouse_pos)

    def on_left_released(self, mouse_pos):
        self.gesture.on_left_button_released(mouse_pos)
    
class RTCamera(Camera):
    '''
        Camera used for ray tracing.
    '''
    def __init__(self, focal_len, width, height, cam_pos, look_at, rotate_scale) -> None:
        super().__init__(cam_pos, look_at, rotate_scale)
        self.focal_len = focal_len

        self.width = width
        self.height = height
        self.aspect_ratio = float(width) / height

    def dump(self):
        return vec13(self.focal_len, self.cam_pos, self.forward, self.right, self.up)