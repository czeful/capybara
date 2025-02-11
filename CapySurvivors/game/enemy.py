# game/enemy.py
import random
import pygame
from game import settings
from game.bullet import BossBullet

class BaseEnemy(pygame.sprite.Sprite):
    """
    Base class for all enemies. Handles shared logic like:
      - movement toward the player,
      - loading animations,
      - pausing,
      - taking damage.
    Subclasses override speed, health, sprite paths, or sizes.
    """
    def __init__(self, pos, target, speed, health, image_prefix, image_count=4, size=(60, 90)):
        super().__init__()
        self.animations = {"left": [], "right": []}
        self.size = size

        # Load animation frames from assets/images/<image_prefix>/left_i_c.png and right_i_c.png
        try:
            for i in range(1, image_count + 1):
                img_left = pygame.image.load(f"assets/images/{image_prefix}/left_{i}_c.png").convert_alpha()
                img_left = pygame.transform.scale(img_left, self.size)
                self.animations["left"].append(img_left)

            for i in range(1, image_count + 1):
                img_right = pygame.image.load(f"assets/images/{image_prefix}/right_{i}_c.png").convert_alpha()
                img_right = pygame.transform.scale(img_right, self.size)
                self.animations["right"].append(img_right)
        except Exception as e:
            print("Error loading enemy animations:", e)
            # Fallback: a plain placeholder
            placeholder = pygame.Surface(self.size)
            placeholder.fill((255, 0, 0))
            self.animations["left"] = [placeholder]
            self.animations["right"] = [placeholder]

        # Animation state
        self.current_direction = "right"
        self.current_frame = 0
        self.animation_timer = 0.0
        self.image = self.animations[self.current_direction][self.current_frame]

        # Position and rect
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

        # Movement toward the target (usually the player)
        self.target = target
        self.speed = speed

        # Health
        self.health = health

        # Paused flag
        self.paused = False

    def update(self, dt):
        if self.paused:
            return

        # Determine target position (using player's intended_pos if available)
        if hasattr(self.target, "intended_pos"):
            target_pos = pygame.Vector2(self.target.intended_pos)
        else:
            target_pos = pygame.Vector2(self.target.rect.center)

        direction_vector = target_pos - self.pos
        if direction_vector.length() != 0:
            direction_vector = direction_vector.normalize()

        # Move toward the target
        self.pos += direction_vector * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Choose animation direction
        self.current_direction = "left" if target_pos.x < self.pos.x else "right"

        # Update animation frame
        self.animation_timer += dt
        if self.animation_timer >= 0.2:
            frames = self.animations[self.current_direction]
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.animation_timer = 0.0
        self.image = self.animations[self.current_direction][self.current_frame]

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False

    @staticmethod
    def _spawn_position(screen_rect):
        # Randomly choose a side for the enemy to spawn from.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(screen_rect.left, screen_rect.right)
            y = screen_rect.top - 50
        elif side == "bottom":
            x = random.randint(screen_rect.left, screen_rect.right)
            y = screen_rect.bottom + 50
        elif side == "left":
            x = screen_rect.left - 50
            y = random.randint(screen_rect.top, screen_rect.bottom)
        else:
            x = screen_rect.right + 50
            y = random.randint(screen_rect.top, screen_rect.bottom)
        return (x, y)


class StandardEnemy(BaseEnemy):
    """
    Standard enemy:
      - 3 HP, normal speed,
      - uses assets/images/enemy/ for sprites.
    """
    def __init__(self, pos, target, speed=150):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=3,
            image_prefix="enemy",
            image_count=4,
            size=(60, 90)
        )

    @staticmethod
    def spawn(screen_rect, target, speed=150):
        pos = BaseEnemy._spawn_position(screen_rect)
        return StandardEnemy(pos, target, speed)


class FastEnemy(BaseEnemy):
    """
    Fast enemy:
      - 1 HP, very high speed,
      - uses assets/images/enemy_fast/ for sprites.
    """
    def __init__(self, pos, target, speed=300):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=1,
            image_prefix="enemy_fast",
            image_count=4,
            size=(50, 80)
        )

    @staticmethod
    def spawn(screen_rect, target, speed=300):
        pos = BaseEnemy._spawn_position(screen_rect)
        return FastEnemy(pos, target, speed)


class TankyEnemy(BaseEnemy):
    """
    Tanky enemy:
      - 6 HP, slower movement,
      - uses assets/images/enemy_tanky/ for sprites.
    """
    def __init__(self, pos, target, speed=50):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=6,
            image_prefix="enemy_tanky",
            image_count=4,
            size=(75, 105)
        )

    @staticmethod
    def spawn(screen_rect, target, speed=50):
        pos = BaseEnemy._spawn_position(screen_rect)
        return TankyEnemy(pos, target, speed)


