# game/camera.py
import pygame
from game import settings

class Camera:
    def __init__(self, level_width, level_height):
        self.level_width = level_width
        self.level_height = level_height
        self.camera_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        print(f"Camera initialized with level_width: {level_width}, level_height: {level_height}")

    def apply(self, target):
        return target.rect.move(-self.camera_rect.topleft[0], -self.camera_rect.topleft[1])

    def apply_rect(self, rect):
        return rect.move(-self.camera_rect.topleft[0], -self.camera_rect.topleft[1])

    def update(self, target):
        x = target.rect.centerx - settings.SCREEN_WIDTH // 2
        y = target.rect.centery - settings.SCREEN_HEIGHT // 2

        x = max(0, min(x, self.level_width - settings.SCREEN_WIDTH))
        y = max(0, min(y, self.level_height - settings.SCREEN_HEIGHT))
        self.camera_rect.topleft = (x, y)
