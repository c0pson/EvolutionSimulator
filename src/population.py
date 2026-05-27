from random import sample, choice
from time import time

from specie import Specie, Hunter

from typing import TypeVar

T = TypeVar("T", bound=Specie)

class Population:
    def __init__(self, max_size: int, population_duration: float):
        self.max_size: int = max_size
        self.population_duration: float = population_duration
        self.start_generation = time()
        self.generation: int = 0

        self.elite_ratio: float = 0.10
        self.tournament_size: int = 4
        self.crossover_rate: float = 0.80
        self.diversity_inject: float = 0.5

    def rank(self, population: list[T]) -> list[T]:
        return sorted(population, key=lambda s: s.fitness(), reverse=True)

    def _tournament(self, population: list[T]) -> T:
        contestants = sample(population, min(self.tournament_size, len(population)))
        return max(contestants, key=lambda s: s.fitness())

    def evolve(self, population: list[T]) -> list[T]:
        if len(population) < 2:
            return population
        ranked = self.rank(population)
        corner = ranked[0].corner if ranked else None
        if isinstance(population[0], Hunter):
            n = self.max_size // 2
        else:
            n = self.max_size
        elite_count = max(2, int(n * self.elite_ratio))
        new_pop: list[T] = ranked[:elite_count]
        crossover_slots = int(n * self.crossover_rate) - elite_count
        crossover_slots = max(0, crossover_slots)
        for _ in range(crossover_slots):
            p1 = self._tournament(ranked)
            p2 = self._tournament(ranked)
            attempts = 0
            while p2 is p1 and attempts < 5:
                p2 = self._tournament(ranked)
                attempts += 1
            child_genes = p1.genes * p2.genes
            child = type(p1).from_genes(child_genes, generation=self.generation, corner=corner)
            new_pop.append(child) # type: ignore
        diversity_count = max(1, int(n * self.diversity_inject))
        for _ in range(diversity_count):
            fresh = type(ranked[0]).from_genes(
                ranked[0].genes * choice(ranked).genes,
                generation=self.generation,
                corner=corner,
            )
            new_pop.append(fresh) # type: ignore
        while len(new_pop) < n:
            survivor = self._tournament(ranked)
            new_pop.append(survivor)
        new_pop = new_pop[:n]
        return new_pop

    def mutate(self, population: list[T], mutation_count: int = 10) -> list[T]:
        return self.evolve(population)
