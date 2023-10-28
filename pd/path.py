from copy import deepcopy
from typing import Self
from pd import singleton, tween
from pd._d_parser import parse_path
from pd.tween import Easings
from pd.utils import (get_pos, linspace, calculate_length,
                      is_points_close, rotate, scale, translate, tuples2list,
                      list2tuples, centroid, bbox, shift,
                      point_on_circle, opposite_angle)
import math


class Path():

    def __init__(self, coordinates: list[float] | list[tuple] | str, close=False):
        """Creates new Path with a list of coordinates or SVG d string

        (A) Arc for SVG string is not supported.
        """
        self.coords = []
        if isinstance(coordinates, str):
            self.coords = parse_path(coordinates)
        if isinstance(coordinates, list):
            self.coords = coordinates
        if isinstance(coordinates[0], tuple):
            self.coords = tuples2list(coordinates)
        self.length = calculate_length(self.coords)
        self.anchor = self.centroid

    def set_anchor(self, pos: tuple):
        self.anchor = pos
        return self

    def is_closed(self) -> bool:
        """Checks if the Path is closed."""
        x1, y1 = self.coords[:2]
        x2, y2 = self.coords[-2:]
        return math.isclose(x1, x2) and math.isclose(y1, y2)

    def close(self):
        """Closes the path"""
        if self.is_closed() == False:
            self.coords.extend((self.coords[0], self.coords[1]))
            self.length = calculate_length(self.coords)
        return self

    def open(self):
        """Opens the path"""
        if self.is_closed():
            self.coords = self.coords[:-2]
            self.length = calculate_length(self.coords)
        return self

    def clone(self):
        """Returns copy of Path"""
        cp = deepcopy(self)
        return cp

    @property
    def segs(self):
        """Returns number of segments"""
        return (len(self.coords) / 2) - 1

    @property
    def start(self) -> tuple:
        """Returns start point"""
        return (self.coords[0], self.coords[1])

    @property
    def end(self) -> tuple:
        """Returns end point"""
        return (self.coords[-2], self.coords[-1])

    @property
    def points(self):
        """Returns number of points"""
        return (len(self.coords) / 2)

    def repeated(self, n):
        """Returns new repeated version of path n times

        Useful for creating motion path loops.
        """
        clone = deepcopy(self)
        clone.open()
        clone.coords = clone.coords * n
        clone.close()
        return clone

    def set_start(self, index):
        """Sets start point of path. (shift coordinates)"""
        self.open()
        self.coords = shift(self.coords, index * 2)
        self.close()
        self.length = calculate_length(self.coords)

    def as_tuples(self, round_coords=False) -> list[tuple]:
        """Returns path coords as tuple list"""
        return list2tuples(self.coords, round_coords=round_coords)

    @property
    def centroid(self) -> tuple:
        """Calculates and returns path centroid"""
        if self.is_closed() == False:
            return centroid(self.coords)
        else:
            self.open()
            point = centroid(self.coords)
            self.close()
            return point

    @property
    def bounds(self) -> list[tuple]:
        """Returns top-left and bottom-right bounding box coordinates as list. [p1, p2]"""
        return bbox(self.coords)

    def translate(self, x, y):
        """Translates Path"""
        translate(self.coords, x, y)
        self.anchor = (self.anchor[0] + x, self.anchor[1] + y)
        return self

    def rotate(self, angle, anchor_point: tuple = None):
        """Rotates the Path around the anchor point.

        The default anchor point is the centroid point of the shape. 
        The anchor point of newly created Path objects
        is calculated by averaging the coordinates."""

        if anchor_point == None:
            anchor_point = self.anchor
        rotate(self.coords, angle, anchor_point)
        return self

    def scale(self, x, y, anchor_point: tuple = None):
        """Scales the Path around the anchor point

        The default anchor point is the centroid point of the shape."""

        if anchor_point == None:
            anchor_point = self.anchor
        scale(self.coords, x, y, anchor_point)
        self.length = calculate_length(self.coords)
        return self

    def translated(self, x, y):
        """Returns new translated Path"""
        cp = deepcopy(self)
        cp.translate(x, y)
        return cp

    def rotated(self, angle, anchor_point: tuple = None):
        """Returns a new Path rotated around the anchor point."""
        cp = deepcopy(self)
        if anchor_point == None:
            anchor_point = cp.anchor
        return cp.rotate(angle, anchor_point)

    def scaled(self, x, y, anchor_point: tuple = None):
        """Returns new scaled Path"""
        cp = deepcopy(self)
        return cp.scale(x, y, anchor_point)

    def set_pos(self, pos: tuple) -> Self:
        """Moves the shape to the target position.

        The anchor point of the Path is taken as basis.
        """
        self.translate(pos[0] - self.anchor[0], pos[1] - self.anchor[1])
        return self

    def reverse(self):
        """reverse direction of path (order of coordinates).

        The starting point becomes the end and the end becomes the beginning.
        """
        self.coords.reverse()
        for i in range(0, len(self.coords), 2):
            self.coords[i], self.coords[i+1] = self.coords[i+1], self.coords[i]
        return self

    def add_point(self, t):
        """Adds a point at position t to the path.

        If there is already a point in the position, the point is not added.
        """

        if t == 1 or t == 0:
            return

        target_length = t * self.length
        total_length = 0.0
        for i in range(0, len(self.coords) - 2, 2):
            x1, y1 = self.coords[i], self.coords[i + 1]
            x2, y2 = self.coords[i + 2], self.coords[i + 3]
            segment_length = math.hypot(x2 - x1, y2 - y1)
            if total_length + segment_length >= target_length:
                frac_seg = (target_length - total_length) / segment_length
                point_x = x1 + (x2 - x1) * frac_seg
                point_y = y1 + (y2 - y1) * frac_seg
                if is_points_close((x2, y2), (point_x, point_y)) == False:
                    self.coords.insert(i + 2, point_y)
                    self.coords.insert(i + 2, point_x)
                    self.length = calculate_length(self.coords)
                return
            total_length += segment_length

    def point_and_angle(self, t) -> tuple[tuple, float]:
        """Returns point and tangent angle at time t (in range 0~1)"""

        if t == 1:
            angle = math.atan2(self.coords[-1] - self.coords[-3],
                               self.coords[-2] - self.coords[-4])
            return ([self.coords[-2], self.coords[-1]],  angle)
        if t == 0:
            angle = math.atan2(self.coords[3] - self.coords[1],
                               self.coords[2] - self.coords[0])
            return ([self.coords[0], self.coords[1]],  angle)

        target_length = t * self.length
        return get_pos(self.coords, target_length)

    def offset(self, t: float, lenght: float) -> tuple[tuple, tuple]:
        """Returns the outer and inner parallel points of the given length in time on the path."""
        pos, ang = self.point_and_angle(t)
        ang += math.pi * 0.5
        p1 = point_on_circle(pos, lenght, ang)
        p2 = point_on_circle(pos, lenght, opposite_angle(ang))
        return (p1, p2)

    def resample(self, n):
        """Resamples the points on the path n times"""
        cords = []
        for i in linspace(0, 1, n):
            cords.extend(self.point_and_angle(i)[0])
        self.coords = cords
        self.length = calculate_length(self.coords)
        return self

    def draw(self, fill="#181818", stroke="grey", thickness=1.5):
        """Draws the path on the canvas."""
        singleton.draw_path(self.coords, fill, stroke,
                            thickness, self.is_closed())
        return self

    def draw_debug(self, radius=3, fill=80, stroke="white", thickness=1.5):
        """Draws path features as colored dots. It is for debugging purposes.

        The starting point is blue. The second point is green and helps find the direction of the path.
        """
        singleton.draw_path(self.coords, fill, stroke, thickness)
        points = self.as_tuples()
        for i, p in enumerate(points):
            if i != 0 or 1:
                singleton.draw_ellipse(
                    p, radius, radius, "grey", None)
        singleton.draw_ellipse(points[0], radius, radius, "deepskyblue", None)
        singleton.draw_ellipse(points[1], radius, radius, "lightgreen", None)
        return self

    def print_info(self, round_coords=True, lines=False):
        "Prints path info and coordinates"
        anchor_ = "anchor: " + str(self.anchor)
        closed_, points_ = str(self.is_closed()), str(
            int(len(self.coords) / 2))
        if lines:
            print("closed:", closed_, "| ", "points:", points_, "| ", anchor_)
            for p in self.as_tuples(round_coords=round_coords):
                print(p)
        else:
            print("closed:", closed_, "| ", "points:", points_, "| ", anchor_)
            print("coords: ", self.as_tuples(round_coords=round_coords))
        return self


class CBezier():

    def __init__(self, sx, sy, c1x, c1y, c2x, c2y, ex, ey):
        """Cubic Bezier object"""
        self.points: list[tuple] = [(sx, sy), (c1x, c1y), (c2x, c2y), (ex, ey)]

    def point(self, t: float) -> tuple:
        """Returns the point at time t in range 0~1"""
        x = (1 - t) * (1 - t) * (1 - t) * self.points[0][0] + 3 * (1 - t) * (
            1 - t) * t * self.points[1][0] + 3 * (1 - t) * t * t * self.points[2][0] + t * t * t * self.points[3][0]
        y = (1 - t) * (1 - t) * (1 - t) * self.points[0][1] + 3 * (1 - t) * (
            1 - t) * t * self.points[1][1] + 3 * (1 - t) * t * t * self.points[2][1] + t * t * t * self.points[3][1]
        return (x, y)

    def flatten(self, samples=50) -> list[float]:
        """Returns the flattened coordinates."""
        coords = []
        for t in linspace(0, 1, samples):
            coords.extend(self.point(t))
        return coords
