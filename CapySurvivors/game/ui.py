# game/ui.py
import pygame
from game import settings

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
    
    def draw_status(self, surface, player, score):
        # Draw health and score on the top-left.
        health_text = self.font.render("Health: " + str(player.health), True, settings.BLACK)
        score_text = self.font.render("Score: " + str(score), True, settings.BLACK)
        surface.blit(health_text, (10, 10))
        surface.blit(score_text, (10, 50))
        
        # Draw player's movement speed and bullet speed on the bottom-right.
        speed_text = "Movement Speed: " + str(player.speed)
        bullet_text = "Bullet Speed: " + str(player.bullet_speed)
        speed_render = self.font.render(speed_text, True, settings.BLACK)
        bullet_render = self.font.render(bullet_text, True, settings.BLACK)
        speed_rect = speed_render.get_rect(bottomright=(settings.SCREEN_WIDTH - 10, settings.SCREEN_HEIGHT - 40))
        bullet_rect = bullet_render.get_rect(bottomright=(settings.SCREEN_WIDTH - 10, settings.SCREEN_HEIGHT - 10))
        surface.blit(speed_render, speed_rect)
        surface.blit(bullet_render, bullet_rect)
        
        # Draw the goal at the top–right.
        goal_text = "Goal: 1500"
        goal_render = self.font.render(goal_text, True, settings.BLACK)
        goal_rect = goal_render.get_rect(topright=(settings.SCREEN_WIDTH - 10, 10))
        surface.blit(goal_render, goal_rect)
    
    def draw_message(self, surface, text, color=settings.RED):
        message = self.large_font.render(text, True, color)
        rect = message.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        surface.blit(message, rect)
