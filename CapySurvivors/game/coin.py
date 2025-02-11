import pygame
from game import settings

class Coin(pygame.sprite.Sprite):
    """
    A coin that spawns on the level.
    When collected by the player, it awards +10 score.
    """
    def __init__(self, pos):
        super().__init__()
        self.pos = pygame.Vector2(pos)

        # Load the coin image from assets/images
        try:
            self.image = pygame.image.load("assets/images/coin.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))  # Scale if needed
        except Exception as e:
            print("Error loading coin image:", e)
            # Fallback in case of missing image
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (10, 10), 10)  # Gold color.

        self.rect = self.image.get_rect(center=pos)
    
    def update(self, dt):
        # Coins are static; no update needed.
        pass
