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
