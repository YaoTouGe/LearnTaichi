from turtle import position
import taichi as ti
import sys
import numpy as np

sys.path.extend(["RT1Weekend"])
from camera import Camera
from datatypes import *

ti.init(ti.gpu)
particle_count = 100

positions = ti.Vector.field(n=3, dtype=ti.f32, shape=particle_count)
velocities = ti.Vector.field(n=3, dtype=ti.f32, shape=particle_count)
delta_t = 0.05
G = vec3(0, -9.8, 0)
mass_inv = 1
radius = 5

width = 640
height = 480

@ti.kernel
def FillInit3D():
    for i in positions:
        for k in ti.static(range(3)):
            positions[i][k] = ti.random() * 4 - 2
            velocities[i][k] = ti.random() * 2 - 1

@ti.kernel
def FillInit2D():
    for i in positions:
            positions[i][0] = ti.random() * 4 - 2
            positions[i][1] = ti.random() * 4 - 2
            positions[i][2] = 0

            velocities[i][0] = ti.random() * 2 - 1
            velocities[i][1] = ti.random() * 2 - 1
            velocities[i][2] = 0

@ti.kernel
def Simulation():
    for i in range(particle_count):
        velocities[i] = velocities[i] + G * delta_t

        # particle collision
        for j in range(particle_count):
            if i != j:
                diff = (positions[i] - positions[j])
                direction = diff.normalized()
                if diff.dot(diff) <= radius * 2:
                    align_v_i = velocities[i].dot(direction)
                    ortho_v_i = velocities[i] - align_v_i

                    align_v_j = velocities[j].dot(direction)
                    ortho_v_j = velocities[j] - align_v_j

                    velocities[i] = -align_v_i + ortho_v_i
                    velocities[j] = -align_v_j + ortho_v_j
                    # need position correction?
        positions[i] += delta_t * velocities[i]

use_ggui = False

if not use_ggui:
    # pos = np.random.random((50, 2))
    # # Create an array of 50 integer elements whose values are randomly 0, 1, 2
    # # 0 corresponds to 0x068587
    # # 1 corresponds to 0xED553B
    # # 2 corresponds to 0xEEEEF0
    indices = np.random.randint(0, 2, size=(particle_count,))
    # gui = ti.GUI("circles", res=(400, 400))
    # while gui.running:
    #     gui.circles(pos, radius=5, palette=[0x068587, 0xED553B, 0xEEEEF0], palette_indices=indices)
    #     gui.show()
    FillInit2D()
    gui = ti.GUI("2d billard", res=(width, height))
    velocities.fill(0)
    while gui.running:
        Simulation()
        nparr = positions.to_numpy()
        gui.circles(nparr[:,[0,1]], radius, palette=[0x068587, 0xED553B, 0xEEEEF0], palette_indices=indices)
        gui.show()
else:
    FillInit3D()
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

        scene.particles(positions, radius)
        canvas.scene(scene)
        window.show()