# -----------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2024 Cameron Kirk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

from math import sqrt
from typing import Iterator


class Vector2:
    """
    A utility 2D vector class to easily enable physics calculations like velocity and position changes.
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        """
        Initialises a new Vector2 object. Defaults to the origin zero vector (0, 0).

        :params:
            x (float, optional): The x-coordinate of the vector. Defaults to 0.
            y (float, optional): The y-coordinate of the vector. Defaults to 0.
        """

        self.x = x
        self.y = y

    def length(self) -> float:
        """
        Calculates the length of the vector.

        :returns: float: The length of the vector.
        """

        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalise(self) -> 'Vector2':
        """
        Normalises the vector by constraining its length to 1.

        :returns: Vector2: The normalised vector.
        """

        mag = self.length()
        if mag != 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2()

    def dot(self, other: 'Vector2') -> float:
        """
        Calculates the dot product of two vectors.

        :param: other (Vector2): The other vector to calculate the dot product with.
        :returns: float: The dot product of the two vectors.
        """

        return self.x * other.x + self.y * other.y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        """
        Adds two vectors together.

        :param: other (Vector2): The other vector to add to the current vector.
        :returns: Vector2: The resulting vector after adding the two vectors together.
        """

        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """
        Subtracts two vectors.

        :param: other (Vector2): The other vector to subtract from the current vector.
        :returns: Vector2: The resulting vector after subtracting the two vectors.
        """

        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        """
        Multiplies a vector by a scalar. The scalar must appear on the right side of the multiplication.

        :param: scalar (float): The scalar to multiply the vector by.
        :returns: Vector2: The resulting vector after multiplying the vector by the scalar.
        """

        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2':
        """
        Multiplies a vector by a scalar. The scalar must appear on the left side of the multiplication.

        :param: scalar (float): The scalar to multiply the vector by.
        :returns: Vector2: The resulting vector after multiplying the vector by the scalar.
        """

        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        """
        Divides a vector by a scalar. The scalar must appear on the right side of the division.

        :param: scalar (float): The scalar to divide the vector by.
        :returns: Vector2: The resulting vector after dividing the vector by the scalar.
        """

        return Vector2(self.x / scalar, self.y / scalar)

    def __iter__(self) -> Iterator[float]:
        """
        A convenience method to allow for iteration over the x and y coordinates of the vector.

        :returns: Iterator[float]: An iterator over the x and y coordinates of the vector.
        """

        return iter((self.x, self.y))

    def __str__(self) -> str:
        """
        A convenience method to convert the vector to a string representation.

        :returns: str: A string representation of the vector in the form "Vector2(x, y)".
        """

        return f"Vector2({self.x}, {self.y})"


class Ray:
    """
    A utility ray casting class to easily enable physics calculations like projected collisions.
    """

    def __init__(self, position: Vector2, direction: Vector2) -> None:
        """
        Initialises a new Ray object.

        :params:
            position (Vector2): The starting position of the ray.
            direction (Vector2): The direction of the ray. Recommended to use a normalised vector.
        """

        self.position = position
        self.direction = direction.normalise()

    def cast_to_line_segment(self, start: Vector2, end: Vector2) -> Vector2 | None:
        """
        Casts a ray to a line segment.

        :params:
            start (Vector2): The starting point of the line segment.
            end (Vector2): The ending point of the line segment.
        :returns: Vector2 | None: The intersection point of the ray and the line segment if it exists, None otherwise.
        """

        x0, y0 = self.position
        dx, dy = self.direction
        x1, y1 = start
        x2, y2 = end
        try:
            t = ((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) / (dx * (y2 - y1) - dy * (x2 - x1))
            u = ((x1 - x0) * dy - (y1 - y0) * dx) / (dx * (y2 - y1) - dy * (x2 - x1))
        except ZeroDivisionError:
            return None
        if (t >= 0) and (0 <= u <= 1):
            return self.position + t * self.direction
        return None

    def cast_to_circle(self, center: Vector2, radius: int) -> Vector2 | None:
        """
        Casts a ray to a circle of radius `radius` centered at `center`.

        :params:
            center (Vector2): The center of the circle.
            radius (int): The radius of the circle.
        :returns: Vector2 | None: The intersection point of the ray and the circle if it exists, None otherwise.
        """

        x0, y0 = self.position
        dx, dy = self.direction
        cx, cy = center
        b = (x0 - cx) * dx + (y0 - cy) * dy
        c = (x0 - cx) ** 2 + (y0 - cy) ** 2 - radius ** 2

        if b ** 2 - c >= 0:
            t = -b - sqrt(b ** 2 - c)
            if t >= 0:
                return self.position + t * self.direction
        return None


class Colour:
    """
    A utility class to manipulate the brightness and transparency of colours.
    """

    @staticmethod
    def lighter(
        colour: tuple[int, int, int] | tuple[int, int, int, int],
        amount: float,
        alpha: int=255) -> tuple[int, int, int, int]:
        """
        Lightens a colour by a given amount. If an alpha value is provided, it will be preserved.

        :params:
            colour (tuple[int, int, int] | tuple[int, int, int, int]): The colour to lighten.
            amount (float): The amount to lighten the colour by.
                            A value of 1 does nothing.
                            A value of 2 doubles the brightness.
                            A value of 0.5 halves the brightness.
            alpha (int, optional): The alpha value of the colour. Defaults to 255.
        :returns: tuple[int, int, int, int]: The lighter colour.
        """

        if len(colour) == 3:
            colour = (colour[0], colour[1], colour[2], alpha)
        r, g, b, a = colour
        return (int(r * amount), int(g * amount), int(b * amount), a)

    @staticmethod
    def darker(
        colour: tuple[int, int, int] | tuple[int, int, int, int],
        amount: float,
        alpha: int=255) -> tuple[int, int, int, int]:
        """
        Darkens a colour by a given amount. If an alpha value is provided, it will be preserved.

        :params:
            colour (tuple[int, int, int] | tuple[int, int, int, int]): The colour to darken.
            amount (float): The amount to darken the colour by.
                            A value of 1 does nothing.
                            A value of 2 doubles the darkness.
                            A value of 0.5 halves the darkness.
            alpha (int, optional): The alpha value of the colour. Defaults to 255.
        :returns: tuple[int, int, int, int]: The darker colour.
        """

        if len(colour) == 3:
            colour = (colour[0], colour[1], colour[2], alpha)
        r, g, b, a = colour
        return (int(r / amount), int(g / amount), int(b / amount), a)
