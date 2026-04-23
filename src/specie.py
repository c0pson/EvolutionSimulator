from stats import Stats

from stats import Stats, PopulationSegment

class Specie:
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        self.stats = Stats(size, speed, stamina, hunger)
        self.population_segment = PopulationSegment(
            birth=generation,
            age=0
        )

class Hunter(Specie):
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        super().__init__(size, speed, stamina, hunger, generation)

class Prey(Specie):
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        super().__init__(size, speed, stamina, hunger, generation)
