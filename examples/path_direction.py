from pd import *


w = 200
canvas(w, w)  # set canvas size
motion_path = regular_polygon((w/2, w/2), 5, 80)
tri = regular_polygon((w/2, w/2), 3, 4).scale(1, 2).rotate(4.71238898038469)
frames = 25
# calculate spaces beetween triangles
step = (1/frames) / frames

for tstep in range(frames):
    clear()
    motion_path.draw(None, "white")
    for t in linspace(0 + step * tstep, 1 - 1/frames + step * tstep, frames):
        # get point and tangent angle on motion path
        p, a = motion_path.point_and_angle(t)
        # set position and tangent angles of triangles
        tri.set_pos(p).rotated(a).draw("orange", None)
    # clone and append current canvas to global frame list (frames)
    append_frame()
save_gif("path_direction.gif")
