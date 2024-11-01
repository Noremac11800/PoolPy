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

from enum import Enum
from math import sqrt
import random

import pygame
from pygame import gfxdraw

from poolpy.utils import *

# Audio
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)
CLINK = pygame.mixer.Sound("./poolpy/assets/clink_trimmed.wav")

# Fonts
CASINO = pygame.font.Font("./poolpy/assets/casino.ttf", 60)
PLAYER = pygame.font.Font("./poolpy/assets/player.otf", 24)
DEBUG = pygame.font.Font("./poolpy/assets/player.otf", 14)

DEBUG_ON = False        # Debug mode flag

WIDTH = 600             # Default window width
HEIGHT = 700            # Default window height

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
VIGNETTE_WHITE = (255, 255, 255, 5)
VIGNETTE_YELLOW = (255, 221, 0, 5)
PLAYER_RED = (227, 66, 66)
PLAYER_BLUE = (0, 121, 234)

# Pool ball colours
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

# Pool table colours
TABLE_GREEN = (26, 89, 46)
WOODEN_BROWN = (139, 69, 19)
POCKET_BLACK = (46, 46, 46)

# Physics constants
MAX_POWER = 20                      # The maximum power that can be applied to the cue ball in a given shot
MAX_POWER_LINE_LENGTH = 150         # The maximum length of the power line in a given shot (in pixels)
TABLE_FRICTION_FACTOR = 0.990       # The friction factor of the table
WALL_RESTITUTION_FACTOR = 0.80      # The wall restitution factor. How much energy wall collisions take from the ball


class Globals:
    """
    A global singleton which is modifiable at runtime and available to all other modules.
    """

    # The coordinates of the center of the light source
    VIGNETTE_CENTER: tuple[int, int] = (WIDTH // 2, 30)
