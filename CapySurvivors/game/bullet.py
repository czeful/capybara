# game/bullet.py
import pygame
from game import settings

class Bullet(pygame.sprite.Sprite):
    """
    A bullet fired by the player.
    (Collision with walls/obstacles is handled externally in the main loop.)
    """
    def __init__(self, pos, direction, speed):
        super().__init__()
        self.speed = speed
        self.direction = pygame.Vector2(direction)
        radius = 5
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

    def update(self, dt):
        displacement = self.direction * self.speed * dt
        self.pos += displacement
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        

class BossBullet(pygame.sprite.Sprite):
    """
    A bullet fired by the boss.
    Deals 10 damage to the player upon collision.
    """
    def __init__(self, pos, direction, speed):
        super().__init__()
        self.speed = speed
        self.direction = pygame.Vector2(direction)
        radius = 7  # slightly larger than player bullet
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Draw the bullet in red
        pygame.draw.circle(self.image, (255, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

    def update(self, dt):
        displacement = self.direction * self.speed * dt
        self.pos += displacement
        self.rect.center = (round(self.pos.x), round(self.pos.y))

class LaserBullet(pygame.sprite.Sprite):
    """
    A laser bullet fired automatically by the player when the laser powerup is active.
    It is drawn as a long, red rectangle, pierces through enemies (does not self-destruct on collision),
    and disappears after a short duration.
    """
    def __init__(self, pos, direction, speed, duration=3.0):
        super().__init__()
        self.speed = speed
        self.direction = pygame.Vector2(direction).normalize()
        self.duration = duration  # lifetime in seconds
        self.is_laser = True 
        self.damaged_enemies = set()

        # Create a simple circle bullet.
        radius = 10  # adjust radius as desired
        diameter = 2 * radius
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

    def update(self, dt):
        displacement = self.direction * self.speed * dt
        self.pos += displacement
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.duration -= dt
        if self.duration <= 0:
            self