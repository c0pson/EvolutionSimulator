import pygame
from random import randint
from consts import SIZE

class Obstacle:
    COLOR = (101, 115, 78)
    BORDER_COLOR = (78, 90, 58)

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.rect = pygame.Rect(x, y, w, h)

    @classmethod
    def spawn_random(cls, count: int, min_size: int = 40, max_size: int = 120) -> list["Obstacle"]:
        margin = 60
        obstacles: list[Obstacle] = []
        attempts = 0
        while len(obstacles) < count and attempts < count * 20:
            w = randint(min_size, max_size)
            h = randint(min_size, max_size)
            x = randint(margin, SIZE.WIDTH - w - margin)
            y = randint(margin, SIZE.HEIGHT - h - margin)
            candidate = pygame.Rect(x, y, w, h)
            if not any(candidate.inflate(20, 20).colliderect(o.rect) for o in obstacles):
                obstacles.append(cls(x, y, w, h))
            attempts += 1
        return obstacles

    def collides_point(self, x: float, y: float) -> bool:
        return self.rect.collidepoint(int(x), int(y))

    def push_out(self, x: float, y: float, radius: float = 16.0) -> tuple[float, float]:
        if not self.rect.collidepoint(int(x), int(y)):
            return x, y
        left_d  = x - self.rect.left
        right_d = self.rect.right - x
        top_d   = y - self.rect.top
        bot_d   = self.rect.bottom - y
        min_d = min(left_d, right_d, top_d, bot_d)
        if min_d == left_d:
            return float(self.rect.left - radius), y
        elif min_d == right_d:
            return float(self.rect.right + radius), y
        elif min_d == top_d:
            return x, float(self.rect.top - radius)
        else:
            return x, float(self.rect.bottom + radius)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.COLOR, self.rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, width=2)
