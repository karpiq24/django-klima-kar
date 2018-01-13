import random

from apps.stats.dictionaries import COLORS


def get_random_colors(n):
    if n == 1:
        return random.choice(COLORS)
    elif n < 1:
        return None

    colors = []
    for i in range(n):
        color = random.choice(COLORS)
        while color in colors:
            color = random.choice(COLORS)
        colors.append(color)
    return colors
