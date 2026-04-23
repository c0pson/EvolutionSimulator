from dataclasses import dataclass

from stats import Stats, PopulationSegment

@dataclass
class History:
    hunters_amount: int
    preys_amount: int
    hunters: list[tuple[Stats, PopulationSegment]]
    preys: list[tuple[Stats, PopulationSegment]]
