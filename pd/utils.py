import math
from colorsys import hsv_to_rgb


def opposite_angle(angle):
    return (angle + math.pi) % (2 * math.pi)


def rotate_point(point: tuple, angle, origin: tuple):
    """Rotates point about origin point"""
    x = math.cos(angle) * (point[0] - origin[0]) - \
        math.sin(angle) * (point[1] - origin[1]) + origin[0]
    y = math.sin(angle) * (point[0] - origin[0]) + \
        math.cos(angle) * (point[1] - origin[1]) + origin[1]
    return (x, y)


def translate(coords: list[float], x, y):
    """Translates xy coordinate sequence"""
    coords[::2] = [x_ + x for x_ in coords[::2]]
    coords[1::2] = [y_ + y for y_ in coords[1::2]]


def rotate(coords: list[float], angle, origin: tuple):
    """Rotates xy coordinate sequence"""
    for i in range(0, len(coords), 2):
        coords[i], coords[i +
                          1] = rotate_point((coords[i], coords[i+1]), angle, origin)


def scale(coords, x, y, origin: tuple):
    """Scales xy coordinate sequence"""
    coords[::2] = [x * (x_ - origin[0]) + origin[0] for x_ in coords[::2]]
    coords[1::2] = [y * (y_ - origin[1]) + origin[1] for y_ in coords[1::2]]


def point_on_circle(center: tuple, radius, angle):
    '''Finding the x, y coordinates on circle, based on given angle.'''
    x = center[0] + (radius * math.cos(angle))
    y = center[1] + (radius * math.sin(angle))
    return (x, y)


def hsv_to_rgb8(h, s, v):
    c = hsv_to_rgb(h, s, v)
    return (int(c[0] * 255.0), int(c[1] * 255.0), int(c[2] * 255.0))


def is_points_close(p1: tuple, p2: tuple) -> bool:
    """check points close"""
    return math.isclose(p1[0], p2[0]) and math.isclose(p1[1], p2[1])


def shift(coords: list, n) -> list:
    n = n % len(coords)
    return coords[n:] + coords[:n]


def quadratic_to_cubic(x0, y0, x1, y1, x2, y2):
    """Calculates control points for the cubic Bezier curve"""

    Q0, Q1, Q2 = (x0, y0), (x1, y1), (x2, y2)
    c0 = Q0
    c1 = (Q0[0] + (2/3) * (Q1[0] - Q0[0]),
          Q0[1] + (2/3) * (Q1[1] - Q0[1]))
    c2 = (Q2[0] + (2/3) * (Q1[0] - Q2[0]),
          Q2[1] + (2/3) * (Q1[1] - Q2[1]))
    c3 = Q2

    return [c0[0], c0[1], c1[0], c1[1], c2[0], c2[1], c3[0], c3[1]]


def bbox(coords: list[float]):
    """Returns top left and bottom right bounding box xy coordinates as list. [p1, p2]"""
    x_coords, y_coords = coords[::2], coords[1::2]
    return [(min(x_coords), min(y_coords)), (max(x_coords), max(y_coords))]


def centroid(coords):
    total = len(coords) / 2
    return (sum(coords[::2]) / total, sum(coords[1::2]) / total)


def lerp_value(a: float, b: float, t: float):
    """linear interpolate a-b at time t in range 0~1"""
    return a * (1 - t) + b * t


def distance(x1, y1, x2, y2):
    """Returns distance between two points"""
    return math.hypot(x2 - x1, y2 - y1)


def find_angle(p0, p1, p2):
    """Returns angle of two points"""
    b = math.pow(p1[0] - p0[0], 2) + math.pow(p1[1] - p0[1], 2)
    a = math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2)
    c = math.pow(p2[0] - p0[0], 2) + math.pow(p2[1] - p0[1], 2)
    return math.acos((a + b - c) / math.sqrt(4 * a * b))


def tangent_angle(x1, y1, x2, y2):
    """Returns tangent angle of two points"""
    return math.atan2(y2 - y1, x2 - x1)


def map_range(t: float, a: float, b: float, c: float, d: float):
    """maps a~b range to c~d range at time t"""
    return (t-a) / (b-a) * (d-c) + c


def calculate_length(coords: list[float]):
    """calculates lenght of xy coords"""

    total_length = 0.0
    for i in range(0, len(coords) - 2, 2):
        x1, y1 = coords[i], coords[i + 1]
        x2, y2 = coords[i + 2], coords[i + 3]
        segment_length = math.hypot(x2 - x1, y2 - y1)
        total_length += segment_length
    return total_length


def list2tuples(coords, round_coords=False) -> list[tuple]:
    """Returns path coords as tuple list"""
    if round_coords:
        return [(round(x), round(y)) for x, y in zip(coords[::2], coords[1::2])]
    else:
        return [(x, y) for x, y in zip(coords[::2], coords[1::2])]


def tuples2list(tuples: list):
    return list(sum(tuples, ()))


def remove_doubles(coords: list[float]) -> list[float]:
    points = list2tuples(coords)
    new_points = []
    for i in range(len(points) - 1):
        if is_points_close(points[i], points[i+1]) == False:
            new_points.append(points[i])

    new_points.append(points[-1])
    return tuples2list(new_points)


def get_pos(coords: list[float], length: float) -> tuple[tuple, float]:
    """Returns point and tangent angle at time t (in range 0~1)"""
    total_length = 0.0
    for i in range(0, len(coords) - 2, 2):
        x1, y1 = coords[i], coords[i + 1]
        x2, y2 = coords[i + 2], coords[i + 3]
        segment_length = math.hypot(x2 - x1, y2 - y1)
        if total_length + segment_length >= length:
            frac_seg = (length - total_length) / segment_length
            point_x = x1 + (x2 - x1) * frac_seg
            point_y = y1 + (y2 - y1) * frac_seg
            point_angle = ([point_x, point_y], math.atan2(y2 - y1, x2 - x1))
            return point_angle
        total_length += segment_length


def linspace(start, stop, num):
    """
    Returns evenly spaced numbers over a specified closed interval.

    Args:
        start (float): The starting value of the interval.
        stop (float): The ending value of the interval.
        num (int): The number of evenly spaced values to generate.

    Returns:
        list: A list of evenly spaced numbers over the specified interval.
    """
    if num <= 0:
        return []
    if num == 1:
        return [start]
    step = (stop - start) / float(num-1)
    res = [0] * num
    res[0] = start
    for i in range(1, num):
        res[i] = start + i * step
    res[num-1] = stop
    return res