class EasyBoss(BaseEnemy):
    """
    Easy Difficulty Boss:
      - 150 HP, 215 speed, 200×200 size.
      - Shoots 1 bullet every ~0.8 seconds toward the player.
      - On collision, instantly kills the player.
      - Awards 100 score upon defeat.
      - Displays an HP bar.
    """
    def __init__(self, pos, target, bullet_group, speed=215, health=150):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=health,
            image_prefix="boss_easy",
            image_count=4,
            size=(265, 200)
        )
        self.bullet_group = bullet_group
        self.shoot_timer = 0.0

    def update(self, dt):
        if self.paused:
            return

        super().update(dt)

        self.shoot_timer += dt
        if self.shoot_timer >= 0.8:
            self.shoot_timer -= 0.8
            direction = pygame.Vector2(self.target.rect.center) - self.pos
            if direction.length() != 0:
                direction = direction.normalize()
            bullet = BossBullet(self.rect.center, direction, speed=600)
            self.bullet_group.add(bullet)

    def draw_hp_bar(self, surface, camera):
        boss_rect = camera.apply(self)
        bar_width = boss_rect.width
        bar_height = 10
        health_ratio = max(self.health, 0) / 150.0
        bar_bg = pygame.Rect(boss_rect.left, boss_rect.bottom, bar_width, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), bar_bg)
        bar_fg = pygame.Rect(boss_rect.left, boss_rect.bottom, int(bar_width * health_ratio), bar_height)
        pygame.draw.rect(surface, (0, 255, 0), bar_fg)


class Summon(BaseEnemy):
    """
    Summon enemy spawned by the Hard Boss:
      - 1 HP, 200 speed, 40×40 size,
      - Uses standard movement animation (from assets/images/summon/).
      - Killing this enemy awards 5 score.
    """
    def __init__(self, pos, target, speed=200, health=1):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=health,
            image_prefix="summon",
            image_count=4,
            size=(60, 50)
        )


class HardBoss(BaseEnemy):
    """
    Hard Difficulty Boss:
      - 250 HP, 150 speed, 200×200 size.
      - Every 4 seconds, shoots 10 bullets radially (evenly distributed around its center).
      - Every 2 seconds, spawns a Summon enemy.
      - On collision, instantly kills the player.
      - Awards 200 score upon defeat.
      - Displays an HP bar.
      - Triggers sound effects.
    """
    def __init__(self, pos, target, bullet_group, enemy_group, sound_manager, speed=150, health=250):
        super().__init__(
            pos=pos,
            target=target,
            speed=speed,
            health=health,
            image_prefix="boss_hard",
            image_count=4,
            size=(265, 200)
        )
        self.bullet_group = bullet_group
        self.enemy_group = enemy_group
        self.sound_manager = sound_manager
        self.shoot_timer = 0.0
        self.summon_timer = 0.0

    def update(self, dt):
        if self.paused:
            return

        super().update(dt)

        # Every 4 seconds, shoot 10 bullets radially around the boss.
        self.shoot_timer += dt
        if self.shoot_timer >= 4.0:
            self.shoot_timer -= 4.0
            num_bullets = 10
            angle_increment = 360 / num_bullets
            for i in range(num_bullets):
                angle_deg = i * angle_increment
                direction = pygame.Vector2(1, 0).rotate(angle_deg)
                bullet = BossBullet(self.rect.center, direction, speed=600)
                self.bullet_group.add(bullet)
            self.sound_manager.play_sound("hardboss_shoot")

        # Every 2 seconds, spawn a Summon enemy near the boss.
        self.summon_timer += dt
        if self.summon_timer >= 2.0:
            self.summon_timer -= 2.0
            summon_pos = (self.pos.x + random.randint(-30, 30), self.pos.y + random.randint(-20, 20))
            summon = Summon(summon_pos, self.target, speed=250, health=1)
            self.enemy_group.add(summon)

    def draw_hp_bar(self, surface, camera):
        boss_rect = camera.apply(self)
        bar_width = boss_rect.width
        bar_height = 10
        health_ratio = max(self.health, 0) / 250.0
        bar_bg = pygame.Rect(boss_rect.left, boss_rect.bottom, bar_width, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), bar_bg)
        bar_fg = pygame.Rect(boss_rect.left, boss_rect.bottom, int(bar_width * health_ratio), bar_height)
        pygame.draw.rect(surface, (0, 255, 0), bar_fg)

