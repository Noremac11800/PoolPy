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
        self.position_before_collision: Vector2 = Vector2(x, y)
        self.has_processed_collision_this_frame: bool = False

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
        if self.has_processed_collision_this_frame:
            return False

        is_colliding = (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (2 * self.radius) ** 2
        if is_colliding:
            self.x, self.y = self.position_before_collision
            self.has_processed_collision_this_frame = True
            other.has_processed_collision_this_frame = True
            # if self.velocity.length() <= 1:
            #     self.velocity = self.velocity.normalize() * 5
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

    def update(self) -> None:
        self.is_colliding_with_wall()
        self.apply_friction()

        self.position_before_collision = Vector2(self.x, self.y)
        if self.velocity.length() <= 0.1:
            self.velocity = Vector2()
        self.x += self.velocity.x
        self.y += self.velocity.y

        self.has_processed_collision_this_frame = False

    def draw(self, window: pygame.Surface) -> None:
        if self.ball_type == BallType.Solid:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, self.color)
        elif self.ball_type == BallType.Stripe:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius-2, BALL_WHITE)
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius+1, 4)
        elif self.ball_type == BallType.Cue:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BALL_WHITE)
        elif self.ball_type == BallType.Black:
            gfxdraw.filled_circle(window, int(self.x), int(self.y), self.radius, BLACK_BALL)
