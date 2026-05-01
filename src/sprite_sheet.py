import pygame

from typing import Self

from consts import FPS

class SpriteSheet:
    def __init__(self, filename: str) -> None:
        self.sheet: pygame.Surface = pygame.image.load(filename).convert_alpha()

    def image_at(self, rectangle: pygame.Rect  | tuple[int,int,int,int]):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0,0), rect)
        return image

    def images_at(self, rects: list[pygame.Rect] | list[tuple[int,int,int,int]]) -> list[pygame.Surface]:
        return [self.image_at(rect) for rect in rects]

    def load_strip(self, rect: pygame.Rect | tuple[int,int,int,int], image_count: int) -> list[pygame.Surface]:
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3]) for x in range(image_count)]
        return self.images_at(tups)

class AnimatedSpriteSheet:
    def __init__(self,
            filename: str,
            rect: pygame.Rect | tuple[int,int,int,int],
            count: int,
            loop: bool=True,
            frames: int=1
        ):
        ss = SpriteSheet(filename)
        self._index: int = 0
        self._sprites: list[pygame.Surface] = ss.load_strip(rect, count)
        self._frames: int = frames
        self._f: int = frames
        self._loop: bool = loop
        self.rect: pygame.Rect = pygame.Rect(rect)

    def iter(self) -> Self:
        self._index = 0
        self._f = self._frames
        return self

    def next(self) -> pygame.Surface:
        if self._index >= len(self._sprites):
            if self._loop:
                self._index = 0
            else:
                raise StopIteration
        image = self._sprites[self._index]
        self._f -= 1
        if self._f == 0:
            self._index += 1
            self._f = self._frames
        return image

    def change_speed(self, speed: int) -> None:
        self._frames = int(FPS / speed)
        self._f = self._frames
