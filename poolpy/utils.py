from math import sqrt
from typing import Iterator


class Vector2:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y

    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self) -> 'Vector2':
        mag = self.length()
        if mag != 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2()

    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))

    def __str__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


class Ray:
    def __init__(self, position: Vector2, direction: Vector2) -> None:
        self.position = position
        self.direction = direction.normalize()

    def cast_to_line_segment(self, start: Vector2, end: Vector2) -> Vector2 | None:
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

    def cast_to_circle(self, centre: Vector2, radius: int) -> Vector2 | None:
        x0, y0 = self.position
        dx, dy = self.direction
        cx, cy = centre
        b = (x0 - cx) * dx + (y0 - cy) * dy
        c = (x0 - cx) ** 2 + (y0 - cy) ** 2 - radius ** 2

        if b ** 2 - c >= 0:
            t = -b - sqrt(b ** 2 - c)
            if t >= 0:
                return self.position + t * self.direction
        return None


class Colour:
    @staticmethod
    def lighter(colour: tuple[int, int, int] | tuple[int, int, int, int], amount: float, alpha: int=255) -> tuple[int, int, int, int]:
        if len(colour) == 3:
            colour = (colour[0], colour[1], colour[2], alpha)
        r, g, b, a = colour
        return (int(r * amount), int(g * amount), int(b * amount), a)

    @staticmethod
    def darker(colour: tuple[int, int, int] | tuple[int, int, int, int], amount: float, alpha: int=255) -> tuple[int, int, int, int]:
        if len(colour) == 3:
            colour = (colour[0], colour[1], colour[2], alpha)
        r, g, b, a = colour
        return (int(r / amount), int(g / amount), int(b / amount), a)
