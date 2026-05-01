from dataclasses import dataclass

@dataclass
class Genes:
    size: float
    speed: float
    stamina: int
    fov: int

@dataclass
class Stats:
    hunger: int
    alive: bool
    score: float
    energy: float = 0.0

@dataclass
class PopulationSegment:
    birth: int
    age: int
