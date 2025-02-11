# game/player.py
import pygame
import math
from game import settings
import random
from game.bullet import Bullet, LaserBullet

try:
    from game.bullet import Bullet
except ImportError:
    class Bullet(pygame.sprite.Sprite):
        def __init__(self, pos, direction, speed):
            super().__init__()
            self.image = pygame.Surface((5, 5))
            self.image.fill((255, 255, 0))
            self.rect = self.image.get_rect(center=pos)
            self.direction = pygame.Vector2(direction)
            self.speed = speed

        def update(self, dt):
            displacement = self.direction * self.speed * dt
            self.rect.x += displacement.x
            self.rect.y += displacement.y

class Player(pygame.sprite.Sprite):
    """
    The Player class represents the main character.
    Uses WASD for movement and shoots toward the mouse.
    Plays a walking animation and shows temporary effects.
    """
    def __init__(self, pos):
        super().__init__()
        self.animations = {"left": [], "right": []}
        try:
            for i in range(1, 5):
                image = pygame.image.load(f"assets/images/player/left_{i}.png").convert_alpha()
                image = pygame.transform.scale(image, (45, 45))
                self.animations["left"].append(image)
            for i in range(1, 5):
                image = pygame.image.load(f"assets/images/player/right_{i}.png").convert_alpha()
                image = pygame.transform.scale(image, (45, 45))
                self.animations["right"].append(image)
        except Exception as e:
            print("Error loading player animations:", e)
            placeholder = pygame.Surface((10, 10))
            placeholder.fill((0, 255, 0))
            for key in self.animations:
                self.animations[key] = [placeholder]

        self.current_direction = "right"
        self.current_frame = 0
        self.animation_timer = 0.0
        self.image = self.animations[self.current_direction][self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.intended_pos = self.pos.copy()

        self.base_speed = 300
        self.speed = self.base_speed
        self.speed_boost_timer = 0
        self.bullet_speed = 350
        self.bullet_count = 1
        self.max_hp = 50
        self.health = self.max_hp

        self.effects = []

        # New attribute: load shield image from assets.
        try:
            self.shield_image = pygame.image.load("assets/images/powerups/shield2.png").convert_alpha()
            # Optionally, scale the image (adjust the size as desired):
            self.shield_image = pygame.transform.scale(self.shield_image, (self.rect.width + 25, self.rect.height + 25))
        except Exception as e:
            print("Error loading shield image:", e)
            self.shield_image = None

        # New attributes for powerups:
        self.shield_timer = 0            # Time remaining for shield
        self.has_shotgun = False         # Whether shotgun is acquired
        self.shotgun_timer = 0           # Timer to auto-fire shotgun
        self.shotgun_bullets = []        # Bullets produced by auto-shotgun

        # Add the following for the laser powerup:
        self.has_laser = False           # Only one laser available per game.
        self.laser_timer = 0             # Counts time until next laser shot.
        self.laser_bullets = []          # Store automatically fired laser bullets.

    def update(self, dt, keys_pressed, collision_group):
        # Update temporary speed boost.
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed = self.base_speed

        # Update shield timer.
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer < 0:
                self.shield_timer = 0

        # Update shotgun timer and auto-fire if applicable.
        if self.has_shotgun:
            self.shotgun_timer += dt
            if self.shotgun_timer >= 5:
                self.shotgun_timer -= 5
                num_bullets = 8
                angle_increment = 360 / num_bullets
                for i in range(num_bullets):
                    angle_deg = i * angle_increment
                    direction = pygame.Vector2(1, 0).rotate(angle_deg)
                    bullet = Bullet(self.rect.center, direction, self.bullet_speed)
                    self.shotgun_bullets.append(bullet)
        
        
        original_pos = self.pos.copy()
        movement = pygame.Vector2(0, 0)
        if keys_pressed[pygame.K_w]:
            movement.y -= 1
        if keys_pressed[pygame.K_s]:
            movement.y += 1
        if keys_pressed[pygame.K_a]:
            movement.x -= 1
        if keys_pressed[pygame.K_d]:
            movement.x += 1
        if movement.length() > 0:
            movement = movement.normalize() * self.speed * dt

        self.intended_pos = self.pos + movement
        self.pos += movement
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if pygame.sprite.spritecollideany(self, collision_group):
            self.pos = original_pos
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        if movement.length() > 0:
            if abs(movement.x) >= abs(movement.y):
                self.current_direction = "right" if movement.x > 0 else "left"
            self.animation_timer += dt
            if self.animation_timer >= 0.11:
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_direction])
                self.animation_timer = 0.0
        else:
            self.current_frame = 0

        self.image = self.animations[self.current_direction][self.current_frame]

        new_effects = []
        for effect in self.effects:
            effect["remaining"] -= dt
            if effect["remaining"] > 0:
                new_effects.append(effect)
        self.effects = new_effects

    def shoot(self, target_pos):
        bullets = []
        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length() == 0:
            return None
        direction = direction.normalize()
        spread = 0.0873  # ~5° in radians
        if self.bullet_count == 1:
            bullet = Bullet(self.rect.center, direction, self.bullet_speed)
            bullets.append(bullet)
        else:
            count = self.bullet_count
            start_angle = -spread * (count - 1) / 2
            for i in range(count):
                angle = start_angle + i * spread
                rotated = direction.rotate_rad(angle)
                bullet = Bullet(self.rect.center, rotated, self.bullet_speed)
                bullets.append(bullet)
        return bullets

    def take_damage(self, amount):
        # If shield is active, prevent damage.
        if self.shield_timer > 0:
            return
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def apply_speed_boost(self, duration, boost_amount):
        self.speed = self.base_speed + boost_amount
        self.speed_boost_timer = duration

    def apply_boost(self, boost_type):
        if boost_type == "max_hp":
            self.max_hp += 5
            self.health += 5
        elif boost_type == "speed":
            self.base_speed += 50
            self.speed = self.base_speed
        elif boost_type == "bullet_speed":
            self.bullet_speed += 100
        elif boost_type == "bullet_count":
            self.bullet_count += 1
        elif boost_type == "shield":
            self.shield_timer = 7.0
            self.effects.append({
                "type": "shield",
                "remaining": 7.0,
                "duration": 7.0,
                "color": (173, 216, 230)
            })
        elif boost_type == "shotgun":
            if not self.has_shotgun:
                self.has_shotgun = True
                self.shotgun_timer = 0
        elif boost_type == "laser":
            if not self.has_laser:
                self.has_laser = True
                self.laser_timer = 0
        else:
            print("Unknown boost type:", boost_type)

    def add_effect(self, effect_type):
        durations = {"heal": 3.0, "speed": 3.0, "coin": 2.0}
        colors = {"heal": (0, 255, 0), "speed": (0, 0, 255), "coin": (255, 255, 0)}
        if effect_type in durations:
            self.effects.append({
                "type": effect_type,
                "remaining": durations[effect_type],
                "duration": durations[effect_type],
                "color": colors[effect_type]
            })

    def draw_effects(self, surface, camera):
        screen_rect = camera.apply(self)
        center = screen_rect.center
        # Draw the usual pulsating effects.
        for effect in self.effects:
            elapsed = effect["duration"] - effect["remaining"]
            pulsate = 2 * math.sin(2 * math.pi * 3 * elapsed)
            base_radius = max(self.rect.width, self.rect.height) // 2 + 4
            radius = base_radius + pulsate
            # Check if the effect type is not 'shield' before drawing the circle.
            if effect["type"] != "shield":
                pygame.draw.circle(surface, effect["color"], center, int(radius), width=3)

        if self.shield_timer > 0 and self.shield_image is not None:
            elapsed = self.shield_timer
            pulsate = 1.0 + 0.2 * math.sin(2 * math.pi * elapsed)  # Adjust the 0.1 factor for more/less pulsation
            shield_width = int(self.rect.width * pulsate) + 20
            shield_height = int(self.rect.height * pulsate) + 20
            scaled_shield_image = pygame.transform.scale(self.shield_image, (shield_width, shield_height))
            shield_rect = scaled_shield_image.get_rect(center=center)
            surface.blit(scaled_shield_image, shield_rect)




