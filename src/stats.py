from dataclasses import dataclass

@dataclass
class Stats:
    size: int
    speed: float
    stamina: int
    hunger: float

@dataclass
class PopulationSegment:
    birth: int
    age: int
