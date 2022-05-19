import taichi as ti
from datatypes import *
from scipy.spatial.transform import Rotation as R

@ti.data_oriented
class RTCamera:
    '''
        OpenGL coordinates
    '''
    def __init__(self, focal_len, width, height, cam_pos, look_at) -> None:
        self.focal_len = focal_len

        self.width = width
        self.height = height
        self.aspect_ratio = float(width) / height

        self.cam_pos = cam_pos
        self.look_at = look_at

        self.forward = (look_at - cam_pos).normalized()
        if ti.abs(self.forward.y) < 0.9:
            self.up = vec3(0, 1, 0)
            self.right = self.forward.cross(self.up).normalized()
            self.up = self.right.cross(self.forward)
        else:
            self.right = vec3(1, 0, 0)
            self.up = self.right.cross(self.forward).normalized()
            self.right = self.forward.cross(self.up).normalized()
        self.drag_start_mouse = None

    def on_cursor(self, dx, dy):
        pass

    # vec2 dir, move on forward right plane
    def move(self, move:vec2):
        self.cam_pos = self.cam_pos + move.x * self.right + move.y * self.forward

    def dump(self):
        return vec13(self.focal_len, self.cam_pos, self.forward, self.right, self.up)

    # rotate camera forward dir a radian around axis 
    def _rotate_cam(self, a, axis:vec3):
        sin_half = ti.sin(a/2)
        quaterion = [axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half, ti.cos(a / 2)]
        r = R.from_quat(quaterion)

        self.forward = ti.Vector(r.apply(self.forward)).normalized()
        self.right = self.forward.cross(self.up).normalized()
        self.up = self.right.cross(self.forward)

    def on_drag_begin(self, mouse_pos):
        self.drag_start_mouse = mouse_pos

    def on_drag(self, move):
        if (ti.abs(move) < vec2(0.001, 0.001)).all():
            return
        target = self.forward + move.x * self.right + self.up * move.y
        axis = self.forward.cross(target).normalized()
        cos = target.normalized().dot(self.forward)
        self._rotate_cam(ti.acos(cos), axis)

    def on_drag_end(self, mouse_pos):
        pass