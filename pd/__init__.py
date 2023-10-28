from pd.singleton import (canvas, save, save_gif,
                          append_frame, set_antialiasing, put_pixel,
                          clear, draw_ellipse, draw_circle,
                          draw_line, draw_rectangle, draw_path, draw_bbox)
from pd.path import Path
from pd.utils import linspace, hsv_to_rgb8, point_on_circle, map_range
from pd.path_factory import (
    line, regular_polygon, ellipse,
    cubic_bezier, quadratic_bezier,
    rectangle, star, bbox)
# from .tween import Easings
from math import radians, pi
