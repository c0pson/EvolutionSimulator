from __future__ import annotations
from dataclasses import dataclass
from random import uniform, choice, gauss, random

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))

@dataclass
class Genes:
    size: float
    speed: float
    stamina: int
    fov: int

    turn_rate: float = 5.0
    aggression: float = 0.5
    caution: float = 0.5
    perception: float = 1.0

    def __mul__(self, other: Genes) -> Genes:
        def _blend_f(a: float, b: float, sigma: float) -> float:
            if random() < 0.7:
                t = uniform(0.3, 0.7)
                base = a * t + b * (1 - t)
            else:
                base = choice([a, b])
            return base + gauss(0, sigma)

        def _blend_i(a: int, b: int, sigma: float) -> int:
            return int(round(_blend_f(float(a), float(b), sigma)))

        return Genes(
            size       = _clamp(_blend_f(self.size,       other.size,       0.03), 0.05, 0.6),
            speed      = _clamp(_blend_f(self.speed,      other.speed,      0.15), 0.3,  4.0),
            stamina    = max(1, _blend_i(self.stamina,    other.stamina,    1.0)),
            fov        = max(10, min(180, _blend_i(self.fov, other.fov, 3.0))),
            turn_rate  = _clamp(_blend_f(self.turn_rate,  other.turn_rate,  0.8),  1.0, 20.0),
            aggression = _clamp(_blend_f(self.aggression, other.aggression, 0.06), 0.0, 1.0),
            caution    = _clamp(_blend_f(self.caution,    other.caution,    0.06), 0.0, 1.0),
            perception = _clamp(_blend_f(self.perception, other.perception, 0.08), 0.5, 2.0),
        )

@dataclass
class Stats:
    hunger: int
    alive: bool
    score: float
    energy: float = 0.0
    damage_dealt: float = 0.0
    food_eaten: int = 0
    times_fled: int = 0
    distance_moved: float = 0.0 

@dataclass
class PopulationSegment:
    birth: int
    age: int
