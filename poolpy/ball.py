from poolpy.globals import *


class BallType(Enum):
    Solid = 1
    Stripe = 2
    Cue = 3
    Black = 4


class Ball:
    def __init__(self, x: float, y: float, color: tuple, ball_type: BallType) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.ball_type = ball_type

        self.radius = 10
        self.velocity = Vector2(0, 0)
        self.distance_rolled: float = 0

    def is_colliding_with_wall(self) -> bool:
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
        velocity_perpendicular = (self.velocity.dot(normal)) * normal
        velocity_parallel = self.velocity - velocity_perpendicular
        self.velocity = -WALL_RESTITUTION_FACTOR * velocity_perpendicular + velocity_parallel

    def is_colliding_with_ball(self, other: 'Ball') -> bool:
        distance_between_centers = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

        is_colliding = distance_between_centers < 2 * self.radius

        if is_colliding:
            away_from_ball = (Vector2(self.x, self.y) - Vector2(other.x, other.y)).normalize()
            self.x += abs(self.radius - distance_between_centers / 2) * away_from_ball.x
            self.y += abs(self.radius - distance_between_centers / 2) * away_from_ball.y

        return is_colliding

    def apply_ball_collision(self, other: 'Ball') -> None:
        vAi = self.velocity
        vBi = other.velocity
        rA = Vector2(self.x, self.y)
        rB = Vector2(other.x, other.y)
        self.velocity = vAi - ((vAi - vBi).dot(rA-rB)) / ((rB - rA).length() ** 2) * (rA - rB)
        other.velocity = vBi - ((vBi - vAi).dot(rB-rA)) / ((rA - rB).length() ** 2) * (rB - rA)

    def apply_friction(self) -> None:
        self.velocity *= TABLE_FRICTION_FACTOR

    def is_in_pocket(self) -> str | None:
        pocket_centres = {
            "top_left": (150 + 5, 100 + 5),
            "top_right": (300 + 150 - 5, 100 + 5),
            "center_left": (150, 100 + 250),
            "center_right": (300 + 150, 100 + 250),
            "bottom_left": (150 + 5, 500 + 100 - 5),
            "bottom_right": (300 + 150 - 5, 500 + 100 - 5),
        }

        for pocket, centre in pocket_centres.items():
            distance = sqrt((self.x - centre[0]) ** 2 + (self.y - centre[1]) ** 2)
            if distance < self.radius + 15:
                percent_overlap = ((self.radius + 15 - distance) ** 2) / (4 * max(self.radius, 15) ** 2)
                if percent_overlap >= 0.15:
                    return pocket

    def update(self) -> None:
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
        vcx, vcy = Globals.VIGNETTE_CENTRE
        difference_vector = Vector2(self.x, self.y) - Vector2(vcx, vcy)
        distance = difference_vector.length()
        max_shadow_radius = 10
        radius_factor = (distance / 500) * max_shadow_radius
        shadow_major_minor = difference_vector.normalize() * radius_factor
        rx, ry = shadow_major_minor
        gfxdraw.filled_ellipse(
            window,
            int(self.x + rx),
            int(self.y + ry),
            int(abs(rx) + self.radius),
            int(abs(ry) + self.radius),
            Colour.darker(TABLE_GREEN, 1.5, 50)
        )

    def draw(self, window: pygame.Surface) -> None:
        if self.ball_type == BallType.Solid:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, self.color)
        elif self.ball_type == BallType.Stripe:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius-2, BALL_WHITE)
            if 0 <= self.distance_rolled <= 25:
                pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius+1, 4)
            if 25 < self.distance_rolled <= 50:
                pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius+1, 5)
            if 50 < self.distance_rolled <= 75:
                pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius+1, 6)
            if 75 < self.distance_rolled <= 100:
                pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius+1, 5)
        elif self.ball_type == BallType.Cue:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BALL_WHITE)
        elif self.ball_type == BallType.Black:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BLACK_BALL)
