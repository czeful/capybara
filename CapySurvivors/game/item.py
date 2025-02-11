# game/item.py
import pygame
from game import settings

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, item_type):
        """
        pos: (x, y) position where the item spawns.
        item_type: "heal" for a healing item, "speed" for a speed boost,
                   or "freezer" for slowing zombies.
        """
        super().__init__()
        self.item_type = item_type
        self.pos = pygame.Vector2(pos)

        try:
            if item_type == "heal":
                self.image = pygame.image.load("assets/images/heal.png").convert_alpha()
            elif item_type == "speed":
                self.image = pygame.image.load("assets/images/boots.png").convert_alpha()
            elif item_type == "freezer":
                self.image = pygame.image.load("assets/images/freezer.png").convert_alpha()
            else:
                raise ValueError(f"Unknown item type: {item_type}")

            # Scale the image to a standard size.
            self.image = pygame.transform.scale(self.image, (45, 45))
        
        except Exception as e:
            print(f"Error loading {item_type} image:", e)
            # Fallback: a simple placeholder.
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            if item_type == "heal":
                color = (0, 255, 0)
            elif item_type == "speed":
                color = (0, 0, 255)
            elif item_type == "freezer":
                color = (173, 216, 230)
            else:
                color = (255, 255, 255)
            pygame.draw.circle(self.image, color, (15, 15), 15)

        self.rect = self.image.get_rect(center=pos)
    
    def update(self, dt):
        # Items remain static.
        pass
