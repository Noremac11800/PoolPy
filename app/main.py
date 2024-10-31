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
from poolpy.ball import Ball
from poolpy.table import Table


if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE, vsync=1)

    pygame.display.set_caption("PoolPy")

    table = Table()
    table.rack()
    table.reset_cue_ball()

    clock =  pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mx, my = pygame.mouse.get_pos()
                    Globals.VIGNETTE_CENTER = (mx, my)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    table = Table()
                    table.rack()
                    table.reset_cue_ball()

        screen.fill(BLACK)

        if not table.is_game_over:
            table.handle_input()
            table.process_game_rules()

        table.update_balls()
        table.draw(screen)

        pygame.display.update()
        clock.tick(120)
