from random import randint, gauss
import pygame
import time
import math
from enum import Enum

from abc import ABC, abstractmethod

from stats import Genes, Stats, PopulationSegment
from tools import resource_path
from consts import SIZE, ENERGY

from sprite_sheet import AnimatedSpriteSheet
from food import PreysFood

class Specie(ABC):
    fov_range = 190

    def __init__(self,
        size: float = 1.0,
        speed: float = 1.0,
        stamina: int = 10,
        fov: int = 45,

        hunger: int = 0,
        alive: bool = True,
        score: float = 0.0,

        generation: int = 0,
        age: int = 0,

        x: float | None = None,
        y: float | None = None
    ):
        self.genes = Genes(size, speed, stamina, fov)
        self.stats = Stats(hunger, alive, score, energy=stamina * ENERGY.STAMINA_TO_ENERGY.value)
        self.population_segment = PopulationSegment(generation, age)

        self.sprites: AnimatedSpriteSheet
        self.x: float = x if x is not None else randint(0, SIZE.WIDTH)
        self.y: float = y if y is not None else randint(0, SIZE.HEIGHT)
        self.rotation: float = randint(0, 360)
        self.wander_time: float = time.time()

        self.hunting = False
        self.fleeing = False
        self.ticks_alive: int = 0

        scaled_size = int(32 * self.genes.size)
        self.rect = pygame.Rect(0, 0, scaled_size, scaled_size)
        self.rect.center = (int(self.x), int(self.y))
        self.fov_surface = pygame.Surface((SIZE.WIDTH, SIZE.HEIGHT), pygame.SRCALPHA)

    def _energy_cost(self, activity_mult: float = 1.0) -> float:
        speed_factor = ENERGY.MOVE_COST_BASE.value * self.genes.speed
        return (ENERGY.IDLE_COST.value + speed_factor) * (self.genes.size ** ENERGY.SIZE_COST_EXP.value) * activity_mult

    def drain_energy(self) -> None:
        if not self.stats.alive:
            return
        if self.hunting:
            mult = ENERGY.HUNT_COST_MULT.value
        elif self.fleeing:
            mult = ENERGY.FLEE_COST_MULT.value
        else:
            mult = 1.0
        self.stats.energy -= self._energy_cost(mult)
        if self.stats.energy <= 0:
            self.stats.energy = 0
            self.stats.alive = False

    def draw(self, surface: pygame.Surface, debug) -> None:
        if debug and self.stats.alive:
            self.draw_fov(surface)
        rotated_sprite = pygame.transform.rotozoom(
            self.sprites.next(),
            self.rotation,
            self.genes.size
        )
        self.rect = rotated_sprite.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(rotated_sprite)
        surface.blit(rotated_sprite, self.rect.topleft)

    def draw_fov(self, surface) -> None:
        half_fov = self.genes.fov / 2
        angle = -self.rotation - half_fov
        angle_rad = math.radians(angle - 90)
        px1 = self.x + self.fov_range * math.cos(angle_rad)
        py1 = self.y + self.fov_range * math.sin(angle_rad)
        angle = -self.rotation - half_fov + self.genes.fov
        angle_rad = math.radians(angle - 90)
        px2 = self.x + self.fov_range * math.cos(angle_rad)
        py2 = self.y + self.fov_range * math.sin(angle_rad)
        self.fov_surface.fill((0, 0, 0, 0))
        pygame.draw.polygon(
            surface, (255, 160, 170, 80),
            [(self.x, self.y), (px1, py1), (px2, py2)]
        )
        surface.blit(self.fov_surface, (0, 0))

    def in_fov(self, other: "Specie") -> bool:
        dx = other.x - self.x
        dy = other.y - self.y
        dist_sq = dx * dx + dy * dy
        if dist_sq > self.fov_range * self.fov_range:
            return False
        angle_to_other = math.degrees(math.atan2(dy, dx))
        facing_angle = -self.rotation + 90
        diff = (angle_to_other - facing_angle) % 360 - 180
        half_fov = self.genes.fov / 2
        return abs(diff) <= half_fov

    @abstractmethod
    def collides(self, other) -> bool: ...

    def move(self) -> None:
        if not self.stats.alive:
            return
        self.ticks_alive += 1
        if not self.hunting and not self.fleeing:
            if time.time() - self.wander_time > 0.1:
                self.rotation += gauss(0, 4)
                self.wander_time = time.time()
        effective_speed = self.genes.speed
        if self.fleeing:
            effective_speed *= 1.3
        new_x = self.x + math.sin(math.radians(self.rotation - 180)) * effective_speed
        new_y = self.y + math.cos(math.radians(self.rotation - 180)) * effective_speed
        if new_x < 0 or new_x > SIZE.WIDTH:
            self.rotation = -self.rotation
        if new_y < 0 or new_y > SIZE.HEIGHT:
            self.rotation = 180 - self.rotation
        self.x = max(0, min(new_x, SIZE.WIDTH))
        self.y = max(0, min(new_y, SIZE.HEIGHT))
        scaled_size = int(32 * self.genes.size)
        self.rect = pygame.Rect(0, 0, scaled_size, scaled_size)
        self.rect.center = (int(self.x), int(self.y))
        self.drain_energy()

    @abstractmethod
    def eat(self, other) -> None: ...

    @abstractmethod
    def fitness(self) -> float: ...

