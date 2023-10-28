import aggdraw
from PIL import Image
from copy import deepcopy

draw, img, frames = None, None, []


def canvas(w, h):
    """Creates a Canvas (PIL Image surface) of the given size and creates a global aggdraw Draw object to draw on."""
    global draw, img
    img = Image.new("RGBA", (w, h), "black")
    draw = aggdraw.Draw(img)


def put_pixel(xy: tuple, color: tuple = (255, 255, 255)):
    global img
    img.putpixel(xy, color)


def set_antialiasing(flag=True):
    """True to enable anti-aliasing, false to disable it."""
    global draw
    draw.setantialias(flag)


def clear(color="black"):
    """Fills the canvas with the given color. Default is black"""
    global draw
    draw.clear(color)


def draw_path(coords: list[float], fill=80, stroke="white", thickness=1.5, closed=False):
    """Draws coordinates as path on global surface"""

    pen = aggdraw.Pen(stroke, thickness) if stroke is not None else None
    brush = aggdraw.Brush(fill) if fill is not None else None
    if closed:
        draw.polygon(coords,  pen, brush)
    else:
        draw.path(aggdraw.Path(coords),  pen, brush)
    draw.flush()


def draw_ellipse(origin: tuple, radius_x, radius_y, fill=80, stroke="white", thickness=1.5):
    """Draws ellipse immediately"""

    pen = aggdraw.Pen(stroke, thickness) if stroke is not None else None
    brush = aggdraw.Brush(fill) if fill is not None else None

    x, y = origin[0] - radius_x, origin[1] - radius_y
    w, h = origin[0] + radius_x, origin[1] + radius_y

    draw.ellipse((x, y, w, h), pen, brush)
    draw.flush()


def draw_circle(origin: tuple, radius, fill=80, stroke="white", thickness=1.5):
    draw_ellipse(origin, radius, radius, fill, stroke, thickness)


def draw_line(start: tuple, end: tuple, stroke="white", thickness=1):
    """Draws line immediately"""
    global draw
    pen = aggdraw.Pen(stroke, thickness)
    draw.line((start[0], start[1], end[0], end[1]), pen)
    draw.flush()


def draw_rectangle(xy: tuple, w, h, fill=80, stroke="white", thickness=1.5):
    """The first parameter set the location of the rectangle's upper-left corner.
    The second and third set the shape's the width and height, respectively"""

    pen = aggdraw.Pen(stroke, thickness) if stroke is not None else None
    brush = aggdraw.Brush(fill) if fill is not None else None
    coords = (xy[0], xy[1], xy[0] + w, xy[1] + h)
    draw.rectangle(coords, pen, brush)
    draw.flush()


def draw_bbox(upper_left: tuple, bottom_right: tuple, fill=None, stroke="cyan", thickness=1.5):
    """Draws bounding box rectangle.

    The first parameter is bounding box's upper-left corner.
    The second is bottom-right corner"""

    pen = aggdraw.Pen(stroke, thickness) if stroke is not None else None
    brush = aggdraw.Brush(fill) if fill is not None else None
    draw.rectangle((*upper_left, *bottom_right), pen, brush)
    draw.flush()


def save(filename="canvas.png"):
    """Saves current canvas to disk"""
    global img
    img.save(filename)


def append_frame():
    """Appends the current state of the canvas to the list as a keyframe image.

    Animation can then be saved with save_gif() .
    """
    global img, frames
    cp = deepcopy(img)
    frames.append(cp)


def save_gif(filename="anim.gif", ms=20, colours=256):
    """Saves animation as GIF


    - 100 MS = 10 FPS  
    - 50 MS = 20 FPS 
    - 33.33333 MS = 30 FPS 
    - 20 MS = 50 FPS 
    """
    global frames
    for i in range(len(frames)):
        frames[i] = frames[i].convert(mode="P",
                                      dither=False, palette=Image.ADAPTIVE,
                                      colors=colours)
    frames[0].save(filename, save_all=True,
                   append_images=frames[1:], optimize=False,
                   duration=ms, loop=0)
