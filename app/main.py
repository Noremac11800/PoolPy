from poolpy.globals import *
from poolpy.ball import Ball
from poolpy.table import Table


if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE, vsync=1)

    pygame.display.set_caption("PoolPy")

    table = Table()
    table.rack()

    clock =  pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mx, my = pygame.mouse.get_pos()
                    Globals.VIGNETTE_CENTRE = (mx, my)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if table.is_mouse_over_cue_ball(mx, my):
                table.is_aiming = True
        else:
            if table.is_aiming:
                table.is_aiming = False
                table.shoot(table.get_power())


        screen.fill(BLACK)

        table.update_balls()
        table.draw(screen)

        pygame.display.update()
        clock.tick(120)