class Hunter(Specie):
    def __init__(self,
        size: float = 1.0,
        speed: float = 1.0,
        stamina: int = 10,
        fov: int = 60,

        hunger: int = 0,
        alive: bool = True,
        score: float = 0.0,

        generation: int = 0,
        age: int = 0,

        x: float | None = None,
        y: float | None = None
    ):
        super().__init__(size, speed, stamina, fov, hunger, alive, score, generation, age, x, y)
        self.sprites = AnimatedSpriteSheet(
            resource_path("assets", "hunter_sheet.png"),
            pygame.Rect(0, 0, 32, 32),
            count=8, loop=True, frames=10
        )
        self.mask = pygame.mask.from_surface(self.sprites.next())

    def collides(self, prey: "Prey"):
        if not self.stats.alive:
            return False
        offset = (int(prey.rect.x - self.rect.x),
                  int(prey.rect.y - self.rect.y))
        return self.mask.overlap(prey.mask, offset) is not None

    def eat(self, prey: "Prey") -> None:
        prey.stats.alive = False
        self.stats.hunger += 1
        self.stats.energy = min(
            self.stats.energy + ENERGY.KILL_ENERGY,
            self.genes.stamina * ENERGY.STAMINA_TO_ENERGY
        )

    def hunt(self, prey: "Prey") -> None:
        self.hunting = True
        dx = prey.x - self.x
        dy = prey.y - self.y
        angle = -math.atan2(dx, dy)
        self.rotation = 180 - math.degrees(angle)

    def fitness(self) -> float:
        hunger_score = math.log1p(self.stats.hunger) * 10.0

        total_energy_spent = (self.genes.stamina * ENERGY.STAMINA_TO_ENERGY
                              - self.stats.energy)
        efficiency = hunger_score / (1.0 + total_energy_spent * 0.1)

        survival = math.sqrt(self.ticks_alive + 1)
        fov_bonus = math.log1p(self.genes.fov / 30.0)

        return efficiency * survival * fov_bonus

class Prey(Specie):
    def __init__(self,
        size: float = 1.0,
        speed: float = 1.0,
        stamina: int = 10,
        fov: int = 45,

        hunger: int = 0,
        alive: bool = True,
        score: float = 0.0,

        generation: int = 0,
        age: int = 0,

        x: float | None = None,
        y: float | None = None
    ):
        super().__init__(size, speed, stamina, fov, hunger, alive, score, generation, age, x, y)
        self.sprites = AnimatedSpriteSheet(
            resource_path("assets", "prey_sheet.png"),
            pygame.Rect(0, 0, 32, 32),
            count=1, loop=True, frames=10
        )
        self.mask = pygame.mask.from_surface(self.sprites.next())

    def collides(self, ram: PreysFood):
        if not self.stats.alive:
            return False
        return self.rect.colliderect(ram.rect)

    def eat(self, ram: PreysFood) -> None:
        ram.eaten = True
        self.stats.hunger += 1
        self.stats.energy = min(
            self.stats.energy + ENERGY.FOOD_ENERGY,
            self.genes.stamina * ENERGY.STAMINA_TO_ENERGY
        )

    def flee(self, hunter: "Hunter") -> None:
        self.fleeing = True
        dx = hunter.x - self.x
        dy = hunter.y - self.y
        away_angle = -math.atan2(dx, dy)
        self.rotation = math.degrees(away_angle)

    def fitness(self) -> float:
        survival = math.log1p(self.ticks_alive) * 5.0
        hunger_score = math.log1p(self.stats.hunger) * 3.0
        stealth = 1.0 / (self.genes.size ** 0.8)
        max_energy = self.genes.stamina * ENERGY.STAMINA_TO_ENERGY
        energy_ratio = (self.stats.energy / max_energy) if max_energy > 0 else 0
        eff_bonus = 1.0 + 0.5 * (2.0 / (1.0 + math.exp(-5.0 * energy_ratio)) - 1.0)
        return (survival + hunger_score) * stealth * eff_bonus
