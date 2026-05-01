import time

import pygame

from random import randint, random

from sprite_sheet import AnimatedSpriteSheet
from consts import SIZE

class PreysFood:
    sprite: pygame.Surface
    def __init__(self) -> None:
        self.update_position()
        self.eaten: bool = False
        self.last_eaten: float | None = None
        self.rand_tick: float = 0.0

    def update_position(self) -> None:
        self.x: int = randint(0, SIZE.WIDTH)
        self.y: int = randint(0, SIZE.HEIGHT)
        self.rect = pygame.Rect(self.x, self.y, 32, 32)

    def update(self) -> None:
        if self.eaten and not self.last_eaten:
            self.last_eaten = time.time()
            self.rand_tick = random() * 3
        if self.last_eaten and time.time() - self.last_eaten > 2:
            self.last_eaten = None
            self.eaten = False
            self.update_position()

    def draw(self, surface: pygame.Surface) -> None:
        if self.eaten:
            return
        surface.blit(pygame.transform.rotozoom(self.sprite, 0, 1), self.rect)

    @classmethod
    def sprite_init(cls) -> None:
        cls.sprite = AnimatedSpriteSheet(
        filename="assets\\food_sheet.png",
        rect=(0, 0, 32, 32),
        count=1,
        loop=True,
        frames=10
    ).next()
