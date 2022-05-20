import math
import copy
import taichi as ti
from datatypes import *
from scipy.spatial.transform import Rotation as R
import numpy

@ti.data_oriented
class RTCamera:
    '''
        In OpenGL coordinates
    '''
    def __init__(self, focal_len, width, height, cam_pos, look_at, rotate_scale) -> None:
        self.focal_len = focal_len

        self.width = width
        self.height = height
        self.aspect_ratio = float(width) / height

        self.cam_pos = cam_pos
        self.look_at = look_at

        self.forward = (look_at - cam_pos).normalized()
        self.update_axises()

        self.start_axises = None
        self.rotate_scale = rotate_scale
        
    def update_axises(self):
        if ti.abs(self.forward.y) < 0.9:
            self.up = vec3(0, 1, 0)
            self.right = self.forward.cross(self.up).normalized()
            self.up = self.right.cross(self.forward)
        else:
            self.right = vec3(1, 0, 0)
            self.up = self.right.cross(self.forward).normalized()
            self.right = self.forward.cross(self.up).normalized()

    def on_cursor(self, dx, dy):
        pass

    # vec2 dir, move on forward right plane
    def move(self, move:vec2):
        self.cam_pos = self.cam_pos + move.x * self.right + move.y * self.forward

    def dump(self):
        return vec13(self.focal_len, self.cam_pos, self.forward, self.right, self.up)

    # rotate dir radian around axis 
    def _rotate(self, target, a, axis:vec3):
        sin_half = ti.sin(a/2)
        quaterion = [axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half, ti.cos(a / 2)]
        r = R.from_quat(quaterion)
        return ti.Vector(r.apply(target)).normalized()

    def on_drag_begin(self, mouse_pos):
        self.drag_start_mouse = mouse_pos
        self.start_axises = [copy.deepcopy(self.right), copy.deepcopy(self.up), copy.deepcopy(self.forward)]

    def on_drag(self, mouse_pos):
        move = mouse_pos - self.drag_start_mouse
        if (ti.abs(move) < vec2(0.001, 0.001)).all():
            return
        # print(move)

        move.y = numpy.clip(-move.y, -89, 89)
        rotate_angle = move * self.rotate_scale

        # print(rotate_angle.y)
        self.forward = self._rotate(self.start_axises[2], math.radians(-rotate_angle.x), self.start_axises[1])
        self.update_axises()
        self.forward = self._rotate(self.forward, math.radians(-rotate_angle.y), self.right)
        self.update_axises()

    def on_drag_end(self, mouse_pos):
        pass