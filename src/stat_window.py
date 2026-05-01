import pygame

from tools import resource_path

class StatWindow:
    def __init__(self) -> None:
        self.rect_surface = pygame.Surface((500, 300), pygame.SRCALPHA)
        self.font = pygame.font.Font(resource_path("fonts", "Roboto-Regular.ttf"), 20)

    def draw(self, surface: pygame.Surface, hunters_count: int, preys_count: int, generation: int, fps: int) -> None:
        gen_text     = self.font.render(f"Generation: {generation}",    False, (0, 0, 0) )
        hunters_text = self.font.render(   f"Hunters: {hunters_count}", False, (0, 0, 0) )
        preys_text   = self.font.render(     f"Preys: {preys_count}",   False, (0, 0, 0) )
        fps_text     = self.font.render(       f"FPS: {fps}",           False, (0, 0, 0) )
        self.rect_surface.fill("#00000000")
        self.rect_surface.blit(gen_text,     (10,  5))
        self.rect_surface.blit(hunters_text, (10, 35))
        self.rect_surface.blit(preys_text,   (10, 65))
        self.rect_surface.blit(fps_text,     (10, 95))
        surface.blit(self.rect_surface, (0,0))

    def update(self, generation: int, hunters_alive: int, preys_alive: int) -> None:
        self.generation = generation
        self.hunters_alive = hunters_alive
        self.preys_alive = preys_alive
