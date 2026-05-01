from specie import Specie

from typing import TypeVar

T = TypeVar("T", bound=Specie)


class Population:
    def __init__(self, max_size: int):
        self.max_size: int = max_size

    def rank(self, population: list[T]) -> list[T]:
        """Sort population best-first by fitness score."""
        return sorted(population, key=lambda s: s.fitness(), reverse=True)

    def select(self, population: list[T], keep_ratio: float = 0.5) -> list[T]:
        """Return the top `keep_ratio` fraction of the population.

        The fitness() method on each Specie already encodes:
            • Hunters  → kills (log), energy efficiency, survival, FOV utility
            • Prey     → survival time (log), food gathered, stealth, energy remaining

        Species that died early, ate nothing, or burned all their energy
        naturally sink to the bottom and get culled.
        """
        ranked = self.rank(population)
        keep = max(2, int(len(ranked) * keep_ratio))
        return ranked[:keep]
