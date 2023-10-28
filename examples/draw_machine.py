from pd import *


from random import random, uniform


def random_numbers(n, min, max):
    l = []
    for i in range(n):
        l.append(uniform(min, max))
    return l


def random_angles(n, min, max):
    l = []
    for i in range(n):
        num = uniform(min, max)
        if random() > 0.5:
            num = -abs(num)
        l.append(num)
    return l


frames = 400
scale = 1
rads = random_numbers(15, 10, 25)
c = pi*2 / frames
speeds = random_angles(15, c, c*16)
# print(rads, speeds)
size = (400, 400)
canvas(*size)

pos = 0
arms = []
for rad in (rads):
    rad = rad * scale
    arm = line((0, 0), (rad, 0)).set_anchor(
        (0, 0)).translate(pos+size[0]/2-40, size[1]/2)
    arms.append(arm)
    pos += rad

coords = []
for i in range(frames):
    clear()
    for i, speed in enumerate(speeds):
        arms[i].rotate(speed)
        if i > 0:
            arms[i].set_pos(arms[i-1].end)
        coords.extend(arms[-1].end)
        arms[i].draw(stroke="deepskyblue", thickness=2)
        draw_circle(arms[-1].end, 3)
    Path(coords).draw(None, "grey", thickness=2)
    append_frame()

save_gif("draw_machine.gif")
# Path(coords).draw(None, "orangered")
# save()
