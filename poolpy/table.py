from poolpy.globals import *
from poolpy.ball import Ball, BallType


class Table:
    rack_order = [
        BallType.Solid,
        BallType.Stripe,
        BallType.Stripe,
        BallType.Solid,
        BallType.Black,
        BallType.Stripe,
        BallType.Stripe,
        BallType.Solid,
        BallType.Solid,
        BallType.Stripe,
        BallType.Stripe,
        BallType.Solid,
        BallType.Stripe,
        BallType.Solid,
        BallType.Solid,
    ]

    def __init__(self) -> None:
        self.balls: list[Ball] = []
        self.cue_ball: Ball | None = None
        self.is_aiming: bool = False

        self.was_collision_this_frame: bool = False

    @staticmethod
    def generate_triangle_pattern(radius: float, num_rows: int, offset_x: float, offset_y: float) -> list[tuple[float, float]]:
        coordinates = []
        for row in range(num_rows):
            start_x = -row * radius
            y = -row * sqrt(3) * radius
            for col in range(row + 1):
                x = start_x + col * 2 * radius
                coordinates.append((x + offset_x, y + offset_y))
        return coordinates

    def rack(self) -> None:
        solids_colours = BALL_COLOURS.copy()
        stripes_colours = BALL_COLOURS.copy()
        random.shuffle(solids_colours)
        random.shuffle(stripes_colours)

        coords = Table.generate_triangle_pattern(11, 5, 150 + 150, 100 + 150)
        for ((ball_x, ball_y), ball_type) in zip(coords, self.rack_order):
            if ball_type == BallType.Solid:
                colour = solids_colours.pop()
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type))
            elif ball_type == BallType.Stripe:
                colour = stripes_colours.pop()
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type))
            elif ball_type == BallType.Black:
                colour = BLACK_BALL
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type))

        self.cue_ball = Ball(150 + 150, 100 + 400, BALL_WHITE, BallType.Cue)
        self.balls.append(self.cue_ball)

    def reset_cue_ball(self) -> None:
        self.cue_ball = Ball(150 + 150, 100 + 400, BALL_WHITE, BallType.Cue)
        self.balls.append(self.cue_ball)

    def is_mouse_over_cue_ball(self, mx: int, my: int) -> bool:
        if self.cue_ball is not None:
            return (self.cue_ball.x - mx) ** 2 + (self.cue_ball.y - my) ** 2 <= 10 ** 2
        return False

    def get_power(self) -> float:
        mx, my = pygame.mouse.get_pos()
        if self.cue_ball is not None:
            line_length = (self.cue_ball.x - mx) ** 2 + (self.cue_ball.y - my) ** 2
            percent = min(1, line_length / MAX_POWER_LINE_LENGTH)
            return MAX_POWER * percent
        return 0

    def shoot(self, power: float) -> None:
        mx, my = pygame.mouse.get_pos()
        mouse_pos = Vector2(mx, my)
        if self.cue_ball is not None:
            direction = Vector2(self.cue_ball.x, self.cue_ball.y) - mouse_pos
            self.cue_ball.velocity = power * direction

    def update_balls(self) -> None:
        self.was_collision_this_frame = False
        for ball in self.balls:
            for other_ball in self.balls:
                if ball is not other_ball:
                    if ball.is_colliding_with_ball(other_ball):
                        self.was_collision_this_frame = True
                        ball.apply_ball_collision(other_ball)
            ball.update()

            if ball.is_in_pocket() is not None:
                self.balls.remove(ball)
                if ball is self.cue_ball:
                    self.reset_cue_ball()

    def draw(self, window: pygame.Surface) -> None:
        gfxdraw.box(window, pygame.Rect(150, 100, 300, 500), TABLE_GREEN)
        gfxdraw.box(window, pygame.Rect(130, 80, 20, 540), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(130, 80, 340, 20), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(300 + 150, 80, 20, 540), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(130, 500 + 100, 340, 20), WOODEN_BROWN)

        # Top pockets
        gfxdraw.filled_circle(window, 150 + 5, 100 + 5, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150 - 5, 100 + 5, 15, POCKET_BLACK)

        # Center pockets
        gfxdraw.filled_circle(window, 150, 100 + 250, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150, 100 + 250, 15, POCKET_BLACK)

        # Bottom pockets
        gfxdraw.filled_circle(window, 150 + 5, 500 + 100 - 5, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150 - 5, 500 + 100 - 5, 15, POCKET_BLACK)

        # Cue lines
        gfxdraw.line(window, 150, 100 + 400, 150 + 300, 100 + 400, WHITE)
        gfxdraw.arc(window, 150 + 150, 100 + 400, 50, 0, 180, WHITE)
        gfxdraw.filled_circle(window, 150 + 150 + 50, 100 + 400, 5, POCKET_BLACK)
        gfxdraw.filled_circle(window, 150 + 150, 100 + 400, 5, POCKET_BLACK)
        gfxdraw.filled_circle(window, 150 + 150 - 50, 100 + 400, 5, POCKET_BLACK)

        for ball in self.balls:
            ball.draw(window)

        if self.is_aiming and self.cue_ball is not None:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.aaline(window, WHITE, (mx, my), (self.cue_ball.x, self.cue_ball.y))
