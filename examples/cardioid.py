from pd import *

canvas(200, 200)
l = line((0, 0), (50, 0)).set_anchor((0, 0)).translate(90, 100)
l2 = line((50, 0), (75, 0)).set_anchor((50, 0)).translate(90, 100)
coords = []
frames = 200
for i in range(frames):
    clear()
    l.rotate(pi*2/frames).draw(stroke="lime")
    l2.set_pos(l.end).rotate(pi*2 / (frames/2)).draw(stroke="yellow")
    coords.extend(l2.end)
    if len(coords) > 4:
        Path(coords).draw(None, "orangered")
    draw_circle(l2.end, 3)
    append_frame()
save_gif("cardioid.gif")
