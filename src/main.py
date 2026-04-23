import pygame

from consts import SIZE

class App:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(
            (SIZE.WIDTH, SIZE.HEIGHT)
        )
        pygame.display.set_caption("Evolution Simulator")
        self.clock = pygame.time.Clock()
        self.running: bool = True

    def eventloop(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def drawloop(self) -> None:
        self.screen.fill((194, 208, 153)) # #C2D099
        pygame.display.flip()

    def mainloop(self) -> None:
        while self.running:
            self.eventloop()
            self.drawloop()

if __name__ == "__main__":
    pygame.init()
    try:
        App().mainloop()
    finally:
        pygame.quit()
