import taichi as ti
import sys
import numpy as np

sys.path.extend(["RT1Weekend"])
from camera import Camera
from datatypes import *

ti.init(ti.gpu)
particle_count = 5000

positions = ti.Vector.field(n=3, dtype=ti.f32, shape=particle_count)
velocities = ti.Vector.field(n=3, dtype=ti.f32, shape=particle_count)
delta_t = 1 / 60
G = vec3(0, -9.8, 0)
# G = vec3(0, 0, 0)
mass_inv = 1
radius = 0.05
substep_count = 1.0

world_size = 3
box_min = vec3(-world_size, -world_size, -world_size)
box_max = vec3(world_size, world_size, world_size)

width = 1280
height = 720

@ti.kernel
def FillInit3D():
    for i in positions:
        for k in ti.static(range(3)):
            positions[i][k] = ti.random() * 4 - 2
            velocities[i][k] = ti.random() * 0.5 - 0.25
        velocities[i][1] = 0
@ti.kernel
def Simulation():
    for i in range(particle_count):
        velocities[i] = velocities[i] + G * delta_t

    # particle collision
    for i in range(particle_count):
        for k in range(substep_count):
            for j in range(i + 1, particle_count):
                diff = (positions[i] - positions[j])
                dist = ti.sqrt(diff.dot(diff))
                direction = diff.normalized()

                if dist <= 2 * radius and dist > 0:
                    align_v_i = velocities[i].dot(-direction)
                    ortho_v_i = velocities[i] + align_v_i * direction

                    align_v_j = velocities[j].dot(direction)
                    ortho_v_j = velocities[j] - align_v_j * direction
                    
                    # exchange speed when mass are the same and full elastic
                    velocities[i] = ortho_v_i + direction * align_v_j
                    velocities[j] = ortho_v_j - direction * align_v_i

                    # correct position
                    correction = radius - dist / 2
                    positions[i] += direction * correction
                    positions[j] -= direction * correction
                    # need position correction?

            # handle boundry collision
            pos = positions[i]
            if pos.x > box_max.x - radius or pos.x < box_min.x + radius:
                velocities[i].x *= -1
            if pos.y > box_max.y - radius or pos.y < box_min.y + radius:
                velocities[i].y *= -1
            if pos.z > box_max.z - radius or pos.z < box_min.z + radius:
                velocities[i].z *= -1
            
            positions[i] = ti.min(box_max - radius, positions[i])
            positions[i] = ti.max(box_min + radius, positions[i])

            positions[i] += delta_t * velocities[i] / substep_count


FillInit3D()
window = ti.ui.Window("Billiards", (width, height), vsync=True)
canvas = window.get_canvas()
scene = ti.ui.Scene()
cam = ti.ui.make_camera()

my_cam = Camera(ti.Vector([0, 0, 10]), ti.Vector([0, 0, -1 ]), 360 / width)
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

    Simulation()
    # cam.track_user_inputs(window)
    scene.set_camera(cam)
    scene.point_light(pos=(0.5, 1, 2), color=(1,1,1))
    scene.ambient_light((0.5,0.7,0.8))

    scene.particles(positions, radius)
    canvas.scene(scene)
    window.show()