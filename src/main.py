import pygame
from time import time

from consts import SIZE

from specie import Hunter, Prey, Specie
from food import PreysFood
from obstacle import Obstacle
from stat_window import StatWindow
from population import Population

class App:
    def __init__(self, debug: bool=False) -> None:
        # GUI
        self.screen = pygame.display.set_mode([SIZE.WIDTH, SIZE.HEIGHT])
        pygame.display.set_caption("Evolution Simulator")
        self.stat_window = StatWindow()
        PreysFood.sprite_init()
        # Obstacles
        self.obstacles = Obstacle.spawn_random(SIZE.OBSTACLE_COUNT)
        Specie.obstacles = self.obstacles  # share with all species
        # Initial Population
        self.population = Population(SIZE.POPULATION, 12)
        self.generation: int = 0
        self.hunters = [Hunter(size=0.5, corner="top-left") for _ in range(SIZE.POPULATION//2)]
        self.preys = [Prey(size=0.5, corner="bottom-right") for _ in range(SIZE.POPULATION)]
        self.preys_food = self._spawn_food()

        self.clock = pygame.time.Clock()
        self.running: bool = True
        self.debug = debug

    def _spawn_food(self) -> list[PreysFood]:
        food_list: list[PreysFood] = []
        count = int(SIZE.POPULATION * 0.75)
        for _ in range(count):
            f = PreysFood()
            for _ in range(20):
                if any(o.rect.collidepoint(f.x, f.y) for o in self.obstacles):
                    f.update_position()
                else:
                    break
            food_list.append(f)
        return food_list

    def eating_collision(self) -> None:
        for hunter in self.hunters:
            hunter.hunting = False
        for prey in self.preys:
            prey.fleeing = False

        for prey in self.preys:
            if not prey.stats.alive:
                continue
            nearest_threat = None
            nearest_dist_sq = float("inf")
            for hunter in self.hunters:
                if not hunter.stats.alive:
                    continue
                if hunter.in_fov(prey):
                    hunter.hunt(prey)
                if prey.in_fov(hunter):
                    dx = hunter.x - prey.x
                    dy = hunter.y - prey.y
                    d2 = dx * dx + dy * dy
                    if d2 < nearest_dist_sq:
                        nearest_dist_sq = d2
                        nearest_threat = hunter
                if hunter.collides(prey):
                    hunter.eat(prey)
            if nearest_threat is not None and prey.stats.alive:
                prey.flee(nearest_threat)
            for ram in self.preys_food:
                if not ram.eaten and prey.collides(ram):
                    prey.eat(ram)

    def eventloop(self) -> None:
        self.eating_collision()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        for hunter in self.hunters:
            hunter.move()
        for prey in self.preys:
            prey.move()
        for food in self.preys_food:
            food.update()

    def drawloop(self) -> None:
        self.screen.fill((194, 208, 153))
        for obs in self.obstacles:
            obs.draw(self.screen)
        for food in self.preys_food:
            food.draw(self.screen)
        for prey in self.preys:
            prey.draw(self.screen, self.debug)
        for hunter in self.hunters:
            hunter.draw(self.screen, self.debug)
        self.stat_window.draw(self.screen,
            hunters_count=len(list(filter(lambda x: x.stats.alive, self.hunters))),
            preys_count=len(list(filter(lambda x: x.stats.alive, self.preys))),
            generation=self.generation,
            fps=int(self.clock.get_fps())
        )
        pygame.display.flip()

    def finish_generation(self) -> None:
        self.hunters = self.population.mutate(self.hunters, 10)
        self.preys = self.population.mutate(self.preys, 10)
        self.preys_food = self._spawn_food()
        self.population.generation += 1
        self.population.start_generation = time()
        for hunter in self.hunters:
            hunter.restart()
        for prey in self.preys:
            prey.restart()
        self.generation += 1

    def mainloop(self) -> None:
        while self.running:
            self.eventloop()
            self.drawloop()
            self.clock.tick(120)
            if time() - self.population.start_generation >= self.population.population_duration:
                self.finish_generation()

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    try:
        App(debug=False).mainloop()
    finally:
        pygame.quit()
