from enum import Enum
from math import sqrt
import random

import pygame
from pygame import gfxdraw

from poolpy.utils import *

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)
CLINK = pygame.mixer.Sound("./poolpy/assets/clink_trimmed.wav")

WIDTH = 600
HEIGHT = 700

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
VIGNETTE_WHITE = (255, 255, 255, 5)
VIGNETTE_YELLOW = (255, 221, 0, 5)

# Pool ball colors
YELLOW = (255, 204, 0)
BLUE = (0, 121, 234)
RED = (222, 35, 35)
PURPLE = (156, 44, 212)
ORANGE = (255, 102, 0)
GREEN = (0, 200, 0)
BURGUNDY = (128, 0, 32)
BLACK_BALL = (32, 32, 32)
BALL_WHITE = (245, 245, 245)
BALL_COLOURS = [
    YELLOW,
    BLUE,
    RED,
    PURPLE,
    ORANGE,
    GREEN,
    BURGUNDY,
]

# Pool table colors
TABLE_GREEN = (26, 89, 46)
WOODEN_BROWN = (139, 69, 19)
POCKET_BLACK = (46, 46, 46)

# Fonts
FONT = pygame.font.SysFont("Optima", 20)

MAX_POWER = 0.1
MAX_POWER_LINE_LENGTH = 75
TABLE_FRICTION_FACTOR = 0.99
WALL_RESTITUTION_FACTOR = 0.80

class Globals:
    VIGNETTE_CENTRE: tuple[int, int] = (WIDTH // 2, HEIGHT // 2)
