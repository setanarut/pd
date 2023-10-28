import math
from pd.path import Path, CBezier
from pd.utils import quadratic_to_cubic, rotate_point, scale


def line(start: tuple, end: tuple):
    """Returns line"""
    p = Path((start, end))
    return p


def rectangle(xy: tuple, width, height):
    """Returns rectangle

    The first parameter set the location of the rectangle's upper-left corner.
    The second and third set the shape's the width and height, respectively"""
    p = Path([0, 0, width, 0, width, height, 0, height, 0, 0]).translate(*xy)
    return p.set_anchor(p.centroid)


def bbox(upper_left: tuple, bottom_right: tuple):
    """Returns bounding box rectangle 

    The first parameter is xy coordinate of the box's upper-left corner.
    The second parameter is bottom-right corner"""
    x1, y1 = upper_left
    x2, y2 = bottom_right
    return Path([x1, y1, x2, y1, x2, y2, x1, y2, x1, y1])


def ellipse(origin: tuple, x_radius, y_radius, samples=200):
    """Returns ellipse"""
    coords = []
    angle_step = 2 * math.pi / samples
    for i in range(samples):
        angle = i * angle_step
        x = x_radius * math.cos(angle)
        y = y_radius * math.sin(angle)
        coords.extend([x + origin[0], y + origin[1]])
    p = Path(coords)
    p.anchor = origin
    p.close()
    return p


def circle(origin: tuple, radius, samples=200):
    """Returns circle"""
    return ellipse(origin, radius, radius, samples)


def cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, samples=200):
    """Returns cubic bezier"""
    cb = CBezier(x0, y0, x1, y1, x2, y2, x3, y3)
    p = Path(cb.flatten(samples))
    p.anchor = p.centroid
    return p


def quadratic_bezier(x0, y0, x1, y1, x2, y2, samples=200):
    """Returns quadratic bezier"""
    cb = CBezier(*quadratic_to_cubic(x0, y0, x1, y1, x2, y2))
    p = Path(cb.flatten(samples))
    p.anchor = p.centroid
    return p


def regular_polygon(origin: tuple, n: int = 5, circum_radius: float = 64, from_side=False):
    """Returns regular polygon

    If `from_side` is True, `circum_radius` is considered the side length. The polygon is drawn according to the side length."""

    def _crad_from_side(side_length, n):
        return 1 / 2 * side_length * 1 / math.sin(math.pi / n)
    crad = 0
    two_pi = math.pi * 2
    if from_side:
        crad = _crad_from_side(circum_radius, n)
    else:
        crad = circum_radius
    align_angle = (two_pi / 4) - two_pi / n / 2
    coords = []
    for i in range(n+1):

        ang = (i / n) * two_pi + align_angle
        x = math.cos(ang) * crad + origin[0]
        y = math.sin(ang) * crad + origin[1]

        coords.extend((x, y))
    p = Path(coords)
    p.anchor = origin
    return p


def star(origin: tuple, circum_radius: float):
    """Returns star shape"""
    r = regular_polygon(origin, 5, circum_radius)
    r2 = regular_polygon(origin,
                         5,
                         circum_radius*0.38196601125).rotate(0.6283185307179586)
    c = list(sum(list(zip(r.as_tuples(), r2.as_tuples())), ()))
    c.pop()
    return Path(c)
