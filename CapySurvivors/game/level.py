# game/level.py
import pygame
from game import settings

# Define extra colors for tiles.
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, tile_type, tile_size):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        if tile_type == "wall":
            self.image.fill(DARK_GRAY)
        elif tile_type == "floor":
            self.image.fill(WHITE)
            self.image.set_alpha(256)
        elif tile_type == "obstacle":
            self.image = pygame.image.load("assets/images/bochka.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        else:
            self.image.fill((0, 0, 0))  # Default color.
        self.rect = self.image.get_rect(topleft=pos)

class Level:
    def __init__(self, filename, tile_size=50):
        self.tile_size = tile_size
        self.tiles = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.player_start = None
        self.background = None
        self.load_level(filename)
        self.load_background()

    def load_level(self, filename):
        with open(filename, "r") as f:
            data = f.readlines()
        self.level_data = [line.strip() for line in data if line.strip()]
        self.height = len(self.level_data) * self.tile_size
        self.width = max(len(line) for line in self.level_data) * self.tile_size

        for row_idx, row in enumerate(self.level_data):
            for col_idx, cell in enumerate(row):
                pos = (col_idx * self.tile_size, row_idx * self.tile_size)
                if cell == "#":
                    tile = Tile(pos, "wall", self.tile_size)
                    self.tiles.add(tile)
                    self.walls.add(tile)
                elif cell == ".":
                    tile = Tile(pos, "floor", self.tile_size)
                    self.tiles.add(tile)
                elif cell == "O":
                    tile = Tile(pos, "obstacle", self.tile_size)
                    self.tiles.add(tile)
                    self.walls.add(tile)
                elif cell == "P":
                    tile = Tile(pos, "floor", self.tile_size)
                    self.tiles.add(tile)
                    self.player_start = (pos[0] + self.tile_size // 2, pos[1] + self.tile_size // 2)
                else:
                    tile = Tile(pos, "floor", self.tile_size)
                    self.tiles.add(tile)

    def load_background(self):
        try:
            bg = pygame.image.load("assets/images/bg3.png").convert()
            self.background = pygame.transform.scale(bg, (self.width, self.height))
            print("Background loaded successfully:", self.background)
        except Exception as e:
            print("Error loading background image:", e)
            self.background = None

    def draw(self, surface, camera):
        if self.background:
            bg_rect = pygame.Rect(0, 0, self.width, self.height)
            surface.blit(self.background, camera.apply_rect(bg_rect))
        for tile in self.tiles:
            surface.blit(tile.image, camera.apply_rect(tile.rect))

