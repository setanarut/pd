# SVG Path specification parser

from math import sqrt, cos, sin, acos, degrees, radians, log, pi
import math
from abc import ABC, abstractmethod
from bisect import bisect
import re

from pd.utils import quadratic_to_cubic, remove_doubles

COMMANDS = set("MmZzLlHhVvCcSsQqTtAa")
UPPERCASE = set("MZLHVCSQTA")

COMMAND_RE = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])")
FLOAT_RE = re.compile(rb"^[-+]?\d*\.?\d*(?:[eE][-+]?\d+)?")


class InvalidPathError(ValueError):
    pass


# The argument sequences from the grammar, made sane.
# u: Non-negative number
# s: Signed number or coordinate
# c: coordinate-pair, which is two coordinates/numbers, separated by whitespace
# f: A one character flag, doesn't need whitespace, 1 or 0
ARGUMENT_SEQUENCE = {
    "M": "c",
    "Z": "",
    "L": "c",
    "H": "s",
    "V": "s",
    "C": "ccc",
    "S": "cc",
    "Q": "cc",
    "T": "c",
    "A": "uusffc",
}


def strip_array(arg_array):
    """Strips whitespace and commas"""
    # EBNF wsp:(#x20 | #x9 | #xD | #xA) + comma: 0x2C
    while arg_array and arg_array[0] in (0x20, 0x9, 0xD, 0xA, 0x2C):
        arg_array[0:1] = b""


def pop_number(arg_array):
    res = FLOAT_RE.search(arg_array)
    if not res or not res.group():
        raise InvalidPathError(f"Expected a number, got '{arg_array}'.")
    number = float(res.group())
    start = res.start()
    end = res.end()
    arg_array[start:end] = b""
    strip_array(arg_array)

    return number


def pop_unsigned_number(arg_array):
    number = pop_number(arg_array)
    if number < 0:
        raise InvalidPathError(
            f"Expected a non-negative number, got '{number}'.")
    return number


def pop_coordinate_pair(arg_array):
    x = pop_number(arg_array)
    y = pop_number(arg_array)
    return complex(x, y)


def pop_flag(arg_array):
    flag = arg_array[0]
    arg_array[0:1] = b""
    strip_array(arg_array)
    if flag == 48:  # ASCII 0
        return False
    if flag == 49:  # ASCII 1
        return True


FIELD_POPPERS = {
    "u": pop_unsigned_number,
    "s": pop_number,
    "c": pop_coordinate_pair,
    "f": pop_flag,
}


def _commandify_path(pathdef):
    """Splits path into commands and arguments"""
    token = None
    for x in COMMAND_RE.split(pathdef):
        x = x.strip()
        if x in COMMANDS:
            if token is not None:
                yield token
            if x in ("z", "Z"):
                # The end command takes no arguments, so add a blank one
                token = (x, "")
            else:
                token = (x,)
        elif x:
            if token is None:
                raise InvalidPathError(
                    f"Path does not start with a command: {pathdef}")
            token += (x,)
    yield token


def _tokenize_path(pathdef):
    for command, args in _commandify_path(pathdef):
        # Shortcut this for the close command, that doesn't have arguments:
        if command in ("z", "Z"):
            yield (command,)
            continue

        # For the rest of the commands, we parse the arguments and
        # yield one command per full set of arguments
        arg_sequence = ARGUMENT_SEQUENCE[command.upper()]
        arguments = bytearray(args, "ascii")
        implicit = False
        while arguments:
            command_arguments = []
            for i, arg in enumerate(arg_sequence):
                try:
                    command_arguments.append(FIELD_POPPERS[arg](arguments))
                except InvalidPathError as e:
                    if i == 0 and implicit:
                        return  # Invalid character in path, treat like a comment
                    raise InvalidPathError(
                        f"Invalid path element {command} {args}"
                    ) from e

            yield (command,) + tuple(command_arguments)
            implicit = True

            # Implicit Moveto commands should be treated as Lineto commands.
            if command == "m":
                command = "l"
            elif command == "M":
                command = "L"


