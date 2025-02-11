# game/obstacle.py
import pygame
from game import settings

class Obstacle(pygame.sprite.Sprite):
    """
    An obstacle that prevents player movement.
    (Enemies will ignore obstacles.)
    """
    def __init__(self, pos, size=(50, 50)):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/images/bochka.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, size)
        except Exception as e:
            self.image = pygame.Surface(size)
            self.image.fill((139, 69, 19))  # Brown color.
        self.rect = self.image.get_rect(topleft=pos)
