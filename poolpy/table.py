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
from poolpy.ball import Ball, BallType


class Table:
    """
    A class responsible for the entire logic, behaviour, and drawing of the game.
    """

    # The order of the ball types in the rack. The colours of the balls are irrelevant
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
        self.pockets: dict[str, list[Ball]] = {
            "top_left" : [],
            "top_right" : [],
            "center_left" : [],
            "center_right" : [],
            "bottom_left" : [],
            "bottom_right" : [],
        }
        self.current_player: int = 1
        self.shots_left: int = 1

        self.player1_balls: list[tuple[int, int, int]] = BALL_COLOURS.copy()
        random.shuffle(self.player1_balls)
        self.player2_balls: list[tuple[int, int, int]] = self.player1_balls.copy()

        self.player1_ball_type: BallType | None = None
        self.player2_ball_type: BallType | None = None

        self.is_turn_in_play: bool = False
        self.was_white_ball_pocketed: bool = False
        self.has_ball_been_hit_this_turn: bool = False
        self.was_wrong_ball_hit: bool = False
        self.was_wrong_ball_pocketed: bool = False
        self.was_black_ball_pocketed: bool = False
        self.is_game_over: bool = False
        self.winner: int | None = None

    @staticmethod
    def generate_triangle_pattern(radius: float, num_rows: int, offset_x: float, offset_y: float) -> list[tuple[float, float]]:
        """
        A convenience static method for producing the Cartesian coordinates that arrange circular objects of radius `radius`
        in `num_rows` rows into a down-pointed triangle pattern.
        """

        coordinates = []
        for row in range(num_rows):
            start_x = -row * radius
            y = -row * sqrt(3) * radius
            for col in range(row + 1):
                x = start_x + col * 2 * radius
                coordinates.append((x + offset_x, y + offset_y))
        return coordinates

    def rack(self) -> None:
        """
        Organises all of the balls on the table in the traditional triangular shape. The ball colours are randomised every
        time the balls are racked but their relative order is always the same.
        """

        self.balls.clear()
        for pocket in self.pockets.values():
            pocket.clear()
        if self.cue_ball is not None:
            self.balls.append(self.cue_ball)

        solids_colours = BALL_COLOURS.copy()
        stripes_colours = BALL_COLOURS.copy()
        random.shuffle(solids_colours)
        random.shuffle(stripes_colours)

        coords = Table.generate_triangle_pattern(11, 5, 150 + 150, 100 + 150)
        ball_id = 1
        for ((ball_x, ball_y), ball_type) in zip(coords, self.rack_order):
            if ball_type == BallType.Solid:
                colour = solids_colours.pop()
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type, ball_id=ball_id))
            elif ball_type == BallType.Stripe:
                colour = stripes_colours.pop()
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type, ball_id=ball_id))
            elif ball_type == BallType.Black:
                colour = BLACK_BALL
                self.balls.append(Ball(ball_x, ball_y, colour, ball_type, ball_id=ball_id))
            ball_id += 1

    def reset_cue_ball(self) -> None:
        """
        Creates a new cue ball instance and adds it to the table's array of balls.
        """

        self.cue_ball = Ball(150 + 150, 100 + 400, BALL_WHITE, BallType.Cue, ball_id=0)
        self.balls.append(self.cue_ball)

    def is_mouse_over_cue_ball(self, mx: int, my: int) -> bool:
        """
        Checks whether the mouse if over the cue ball.

        :returns: True if the mouse if over the cue ball, False otherwise.
        """

        if self.cue_ball is not None:
            return (self.cue_ball.x - mx) ** 2 + (self.cue_ball.y - my) ** 2 <= 10 ** 2
        return False

    def process_game_rules(self) -> None:
        """
        Logically steps through the pool game rules to determine the state of the game after the current play has concluded.
        A play or turn is active if any of the balls on the table are moving. This method maintains game state.
        """

        if self.is_turn_in_play:
            if not self.are_balls_moving():
                self.is_turn_in_play = False
                if self.was_black_ball_pocketed:
                    if self.was_white_ball_pocketed:
                        if self.current_player == 1:
                            self.game_over(2)
                        elif self.current_player == 2:
                            self.game_over(1)
                    elif self.current_player == 1:
                        if len(self.player1_balls) == 0:
                            self.game_over(1)
                        else:
                            self.game_over(2)
                    elif self.current_player == 2:
                        if len(self.player2_balls) == 0:
                            self.game_over(2)
                        else:
                            self.game_over(1)

                if self.was_white_ball_pocketed:
                    self.reset_cue_ball()
                    self.was_white_ball_pocketed = False
                    self.change_player()
                    if self.current_player == 1:
                        if len(self.player1_balls) == 0:
                            self.shots_left = 1
                        else:
                            self.shots_left = 2
                    elif self.current_player == 2:
                        if len(self.player2_balls) == 0:
                            self.shots_left = 1
                        else:
                            self.shots_left = 2
                elif not self.has_ball_been_hit_this_turn \
                or  self.was_wrong_ball_hit \
                or  self.was_wrong_ball_pocketed:
                    self.change_player()
                    if self.current_player == 1:
                        if len(self.player1_balls) == 0:
                            self.shots_left = 1
                        else:
                            self.shots_left = 2
                    elif self.current_player == 2:
                        if len(self.player2_balls) == 0:
                            self.shots_left = 1
                        else:
                            self.shots_left = 2
                elif self.shots_left == 0:
                    self.change_player()
                    self.shots_left = 1

                self.reset_rules()

    def game_over(self, winner: int) -> None:
        """
        Set the game as over and set the winner.
        """

        self.is_game_over = True
        self.winner = winner

    def change_player(self) -> None:
        """
        A convenience method to change the current player.
        """

        self.current_player = 1 if self.current_player == 2 else 2

    def reset_rules(self) -> None:
        """
        A convenience method to reset the rule variables.
        """

        self.has_ball_been_hit_this_turn = False
        self.was_white_ball_pocketed = False
        self.was_black_ball_pocketed = False
        self.was_wrong_ball_hit = False
        self.was_wrong_ball_pocketed = False

    def handle_input(self) -> None:
        """
        Handle input events.
        Checks if the mouse is pressed and if the mouse is over the cue ball.
        If the mouse is pressed and the mouse is over the cue ball, the cue ball is aimed.
        If the mouse is released while the cue ball is aimed, the cue ball shoots with the appropriate power.
        """

        if pygame.mouse.get_pressed()[0]:
            if not self.is_turn_in_play:
                mx, my = pygame.mouse.get_pos()
                if self.is_mouse_over_cue_ball(mx, my):
                    self.is_aiming = True
        else:
            if self.is_aiming:
                self.is_aiming = False
                self.shoot(self.get_power())

    def get_power(self) -> float:
        """
        Get the power of the cue ball.
        Calculates the power of the cue ball based on the distance of the mouse cursor from the cue ball.
        Uses the `MAX_POWER` and `MAX_POWER_LINE_LENGTH` constants to determine the maximum power.

        :return: The power factor of the shot applied to the cue ball.
        """

        mx, my = pygame.mouse.get_pos()
        mouse_pos = Vector2(mx, my)
        if self.cue_ball is not None:
            line_length = (Vector2(self.cue_ball.x, self.cue_ball.y) - mouse_pos).length()
            percent = min(1, line_length / MAX_POWER_LINE_LENGTH)
            return MAX_POWER * percent
        return 0

    def shoot(self, power: float) -> None:
        """
        Shoot the cue ball with the given power.
        Applies an instantaneous velocity to the cue ball in the aimed direction with the given power.
        """

        mx, my = pygame.mouse.get_pos()
        mouse_pos = Vector2(mx, my)
        if self.cue_ball is not None:
            direction = (Vector2(self.cue_ball.x, self.cue_ball.y) - mouse_pos).normalise()
            self.cue_ball.velocity = power * direction

        self.is_turn_in_play = True
        self.shots_left -= 1

    def are_balls_moving(self) -> bool:
        """
        Check if any ball is moving.

        :return: True if any ball is moving, False otherwise.
        """

        return any(ball.velocity.length() > 0.1 for ball in self.balls)

    def update_balls(self) -> None:
        """
        Update the balls' positions and check for ball and pocket collisions.
        """

        for ball in self.balls:
            for other_ball in self.balls:
                if ball is not other_ball:
                    self.check_collision(ball, other_ball)

            ball.update()
            self.check_pockets(ball)

    def check_collision(self, ball: Ball, other_ball: Ball) -> None:
        """
        Check if the balls are colliding and update the game state accordingly.
        """

        if ball.is_colliding_with_ball(other_ball):
            ball.apply_ball_collision(other_ball)
            if other_ball == self.cue_ball:
                if not self.has_ball_been_hit_this_turn:
                    self.has_ball_been_hit_this_turn = True
                    if not (self.player1_ball_type is None or self.player2_ball_type is None):
                        if self.current_player == 1:
                            if len(self.player1_balls) != 0:
                                if ball.ball_type != self.player1_ball_type:
                                    self.was_wrong_ball_hit = True
                        elif self.current_player == 2:
                            if len(self.player2_balls) != 0:
                                if ball.ball_type != self.player2_ball_type:
                                    self.was_wrong_ball_hit = True

    def check_pockets(self, ball: Ball) -> None:
        """
        Check if the ball has been pocketed and update the game state accordingly.
        """

        pocket = ball.is_in_pocket()
        if pocket is not None:
            self.shots_left += 1
            self.balls.remove(ball)
            if ball is self.cue_ball:
                self.was_white_ball_pocketed = True
            else:
                if ball.ball_type == BallType.Black:
                    self.was_black_ball_pocketed = True
                self.pockets[pocket].append(ball)
                if self.current_player == 1:
                    if self.player1_ball_type is None:
                        self.player1_ball_type = ball.ball_type
                        self.player2_ball_type = BallType.Solid if ball.ball_type == BallType.Stripe else BallType.Stripe
                    elif ball.ball_type != self.player1_ball_type:
                        self.was_wrong_ball_pocketed = True
                elif self.current_player == 2:
                    if self.player2_ball_type is None:
                        self.player2_ball_type = ball.ball_type
                        self.player1_ball_type = BallType.Solid if ball.ball_type == BallType.Stripe else BallType.Stripe
                    elif ball.ball_type != self.player2_ball_type:
                        self.was_wrong_ball_pocketed = True

                if ball.ball_type == self.player1_ball_type:
                    self.player1_balls.remove(ball.colour)
                elif ball.ball_type == self.player2_ball_type:
                    self.player2_balls.remove(ball.colour)

    def draw_ball_trace(self, window: pygame.Surface) -> bool:
        """
        Draw the ball trace.
        Draws a line from the cue ball to the mouse position, and then draws a circle at the closest point on the line to the ball. Ray collisions with balls take precedence over walls.
        """

        if self.cue_ball is None:
            return False

        mx, my = pygame.mouse.get_pos()
        mouse_pos = Vector2(mx, my)
        position = Vector2(self.cue_ball.x, self.cue_ball.y)
        ray_collisions = []
        for ball in self.balls:
            if ball is not self.cue_ball:
                ray_collision = Ray(position, position - mouse_pos).cast_to_circle(Vector2(ball.x, ball.y), ball.radius)
                if ray_collision is not None:
                    ray_collisions.append((ball, ray_collision))

        if len(ray_collisions) > 0:
            closest_ray_collision = min(ray_collisions, key=lambda x: (x[1] - position).length())[1]
            pygame.draw.aaline(window, WHITE, (self.cue_ball.x, self.cue_ball.y), (closest_ray_collision.x, closest_ray_collision.y))
            gfxdraw.filled_circle(window, int(closest_ray_collision.x), int(closest_ray_collision.y), self.cue_ball.radius, Colour.lighter(BALL_WHITE, 1, 100))
            return True
        return False

    def draw_wall_trace(self, window: pygame.Surface) -> None:
        """
        Draw the wall trace.
        Draws a line from the cue ball to intersecting wall, and then draws a circle at the closest point on the line to the wall. Ray collisions with balls take precedence over walls.
        """

        if self.cue_ball is None:
            return

        mx, my = pygame.mouse.get_pos()
        mouse_pos = Vector2(mx, my)
        position = Vector2(self.cue_ball.x, self.cue_ball.y)

        top_wall_ray_collision = Ray(position, position - mouse_pos) \
            .cast_to_line_segment(Vector2(150, 100), Vector2(450, 100))
        bottom_wall_ray_collision = Ray(position, position - mouse_pos) \
            .cast_to_line_segment(Vector2(150, 600), Vector2(450, 600))
        left_wall_ray_collision = Ray(position, position - mouse_pos) \
            .cast_to_line_segment(Vector2(150, 100), Vector2(150, 600))
        right_wall_ray_collision = Ray(position, position - mouse_pos) \
            .cast_to_line_segment(Vector2(450, 100), Vector2(450, 600))

        wall_collisions = [top_wall_ray_collision, bottom_wall_ray_collision, left_wall_ray_collision, right_wall_ray_collision]
        for collision in wall_collisions:
            if collision is None:
                continue
            pygame.draw.aaline(window, WHITE, (self.cue_ball.x, self.cue_ball.y), (collision.x, collision.y))
            gfxdraw.filled_circle(
                window,
                int(collision.x),
                int(collision.y),
                self.cue_ball.radius,
                Colour.lighter(BALL_WHITE, 1, 100)
            )

    def draw_pocket_indicators(self, window: pygame.Surface) -> None:
        """
        Draw the pocket indicators.
        Draws small circles near the pockets to indicate the number of balls in each pocket, and which colours were pocketed.
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
            cx, cy = center
            dx, dy = 10, 10
            match pocket:
                case "top_left":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx - dx * i, cy - dy * i, 4, WHITE)
                        gfxdraw.filled_circle(window, cx - dx * i, cy - dy * i, 3, ball.colour)
                case "top_right":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx + dx * i, cy - dy * i, 4, WHITE)
                        gfxdraw.filled_circle(window, cx + dx * i, cy - dy * i, 3, ball.colour)
                case "center_left":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx - 2 * dx * i, cy, 4, WHITE)
                        gfxdraw.filled_circle(window, cx - 2 * dx * i, cy, 3, ball.colour)
                case "center_right":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx + 2 * dx * i, cy, 4, WHITE)
                        gfxdraw.filled_circle(window, cx + 2 * dx * i, cy, 3, ball.colour)
                case "bottom_left":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx - dx * i, cy + dy * i, 4, WHITE)
                        gfxdraw.filled_circle(window, cx - dx * i, cy + dy * i, 3, ball.colour)
                case "bottom_right":
                    for (i, ball) in enumerate(self.pockets[pocket]):
                        gfxdraw.filled_circle(window, cx + dx * i, cy + dy * i, 4, WHITE)
                        gfxdraw.filled_circle(window, cx + dx * i, cy + dy * i, 3, ball.colour)

    def draw_ui(self, window: pygame.Surface) -> None:
        """
        Draw the UI. Includes the game over UI.
        """

        title = CASINO.render("PoolPy", True, WHITE)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2,  0))

        p1_shots = '+' + str(self.shots_left) if self.current_player == 1 else ""
        p2_shots = '+' + str(self.shots_left)if self.current_player == 2 else ""
        player1 = PLAYER.render("Player 1 " + p1_shots, True, PLAYER_RED)
        player2 = PLAYER.render("Player 2 " + p2_shots, True, PLAYER_BLUE)

        window.blit(player1, (30, 20))
        window.blit(player2, (WIDTH - player2.get_width() - 30, 20))

        # Draw player remaining balls indicators
        gap = 20
        for i, colour in enumerate(self.player1_balls):
            gfxdraw.filled_circle(window, 30 + i * gap, 60, 8, WHITE)
            gfxdraw.filled_circle(window, 30 + i * gap, 60, 7, colour)
        for i, colour in enumerate(self.player2_balls):
            gfxdraw.filled_circle(window, WIDTH - 30 - i * gap, 60, 8, WHITE)
            gfxdraw.filled_circle(window, WIDTH - 30 - i * gap, 60, 7, colour)

        # Draw game over messages
        if self.is_game_over:
            winner = "Player 1" if self.winner == 1 else "Player 2"
            colour = PLAYER_RED if self.winner == 1 else PLAYER_BLUE
            winner_label = PLAYER.render(f"{winner} Wins!", True, colour)
            window.blit(
                winner_label,
                (WIDTH // 2 - winner_label.get_width() // 2, HEIGHT // 2 - winner_label.get_height() // 2))

            restart_label = DEBUG.render("Press R to restart", True, WHITE)
            window.blit(
                restart_label,
                (WIDTH // 2 - restart_label.get_width() // 2, HEIGHT // 2 + winner_label.get_height() // 2 + 20))

        if DEBUG_ON:
            self.draw_debug_info(window)

    def draw_debug_info(self, window: pygame.Surface) -> None:
        """
        Draw debug info

        Current player's turn
        Shots left
        If white ball pocketed
        If wrong ball hit
        If wrong ball pocketed
        Player 1's ball type
        Player 2's ball type
        """

        current_player_label = DEBUG.render(f"Player {self.current_player}", True, WHITE)
        window.blit(current_player_label, (10, 100))
        shots_left_label = DEBUG.render(f"Shots left: {self.shots_left}", True, WHITE)
        window.blit(shots_left_label, (10, 140))

        l1 = DEBUG.render(f"white ball pocketed: {self.was_white_ball_pocketed}", True, WHITE)
        l2 = DEBUG.render(f"wrong ball hit: {self.was_wrong_ball_hit}", True, WHITE)
        l3 = DEBUG.render(f"wrong ball pocketed: {self.was_wrong_ball_pocketed}", True, WHITE)
        window.blit(l1, (10, 180))
        window.blit(l2, (10, 220))
        window.blit(l3, (10, 260))

        p1_ball_type_label = DEBUG.render(f"Player 1 ball type: {self.player1_ball_type}", True, WHITE)
        p2_ball_type_label = DEBUG.render(f"Player 2 ball type: {self.player2_ball_type}", True, WHITE)
        window.blit(p1_ball_type_label, (10, 300))
        window.blit(p2_ball_type_label, (10, 340))

    def draw_table(self, window: pygame.Surface) -> None:
        """
        Draw the table
        """

        gfxdraw.box(window, pygame.Rect(150, 100, 300, 500), TABLE_GREEN)

        # Draw cue lines
        gfxdraw.line(window, 150, 100 + 400, 150 + 300, 100 + 400, WHITE)
        gfxdraw.arc(window, 150 + 150, 100 + 400, 50, 0, 180, WHITE)
        gfxdraw.filled_circle(window, 150 + 150 + 50, 100 + 400, 5, POCKET_BLACK)
        gfxdraw.filled_circle(window, 150 + 150, 100 + 400, 5, POCKET_BLACK)
        gfxdraw.filled_circle(window, 150 + 150 - 50, 100 + 400, 5, POCKET_BLACK)

        # Draw ball shadows
        for ball in self.balls:
            ball.draw_shadow(window)

        # Draw cushions/edges
        gfxdraw.box(window, pygame.Rect(130, 80, 20, 540), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(130, 80, 340, 20), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(300 + 150, 80, 20, 540), WOODEN_BROWN)
        gfxdraw.box(window, pygame.Rect(130, 500 + 100, 340, 20), WOODEN_BROWN)

        # Draw top pockets
        gfxdraw.filled_circle(window, 150 + 5, 100 + 5, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150 - 5, 100 + 5, 15, POCKET_BLACK)

        # Draw center pockets
        gfxdraw.filled_circle(window, 150, 100 + 250, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150, 100 + 250, 15, POCKET_BLACK)

        # Draw bottom pockets
        gfxdraw.filled_circle(window, 150 + 5, 500 + 100 - 5, 15, POCKET_BLACK)
        gfxdraw.filled_circle(window, 300 + 150 - 5, 500 + 100 - 5, 15, POCKET_BLACK)

    def draw(self, window: pygame.Surface) -> None:
        """
        Draw the table, balls, lighting, shadows, and UI.
        """

        # Draw table
        self.draw_table(window)

        # Draw balls
        for ball in self.balls:
            ball.draw(window)

        # Draw aiming line
        if self.is_aiming and self.cue_ball is not None:
            mx, my = pygame.mouse.get_pos()
            mouse_pos = Vector2(mx, my)
            pygame.draw.aaline(window, WHITE, (mx, my), (self.cue_ball.x, self.cue_ball.y))
            if not self.draw_ball_trace(window):
                self.draw_wall_trace(window)

        # Vignette/lighting
        for r in range(0, 400, 25):
            gfxdraw.filled_circle(window, *Globals.VIGNETTE_CENTER, r, VIGNETTE_YELLOW)

        # Draw pocket indicators
        self.draw_pocket_indicators(window)

        # Draw UI
        self.draw_ui(window)
