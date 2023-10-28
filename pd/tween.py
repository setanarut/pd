from enum import Enum
import math


class Easings(Enum):
    """ https://easings.net/ """
    EASE_IN_BACK = "ease_in_back"
    EASE_IN_BOUNCE = "ease_in_bounce"
    EASE_IN_CIRC = "ease_in_circ"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_IN_ELASTIC = "ease_in_elastic"
    EASE_IN_EXPO = "ease_in_expo"
    EASE_IN_OUT_BACK = "ease_in_out_back"
    EASE_IN_OUT_BOUNCE = "ease_in_out_bounce"
    EASE_IN_OUT_CIRC = "ease_in_out_circ"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_OUT_ELASTIC = "ease_in_out_elastic"
    EASE_IN_OUT_EXPO = "ease_in_out_expo"
    EASE_IN_OUT_POLY = "ease_in_out_poly"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    EASE_IN_OUT_QUINT = "ease_in_out_quint"
    EASE_IN_OUT_SINE = "ease_in_out_sine"
    EASE_IN_POLY = "ease_in_poly"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_IN_QUART = "ease_in_quart"
    EASE_IN_QUINT = "ease_in_quint"
    EASE_IN_SINE = "ease_in_sine"
    EASE_OUT_BACK = "ease_out_back"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_OUT_CIRC = "ease_out_circ"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_OUT_ELASTIC = "ease_out_elastic"
    EASE_OUT_EXPO = "ease_out_expo"
    EASE_OUT_POLY = "ease_out_poly"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_OUT_QUINT = "ease_out_quint"
    EASE_OUT_SINE = "ease_out_sine"
    LINEAR = "linear"


def _check_range(n):
    if not 0.0 <= n <= 1.0:
        raise ValueError("Argument must be between 0.0 and 1.0.")


def get_point_on_line(x1, y1, x2, y2, t):
    x = ((x2 - x1) * t) + x1
    y = ((y2 - y1) * t) + y1
    return (x, y)


def linear(t):
    _check_range(t)
    return t


def ease_in_quad(t):
    _check_range(t)
    return t**2


def ease_out_quad(t):
    _check_range(t)
    return -t * (t - 2)


def ease_in_out_quad(t):
    _check_range(t)
    if t < 0.5:
        return 2 * t**2
    else:
        t = t * 2 - 1
        return -0.5 * (t * (t - 2) - 1)


def ease_in_cubic(t):
    _check_range(t)
    return t**3


def ease_out_cubic(n):
    _check_range(n)
    n -= 1
    return n**3 + 1


def ease_in_out_cubic(t: float):
    """A cubic tween function that accelerates, reaches the midpoint, and then decelerates.
    t (float): The time progress, starting at 0.0 and ending at 1.0.
    """
    _check_range(t)
    t *= 2
    if t < 1:
        return 0.5 * t**3
    else:
        t -= 2
        return 0.5 * (t**3 + 2)


def ease_in_quart(n):
    _check_range(n)
    return n**4


def ease_out_quart(n):
    _check_range(n)
    n -= 1
    return -(n**4 - 1)


def ease_in_out_quart(n):
    _check_range(n)
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


def ease_in_quint(n):
    _check_range(n)
    return n**5


def ease_out_quint(n):
    _check_range(n)
    n -= 1
    return n**5 + 1


def ease_in_out_quint(n):
    _check_range(n)
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


def ease_in_poly(n, degree=2):
    _check_range(n)
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError("degree argument must be a positive number.")
    return n**degree


def ease_out_poly(n, degree=2):
    _check_range(n)
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError("degree argument must be a positive number.")
    return 1 - abs((n - 1) ** degree)


def ease_in_out_poly(t: float, degree: float = 2):
    _check_range(t)
    if not isinstance(degree, (int, float)) or degree < 0:
        raise ValueError("degree argument must be a positive number.")
    t *= 2
    if t < 1:
        return 0.5 * t**degree
    else:
        t -= 2
        return 1 - 0.5 * abs(t**degree)


def ease_in_sine(n):
    _check_range(n)
    return -1 * math.cos(n * math.pi / 2) + 1


def ease_out_sine(n):
    _check_range(n)
    return math.sin(n * math.pi / 2)


def ease_in_out_sine(n):
    _check_range(n)
    return -0.5 * (math.cos(math.pi * n) - 1)


def ease_in_expo(n):
    _check_range(n)
    if n == 0:
        return 0
    else:
        return 2 ** (10 * (n - 1))


def ease_out_expo(n):
    _check_range(n)
    if n == 1:
        return 1
    else:
        return -(2 ** (-10 * n)) + 1


def ease_in_out_expo(n):
    _check_range(n)
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        n *= 2
        if n < 1:
            return 0.5 * 2 ** (10 * (n - 1))
        else:
            n -= 1
            return 0.5 * (-1 * (2 ** (-10 * n)) + 2)


def ease_in_circ(n):
    _check_range(n)
    return -1 * (math.sqrt(1 - n * n) - 1)


def ease_out_circ(n):
    _check_range(n)
    n -= 1
    return math.sqrt(1 - (n * n))


def ease_in_out_circ(n):
    _check_range(n)
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n -= 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)


def ease_in_elastic(n, amplitude=1, period=0.3):
    _check_range(n)
    return 1 - ease_out_elastic(1 - n, amplitude=amplitude, period=period)


def ease_out_elastic(n, amplitude=1, period=0.3):
    _check_range(n)
    if amplitude < 1:
        amplitude = 1
        s = period / 4
    else:
        s = period / (2 * math.pi) * math.asin(1 / amplitude)
    return amplitude * 2 ** (-10 * n) * math.sin((n - s) * (2 * math.pi / period)) + 1


def ease_in_out_elastic(n, amplitude=1, period=0.5):
    _check_range(n)
    n *= 2
    if n < 1:
        return ease_in_elastic(n, amplitude=amplitude, period=period) / 2
    else:
        return ease_out_elastic(n - 1, amplitude=amplitude, period=period) / 2 + 0.5


def ease_in_back(n, s=1.70158):
    _check_range(n)
    return n * n * ((s + 1) * n - s)


def ease_out_back(n, s=1.70158):
    _check_range(n)
    n -= 1
    return n * n * ((s + 1) * n + s) + 1


def ease_in_out_back(n, s=1.70158):
    _check_range(n)
    n *= 2
    if n < 1:
        s *= 1.525
        return 0.5 * (n * n * ((s + 1) * n - s))
    else:
        n -= 2
        s *= 1.525
        return 0.5 * (n * n * ((s + 1) * n + s) + 2)


def ease_in_bounce(n):
    _check_range(n)
    return 1 - ease_out_bounce(1 - n)


def ease_out_bounce(n):
    _check_range(n)
    if n < (1 / 2.75):
        return 7.5625 * n * n
    elif n < (2 / 2.75):
        n -= 1.5 / 2.75
        return 7.5625 * n * n + 0.75
    elif n < (2.5 / 2.75):
        n -= 2.25 / 2.75
        return 7.5625 * n * n + 0.9375
    else:
        n -= 2.65 / 2.75
        return 7.5625 * n * n + 0.984375


def ease_in_out_bounce(n):
    _check_range(n)
    if n < 0.5:
        return ease_in_bounce(n * 2) * 0.5
    else:
        return ease_out_bounce(n * 2 - 1) * 0.5 + 0.5
