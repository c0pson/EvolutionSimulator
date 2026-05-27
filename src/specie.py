from random import randint, gauss, random
import pygame
import time
import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from stats import Genes, Stats, PopulationSegment
from tools import resource_path
from consts import SIZE, ENERGY, AI
from sprite_sheet import AnimatedSpriteSheet

from food import PreysFood
from obstacle import Obstacle

def _angle_diff(a: float, b: float) -> float:
    d = (b - a) % 360
    return d - 360 if d > 180 else d

def _angle_to(x1, y1, x2, y2) -> float:
    dx = x2 - x1
    dy = y2 - y1
    return math.degrees(math.atan2(dx, -dy)) % 360

def _dist_sq(x1, y1, x2, y2) -> float:
    dx = x1 - x2
    dy = y1 - y2
    return dx * dx + dy * dy

class Specie(ABC):
    BASE_FOV_RANGE = 190
    obstacles: list[Obstacle] = []
    @staticmethod
    def _spawn_position(corner: str | None = None) -> tuple[float, float]:
        margin = 80
        for _ in range(50):
            if corner == "top-left":
                pos = (float(randint(margin, SIZE.WIDTH // 2 - margin)),
                       float(randint(margin, SIZE.HEIGHT // 2 - margin)))
            elif corner == "top-right":
                pos = (float(randint(SIZE.WIDTH // 2 + margin, SIZE.WIDTH - margin)),
                       float(randint(margin, SIZE.HEIGHT // 2 - margin)))
            elif corner == "bottom-left":
                pos = (float(randint(margin, SIZE.WIDTH // 2 - margin)),
                       float(randint(SIZE.HEIGHT // 2 + margin, SIZE.HEIGHT - margin)))
            elif corner == "bottom-right":
                pos = (float(randint(SIZE.WIDTH // 2 + margin, SIZE.WIDTH - margin)),
                       float(randint(SIZE.HEIGHT // 2 + margin, SIZE.HEIGHT - margin)))
            else:
                pos = (float(randint(40, SIZE.WIDTH - 40)), float(randint(40, SIZE.HEIGHT - 40)))
            if not any(o.rect.collidepoint(int(pos[0]), int(pos[1])) for o in Specie.obstacles):
                return pos
        return pos

    def __init__(
        self,
        size: float = 1.0,
        speed: float = 1.0,
        stamina: int = 10,
        fov: int = 45,
        turn_rate: float = 5.0,
        aggression: float = 0.5,
        caution: float = 0.5,
        perception: float = 1.0,
        hunger: int = 0,
        alive: bool = True,
        score: float = 0.0,
        generation: int = 0,
        age: int = 0,
        x: float | None = None,
        y: float | None = None,
        corner: str | None = None,
    ):
        self.genes = Genes(size, speed, stamina, fov, turn_rate, aggression, caution, perception)
        self.stats = Stats(hunger, alive, score, energy=stamina * ENERGY.STAMINA_TO_ENERGY.value)
        self.population_segment = PopulationSegment(generation, age)

        self.sprites: AnimatedSpriteSheet
        self.corner = corner
        if x is not None and y is not None:
            self.x: float = x
            self.y: float = y
        else:
            self.x, self.y = self._spawn_position(corner)
        self.rotation: float = randint(0, 360)

        self.desired_rotation: float = self.rotation
        self.wander_angle: float = float(randint(0, 360))
        self.hunting = False
        self.fleeing = False
        self.ticks_alive: int = 0

        scaled_size = int(32 * self.genes.size)
        self.rect = pygame.Rect(0, 0, scaled_size, scaled_size)
        self.rect.center = (int(self.x), int(self.y))
        self.fov_surface = pygame.Surface((SIZE.WIDTH, SIZE.HEIGHT), pygame.SRCALPHA)

    @property
    def fov_range(self) -> float:
        return self.BASE_FOV_RANGE * self.genes.perception

    def _energy_cost(self, activity_mult: float = 1.0) -> float:
        speed_factor = ENERGY.MOVE_COST_BASE.value * self.genes.speed
        size_penalty = self.genes.size ** ENERGY.SIZE_COST_EXP.value
        perception_cost = 1.0 + 0.05 * (self.genes.perception - 1.0)
        return (ENERGY.IDLE_COST.value + speed_factor) * size_penalty * activity_mult * perception_cost

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

    def draw(self, surface: pygame.Surface, debug: bool) -> None:
        if debug and self.stats.alive:
            self.draw_fov(surface)
        rotated_sprite = pygame.transform.rotozoom(
            self.sprites.next(), self.rotation, self.genes.size
        )
        self.rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
        self.mask = pygame.mask.from_surface(rotated_sprite)
        surface.blit(rotated_sprite, self.rect.topleft)

    def draw_fov(self, surface: pygame.Surface) -> None:
        half_fov = self.genes.fov / 2
        r = self.fov_range
        angle1 = -self.rotation - half_fov
        rad1 = math.radians(angle1 - 90)
        px1 = self.x + r * math.cos(rad1)
        py1 = self.y + r * math.sin(rad1)
        angle2 = -self.rotation - half_fov + self.genes.fov
        rad2 = math.radians(angle2 - 90)
        px2 = self.x + r * math.cos(rad2)
        py2 = self.y + r * math.sin(rad2)
        self.fov_surface.fill((0, 0, 0, 0))
        pygame.draw.polygon(
            surface, (255, 160, 170, 80),
            [(self.x, self.y), (px1, py1), (px2, py2)],
        )
        surface.blit(self.fov_surface, (0, 0))

    def in_fov(self, other: "Specie") -> bool:
        dx = other.x - self.x
        dy = other.y - self.y
        d2 = dx * dx + dy * dy
        if d2 > self.fov_range ** 2:
            return False
        angle_to = math.degrees(math.atan2(dy, dx))
        facing = -self.rotation + 90
        diff = (angle_to - facing) % 360 - 180
        return abs(diff) <= self.genes.fov / 2

    def _has_obstacle_between(self, tx: float, ty: float) -> bool:
        for obs in self.obstacles:
            if obs.rect.clipline(self.x, self.y, tx, ty):
                return True
        return False

    def _steer_toward(self, target_angle: float) -> None:
        diff = _angle_diff(self.rotation, target_angle)
        max_turn = self.genes.turn_rate
        clamped = max(-max_turn, min(max_turn, diff))
        self.desired_rotation = self.rotation + clamped

    def _wander_steer(self) -> None:
        self.wander_angle += gauss(0, AI.WANDER_JITTER.value)
        self._steer_toward(self.wander_angle)

    def _boundary_steer(self) -> float:
        m = AI.BOUNDARY_MARGIN.value
        f = AI.BOUNDARY_FORCE.value
        nudge = 0.0
        if self.x < m:
            nudge += f * (1.0 - self.x / m)
        elif self.x > SIZE.WIDTH - m:
            nudge -= f * (1.0 - (SIZE.WIDTH - self.x) / m)
        if self.y < m:
            nudge += f * (1.0 - self.y / m) * (1 if math.sin(math.radians(self.rotation)) > 0 else -1)
        elif self.y > SIZE.HEIGHT - m:
            nudge -= f * (1.0 - (SIZE.HEIGHT - self.y) / m) * (1 if math.sin(math.radians(self.rotation)) > 0 else -1)
        return nudge

    def _obstacle_steer(self) -> float:
        margin = AI.OBSTACLE_STEER_MARGIN.value
        force = AI.OBSTACLE_STEER_FORCE.value
        rad = math.radians(self.rotation)
        probe_x = self.x + math.sin(rad) * margin
        probe_y = self.y - math.cos(rad) * margin
        nudge = 0.0
        for obs in self.obstacles:
            if obs.rect.collidepoint(int(probe_x), int(probe_y)):
                cx = obs.rect.centerx
                cy = obs.rect.centery
                away_angle = _angle_to(self.x, self.y, cx, cy) + 180.0
                diff = _angle_diff(self.rotation, away_angle % 360)
                nudge += math.copysign(force, diff)
        return nudge

    def move(self) -> None:
        if not self.stats.alive:
            return
        self.ticks_alive += 1
        if not self.hunting and not self.fleeing:
            self._wander_steer()
        self.rotation = self.desired_rotation + self._boundary_steer() + self._obstacle_steer()
        effective_speed = self.genes.speed
        if self.fleeing:
            effective_speed *= 1.3
        elif self.hunting:
            effective_speed *= 1.1
        rad = math.radians(self.rotation)
        dx = math.sin(rad) * effective_speed
        dy = -math.cos(rad) * effective_speed
        new_x = self.x + dx
        new_y = self.y + dy
        if new_x < 0 or new_x > SIZE.WIDTH:
            self.rotation = -self.rotation
            new_x = max(0, min(new_x, SIZE.WIDTH))
        if new_y < 0 or new_y > SIZE.HEIGHT:
            self.rotation = 180 - self.rotation
            new_y = max(0, min(new_y, SIZE.HEIGHT))
        for obs in self.obstacles:
            if obs.rect.collidepoint(int(new_x), int(new_y)):
                new_x, new_y = obs.push_out(new_x, new_y, radius=16.0 * self.genes.size)
                away = _angle_to(self.x, self.y, obs.rect.centerx, obs.rect.centery) + 180.0
                self.rotation = away % 360
        step = math.hypot(new_x - self.x, new_y - self.y)
        self.stats.distance_moved += step
        self.x = new_x
        self.y = new_y
        scaled_size = int(32 * self.genes.size)
        self.rect = pygame.Rect(0, 0, scaled_size, scaled_size)
        self.rect.center = (int(self.x), int(self.y))
        self.drain_energy()

    def restart(self) -> None:
        self.stats.alive = True
        self.stats.energy = self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value
        self.stats.hunger = 0
        self.stats.damage_dealt = 0.0
        self.stats.food_eaten = 0
        self.stats.times_fled = 0
        self.stats.distance_moved = 0.0
        self.ticks_alive = 0
        self.x, self.y = self._spawn_position(self.corner)
        self.rotation = randint(0, 360)
        self.hunting = False
        self.fleeing = False

    @abstractmethod
    def collides(self, other) -> bool: ...

    @abstractmethod
    def eat(self, other) -> None: ...

    @abstractmethod
    def fitness(self) -> float: ...

    @classmethod
    @abstractmethod
    def from_genes(cls, genes: Genes, generation: int, corner: str | None = None) -> "Specie": ...

class Hunter(Specie):
    def __init__(self, size=0.15, speed=1.2, stamina=8, fov=30,
                 turn_rate=6.0, aggression=0.6, caution=0.4, perception=1.0,
                 hunger=0, alive=True, score=0.0,
                 generation=0, age=0, x=None, y=None, corner=None) -> None:
        super().__init__(size, speed, stamina, fov, turn_rate, aggression,
                         caution, perception, hunger, alive, score,
                         generation, age, x, y, corner)
        self.sprites = AnimatedSpriteSheet(
            resource_path("assets", "hunter_sheet.png"),
            pygame.Rect(0, 0, 32, 32),
            count=8, loop=True, frames=10,
        )
        self.mask = pygame.mask.from_surface(self.sprites.next())
        self._target: Prey | None = None

    def collides(self, prey: "Prey") -> bool:
        if not self.stats.alive:
            return False
        offset = (int(prey.rect.x - self.rect.x), int(prey.rect.y - self.rect.y))
        return self.mask.overlap(prey.mask, offset) is not None

    def eat(self, prey: "Prey") -> None:
        prey.stats.alive = False
        self.stats.hunger += 1
        self.stats.damage_dealt += prey.genes.size
        self.stats.energy = min(
            self.stats.energy + ENERGY.KILL_ENERGY.value,
            self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value,
        )

    def pick_target(self, visible_prey: list["Prey"]) -> None:
        if not visible_prey:
            self._target = None
            return
        if self._target and self._target.stats.alive and self._target in visible_prey:
            if random() < self.genes.aggression:
                return
        best = None
        best_score = -1.0
        for p in visible_prey:
            d2 = _dist_sq(self.x, self.y, p.x, p.y)
            dist = math.sqrt(d2) + 1.0
            los_penalty = 0.3 if self._has_obstacle_between(p.x, p.y) else 1.0
            score = (1.0 / dist) * (1.0 / (p.genes.size + 0.1)) * los_penalty
            if score > best_score:
                best_score = score
                best = p
        self._target = best

    def hunt(self, prey: "Prey") -> None:
        self.hunting = True
        self._target = prey
        closing_speed = self.genes.speed * 1.1
        d = math.sqrt(_dist_sq(self.x, self.y, prey.x, prey.y)) + 1.0
        ticks_to_reach = d / (closing_speed + 0.01)
        prey_rad = math.radians(prey.rotation)
        pred_x = prey.x + math.sin(prey_rad) * prey.genes.speed * min(ticks_to_reach, 30) * 0.3
        pred_y = prey.y - math.cos(prey_rad) * prey.genes.speed * min(ticks_to_reach, 30) * 0.3
        target_angle = _angle_to(self.x, self.y, pred_x, pred_y)
        self._steer_toward(target_angle)

    def should_conserve_energy(self) -> bool:
        max_e = self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value
        ratio = self.stats.energy / max_e if max_e > 0 else 0
        return ratio < (0.2 + 0.3 * self.genes.caution)

    def fitness(self) -> float:
        kill_score = math.log1p(self.stats.damage_dealt * 5.0) * 8.0
        energy_spent = max(0.01, self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value - self.stats.energy)
        efficiency = kill_score / (1.0 + energy_spent * 0.05)
        survival = math.sqrt(self.ticks_alive + 1) * 0.5
        fov_bonus = math.log1p(self.genes.fov * self.genes.perception / 20.0)
        agility = self.genes.speed / (self.genes.size ** 0.5 + 0.1)
        agility_bonus = math.log1p(agility) * 0.5
        return (efficiency + survival) * fov_bonus * (1.0 + agility_bonus)

    @classmethod
    def from_genes(cls, genes: Genes, generation: int = 0, corner: str | None = None) -> "Hunter":
        return cls(
            size=genes.size, speed=genes.speed, stamina=genes.stamina,
            fov=genes.fov, turn_rate=genes.turn_rate, aggression=genes.aggression,
            caution=genes.caution, perception=genes.perception,
            generation=generation,
            corner=corner,
        )

class Prey(Specie):
    def __init__(self, size=0.1, speed=1.0, stamina=10, fov=60,
                 turn_rate=7.0, aggression=0.3, caution=0.6, perception=1.0,
                 hunger=0, alive=True, score=0.0,
                 generation=0, age=0, x=None, y=None, corner=None) -> None:
        super().__init__(size, speed, stamina, fov, turn_rate, aggression,
                         caution, perception, hunger, alive, score,
                         generation, age, x, y, corner)
        self.sprites = AnimatedSpriteSheet(
            resource_path("assets", "prey_sheet.png"),
            pygame.Rect(0, 0, 32, 32),
            count=1, loop=True, frames=10,
        )
        self.mask = pygame.mask.from_surface(self.sprites.next())
        self._flee_jitter: float = 0.0

    def collides(self, ram: PreysFood) -> bool:
        if not self.stats.alive:
            return False
        return self.rect.colliderect(ram.rect)

    def eat(self, ram: PreysFood) -> None:
        ram.eaten = True
        self.stats.hunger += 1
        self.stats.food_eaten += 1
        self.stats.energy = min(
            self.stats.energy + ENERGY.FOOD_ENERGY.value,
            self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value,
        )

    def forage(self, food_items: list[PreysFood]) -> bool:
        best = None
        best_d2 = float("inf")
        for f in food_items:
            if f.eaten:
                continue
            d2 = _dist_sq(self.x, self.y, f.x, f.y)
            if d2 < self.fov_range ** 2 and d2 < best_d2:
                angle = math.degrees(math.atan2(f.y - self.y, f.x - self.x))
                facing = -self.rotation + 90
                diff = (angle - facing) % 360 - 180
                if abs(diff) <= self.genes.fov / 2:
                    best_d2 = d2
                    best = f
        if best is not None:
            target = _angle_to(self.x, self.y, best.x, best.y)
            self._steer_toward(target)
            return True
        return False

    def flee(self, hunter: Hunter) -> None:
        self.stats.times_fled += 1
        away = _angle_to(self.x, self.y, hunter.x, hunter.y) + 180.0
        jitter_amp = 25.0 * (1.0 - self.genes.caution * 0.5)
        self._flee_jitter = -self._flee_jitter if abs(self._flee_jitter) > 0.1 else jitter_amp
        self._flee_jitter += gauss(0, 5)
        away += self._flee_jitter
        self._steer_toward(away % 360)

    def should_flee(self, hunter: Hunter) -> bool:
        d2 = _dist_sq(self.x, self.y, hunter.x, hunter.y)
        flee_range = self.fov_range * (0.5 + 0.5 * self.genes.caution)
        return d2 < flee_range ** 2

    def school_steer(self, neighbors: list["Prey"]) -> None:
        if not neighbors:
            return
        cx, cy = 0.0, 0.0
        n = 0
        for p in neighbors:
            if p is self or not p.stats.alive:
                continue
            d2 = _dist_sq(self.x, self.y, p.x, p.y)
            if d2 < AI.PREY_SCHOOL_RADIUS.value ** 2:
                cx += p.x
                cy += p.y
                n += 1
        if n > 0:
            cx /= n
            cy /= n
            cohesion_angle = _angle_to(self.x, self.y, cx, cy)
            diff = _angle_diff(self.rotation, cohesion_angle) * AI.PREY_SCHOOL_WEIGHT.value
            self.desired_rotation += diff

    def fitness(self) -> float:
        survival = math.log1p(self.ticks_alive) * 6.0
        food_score = math.log1p(self.stats.food_eaten) * 3.0
        max_e = self.genes.stamina * ENERGY.STAMINA_TO_ENERGY.value
        energy_ratio = (self.stats.energy / max_e) if max_e > 0 else 0
        eff_bonus = 1.0 + 0.4 * energy_ratio
        stealth = 1.0 / (self.genes.size ** 0.6 + 0.05)
        agility = math.log1p(self.genes.turn_rate * self.genes.speed / 5.0) * 0.5
        percept = math.log1p(self.genes.fov * self.genes.perception / 30.0) * 0.3

        return (survival + food_score) * stealth * eff_bonus * (1.0 + agility + percept)

    @classmethod
    def from_genes(cls, genes: Genes, generation: int = 0, corner: str | None = None) -> "Prey":
        return cls(
            size=genes.size, speed=genes.speed, stamina=genes.stamina,
            fov=genes.fov, turn_rate=genes.turn_rate, aggression=genes.aggression,
            caution=genes.caution, perception=genes.perception,
            generation=generation,
            corner=corner,
        )
