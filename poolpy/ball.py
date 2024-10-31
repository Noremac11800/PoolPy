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

from poolpy.globals import *


class BallType(Enum):
    """
    A convenience enum to represent the differe ball types in pool.
    """

    Solid = 1
    Stripe = 2
    Cue = 3
    Black = 4


class Ball:
    """
    A ball object that represents a ball in pool.
    """

    def __init__(self, x: float, y: float, colour: tuple[int, int, int], ball_type: BallType, ball_id: int=-1) -> None:
        """
        Initializes a new Ball object.

        :params:
            x (float): The x-coordinate of the ball.
            y (float): The y-coordinate of the ball.
            colour (tuple[int, int, int]): The colour of the ball.
            ball_type (BallType): The type of the ball.
            ball_id (int, optional): The ID of the ball. Defaults to -1.
        """

        self.x = x
        self.y = y
        self.colour = colour
        self.ball_type = ball_type
        self.ball_id = ball_id

        self.radius = 10
        self.velocity = Vector2(0, 0)
        self.distance_rolled: float = 0
        self.channel: pygame.mixer.Channel = pygame.mixer.Channel(self.ball_id)

    def is_colliding_with_wall(self) -> bool:
        """
        Checks if the ball is colliding with the wall.

        :returns: bool: True if the ball is colliding with the wall, False otherwise.
        """

        # Top
        if self.y - self.radius <= 100:
            self.y = 100 + self.radius
            self.apply_wall_collision(Vector2(0, 1))
            return True

        # Bottom
        if self.y + self.radius >= 600:
            self.y = 600 - self.radius
            self.apply_wall_collision(Vector2(0, -1))
            return True

        # Left
        if self.x - self.radius <= 150:
            self.x = 150 + self.radius
            self.apply_wall_collision(Vector2(1, 0))
            return True

        # Right
        if self.x + self.radius >= 450:
            self.x = 450 - self.radius
            self.apply_wall_collision(Vector2(-1, 0))
            return True

        return False

    def apply_wall_collision(self, normal: Vector2) -> None:
        """
        Applies wall collision to the ball.

        :param: normal (Vector2): The normal vector of the wall collision. The normal vector should be normalised.
        """

        velocity_perpendicular = (self.velocity.dot(normal)) * normal
        velocity_parallel = self.velocity - velocity_perpendicular
        self.velocity = -WALL_RESTITUTION_FACTOR * velocity_perpendicular + velocity_parallel

    def is_colliding_with_ball(self, other: 'Ball') -> bool:
        """
        Checks if the ball is colliding with another ball.

        :param: other (Ball): The other ball to check for collision.
        :returns: bool: True if the ball is colliding with the other ball, False otherwise.
        """

        distance_between_centers = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

        is_colliding = distance_between_centers < 2 * self.radius

        if is_colliding:
            away_from_ball = (Vector2(self.x, self.y) - Vector2(other.x, other.y)).normalise()
            self.x += abs(self.radius - distance_between_centers / 2) * away_from_ball.x
            self.y += abs(self.radius - distance_between_centers / 2) * away_from_ball.y

        return is_colliding

    def apply_ball_collision(self, other: 'Ball') -> None:
        """
        Applies ball collision to the ball using simple elastic collision.

        :param: other (Ball): The other ball to apply collision to.
        """
        vAi = self.velocity
        vBi = other.velocity
        rA = Vector2(self.x, self.y)
        rB = Vector2(other.x, other.y)
        self.velocity = vAi - ((vAi - vBi).dot(rA-rB)) / ((rB - rA).length() ** 2) * (rA - rB)
        other.velocity = vBi - ((vBi - vAi).dot(rB-rA)) / ((rA - rB).length() ** 2) * (rB - rA)

        volume = min(self.velocity.length(), 10) / 10
        self.channel.set_volume(volume)
        self.channel.play(CLINK)

    def apply_friction(self) -> None:
        """
        Applies table friction to the ball using the `TABLE_FRICTION_FACTOR` constant.
        """

        self.velocity *= TABLE_FRICTION_FACTOR

    def is_in_pocket(self) -> str | None:
        """
        Checks if the ball is in a pocket.

        :returns: str | None: The name of the pocket if the ball is in a pocket, None otherwise.
        """

        pocket_centers = {
            "top_left": (150 + 5, 100 + 5),
            "top_right": (300 + 150 - 5, 100 + 5),
            "center_left": (150, 100 + 250),
            "center_right": (300 + 150, 100 + 250),
            "bottom_left": (150 + 5, 500 + 100 - 5),
            "bottom_right": (300 + 150 - 5, 500 + 100 - 5),
        }

        for pocket, center in pocket_centers.items():
            distance = sqrt((self.x - center[0]) ** 2 + (self.y - center[1]) ** 2)
            if distance < self.radius + 15:
                percent_overlap = ((self.radius + 15 - distance) ** 2) / (4 * max(self.radius, 15) ** 2)
                if percent_overlap >= 0.15:
                    return pocket

    def update(self) -> None:
        """
        Updates the ball's position and velocity. Takes collisions and friction into account.
        """

        self.is_colliding_with_wall()
        self.apply_friction()

        if self.velocity.length() <= 0.1:
            self.velocity = Vector2()
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.distance_rolled += self.velocity.length()
        if self.distance_rolled > 100:
            self.distance_rolled = 0

    def draw_shadow(self, window: pygame.Surface) -> None:
        """
        Draws the ball's shadow on the table relative to the light's position.

        :param: window (pygame.Surface): The window to draw the shadow on.
        """

        vcx, vcy = Globals.VIGNETTE_CENTER
        difference_vector = Vector2(self.x, self.y) - Vector2(vcx, vcy)
        distance = difference_vector.length()
        max_shadow_radius = 10
        radius_factor = (distance / 500) * max_shadow_radius
        shadow_major_minor = difference_vector.normalise() * radius_factor
        rx, ry = shadow_major_minor
        gfxdraw.filled_ellipse(
            window,
            int(self.x + rx),
            int(self.y + ry),
            int(abs(rx) + self.radius),
            int(abs(ry) + self.radius),
            Colour.darker(TABLE_GREEN, 1.5, 100)
        )

    def draw(self, window: pygame.Surface) -> None:
        """
        Draws the ball on the table.

        :param: window (pygame.Surface): The window to draw the ball on.
        """

        if self.ball_type == BallType.Solid:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, self.colour)
        elif self.ball_type == BallType.Stripe:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius-2, BALL_WHITE)
            if 0 <= self.distance_rolled <= 25:
                pygame.draw.circle(window, self.colour, (int(self.x), int(self.y)), self.radius+1, 4)
            if 25 < self.distance_rolled <= 50:
                pygame.draw.circle(window, self.colour, (int(self.x), int(self.y)), self.radius+1, 5)
            if 50 < self.distance_rolled <= 75:
                pygame.draw.circle(window, self.colour, (int(self.x), int(self.y)), self.radius+1, 6)
            if 75 < self.distance_rolled <= 100:
                pygame.draw.circle(window, self.colour, (int(self.x), int(self.y)), self.radius+1, 5)
        elif self.ball_type == BallType.Cue:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BALL_WHITE)
        elif self.ball_type == BallType.Black:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BLACK_BALL)
