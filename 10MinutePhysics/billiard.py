from matplotlib import widgets
import taichi as ti
import sys

sys.path.extend(["RT1Weekend"])
from camera import Camera
from datatypes import *

ti.init(ti.gpu)
positions = ti.Vector.field(n=3, dtype=ti.f32, shape=100)

@ti.kernel
def FillPositions():
    for i in positions:
        for k in ti.static(range(3)):
            positions[i][k] = ti.random() * 4 - 2

FillPositions()

width = 1280
height = 720

window = ti.ui.Window("Billiards", (width, height), vsync=True)
canvas = window.get_canvas()
scene = ti.ui.Scene()
cam = ti.ui.make_camera()

my_cam = Camera(ti.Vector([0, 0, 4]), ti.Vector([0, 0, -1 ]), 360 / width)
# cam.position(0, 0, 4)
# cam.lookat(0, 0, -1)
# cam.up(0, 1, 0)

while window.running:
    mouse_pos = window.get_cursor_pos()
    mouse_pos_px = vec2(mouse_pos[0] * width, mouse_pos[1] * height)

    my_cam.on_mouse_position(mouse_pos_px)

    if window.get_event(ti.ui.PRESS):
        if window.event.key == ti.ui.LMB:
            my_cam.on_left_pressed(mouse_pos_px)

    if window.get_event(ti.ui.RELEASE):
        if window.event.key == ti.ui.LMB:
            my_cam.on_left_released(mouse_pos_px)

    if window.is_pressed('a'):
        my_cam.move(vec2(-0.1, 0))
    if window.is_pressed('d'):
        my_cam.move(vec2(0.1, 0))
    if window.is_pressed('w'):
        my_cam.move(vec2(0, 0.1))
    if window.is_pressed('s'):
        my_cam.move(vec2(0, -0.1))

    cam.position(my_cam.cam_pos[0], my_cam.cam_pos[1], my_cam.cam_pos[2])
    cam.lookat(my_cam.look_at[0], my_cam.look_at[1], my_cam.look_at[2])
    cam.up(my_cam.up[0], my_cam.up[1], my_cam.up[2])
    # cam.track_user_inputs(window)
    scene.set_camera(cam)
    scene.point_light(pos=(0.5, 1, 2), color=(1,1,1))
    scene.ambient_light((0.5,0.7,0.8))

    scene.particles(positions, 0.1)
    canvas.scene(scene)
    window.show()