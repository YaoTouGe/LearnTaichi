import taichi as ti
from datatypes import *

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

    def on_cursor(self, dx, dy):
        pass

    # vec2 dir, move on forward right plane
    def move(self, move:vec2):
        self.cam_pos = self.cam_pos + move.x * self.right + move.y * self.forward

    def dump(self):
        return vec13(self.focal_len, self.cam_pos, self.forward, self.right, self.up)