def parse_path(pathdef):
    from pd.path import CBezier
    segments = []
    start_pos = None
    last_command = None
    current_pos = 0

    for token in _tokenize_path(pathdef):
        command = token[0]
        relative = command.islower()
        command = command.upper()
        if command == "M":
            pos = token[1]
            if relative:
                current_pos += pos
            else:
                current_pos = pos
            # segments.append(Move(current_pos, relative=relative))
            start_pos = current_pos

        elif command == "Z":
            # For Close commands the "relative" argument just preserves case,
            # it has no different in behavior.
            # segments.append(Close(current_pos, start_pos, relative=relative))
            current_pos = start_pos

        elif command == "L":
            pos = token[1]
            if relative:
                pos += current_pos
            segments.append(SVG_Line(current_pos, pos, relative=relative))
            current_pos = pos

        elif command == "H":
            hpos = token[1]
            if relative:
                hpos += current_pos.real
            pos = complex(hpos, current_pos.imag)
            segments.append(
                SVG_Line(current_pos, pos, relative=relative, horizontal=True)
            )
            current_pos = pos

        elif command == "V":
            vpos = token[1]
            if relative:
                vpos += current_pos.imag
            pos = complex(current_pos.real, vpos)
            segments.append(
                SVG_Line(current_pos, pos, relative=relative, vertical=True)
            )
            current_pos = pos

        elif command == "C":
            control1 = token[1]
            control2 = token[2]
            end = token[3]

            if relative:
                control1 += current_pos
                control2 += current_pos
                end += current_pos

            segments.append(
                CBezier(current_pos.real, current_pos.imag, control1.real,
                        control1.imag, control2.real, control2.imag, end.real, end.imag)
            )
            current_pos = end

        elif command == "S":
            # Smooth curve. First control point is the "reflection" of
            # the second control point in the previous
            control2 = token[1]
            end = token[2]

            if relative:
                control2 += current_pos
                end += current_pos

            if last_command in "CS":
                # The first control point is assumed to be the reflection of
                # the second control point on the previous command relative
                # to the current point.
                control1 = current_pos + current_pos - segments[-1].control2
            else:
                # If there is no previous command or if the previous command
                # was not an C, c, S or s, assume the first control point is
                # coincident with the current point.
                control1 = current_pos

            segments.append(
                CBezier(current_pos.real, current_pos.imag, control1.real,
                        control1.imag, control2.real, control2.imag, end.real, end.imag)

            )
            current_pos = end

        elif command == "Q":
            control = token[1]
            end = token[2]

            if relative:
                control += current_pos
                end += current_pos

            cords = quadratic_to_cubic(current_pos.real, current_pos.imag, control.real,
                                       control.imag, end.real, end.imag)
            segments.append(CBezier(*cords))
            current_pos = end

        elif command == "T":
            # Smooth curve. Control point is the "reflection" of
            # the second control point in the previous
            end = token[1]

            if relative:
                end += current_pos

            if last_command in "QT":
                # The control point is assumed to be the reflection of
                # the control point on the previous command relative
                # to the current point.
                control = current_pos + current_pos - segments[-1].control
            else:
                # If there is no previous command or if the previous command
                # was not an Q, q, T or t, assume the first control point is
                # coincident with the current point.
                control = current_pos

            cords = quadratic_to_cubic(current_pos.real, current_pos.imag, control.real,
                                       control.imag, end.real, end.imag)
            segments.append(CBezier(*cords))
            current_pos = end

        elif command == "A":
            # For some reason I implemented the Arc with a complex radius.
            # That doesn't really make much sense, but... *shrugs*
            radius = complex(token[1], token[2])
            rotation = token[3]
            arc = token[4]
            sweep = token[5]
            end = token[6]

            if relative:
                end += current_pos

            segments.append(
                Arc(
                    current_pos, radius, rotation, arc, sweep, end, relative=relative
                )
            )
            current_pos = end

        # Finish up the loop in preparation for next command
        last_command = command
    cords = []
    for seg in segments:
        if isinstance(seg, CBezier):
            cords.extend(seg.flatten())
        if isinstance(seg, SVG_Line):
            cords.extend(seg.flatten())
    cords = remove_doubles(cords)
    return cords
    # return segments


try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

# This file contains classes for the different types of SVG path segments as
# well as a Path object that contains a sequence of path segments.

MIN_DEPTH = 5
ERROR = 1e-12


def _find_solutions_for_arc(a, b, c, d):
    """Find solution for a sin(x) + b cos(x) = 0 where x = c + d * t and t in [0, 1]"""
    if a == 0:
        # when n \in Z
        # pi / 2 + pi * n = c + d * t
        # --> n = d / pi * t - (1/2 - c/pi)
        # --> t = (pi / 2 - c + pi * n) / d
        n_ranges = [-0.5 + c / math.pi, d / math.pi - 0.5 + c / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [
            (math.pi / 2 - c + math.pi * n) / d
            for n in range(n_range_start, n_range_end + 1)
        ]
    elif b == 0:
        # when n \in Z
        # pi * n = c + d * t
        # --> n = d / pi * t + c / pi
        # --> t = (- c + pi * n) / d
        n_ranges = [c / math.pi, d / math.pi + c / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [(-c + math.pi * n) /
                  d for n in range(n_range_start, n_range_end + 1)]
    else:
        # when n \in Z
        # arct = tan^-1 (- b / a)  and
        # arct + pi * n = c + d * t
        # --> n = (c - arct + d * t) / pi
        # --> t = (arct - c + pi * n) / d
        arct = math.atan(-b / a)
        n_ranges = [(c - arct) / math.pi, d / math.pi + (c - arct) / math.pi]
        n_range_start = math.floor(min(n_ranges))
        n_range_end = math.ceil(max(n_ranges))
        t_list = [
            (arct - c + math.pi * n) / d for n in range(n_range_start, n_range_end + 1)
        ]

    t_list = [t for t in t_list if 0.0 <= t and t <= 1.0]
    return t_list


class SVG_Line():
    def __init__(self, start, end, relative=False, vertical=False, horizontal=False):
        self.start = start
        self.end = end
        self.points = [(self.start.real, self.start.imag),
                       (self.end.real, self.end.imag)]

    def flatten(self):
        return [self.start.real, self.start.imag, self.end.real, self.end.imag]
