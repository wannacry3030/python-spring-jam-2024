# Passo 1: Configuração Inicial e Classe GameWindow

import pygame
import sys
import math
import random

# Inicialização do Pygame
pygame.init()

screen_w, screen_h = 1500, 800
screen = pygame.display.set_mode((screen_w, screen_h  ))
pygame.display.set_caption("spring game jam")


# Classe base para entidades animadas (Player, Enemy)
class AnimatedEntity:
    def __init__(self, x, y, width, height, sprite_paths, animation_time=0.1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_time = animation_time
        self.sprites = [pygame.transform.scale(pygame.image.load(path), (width, height)) for path in sprite_paths]
        self.current_sprite = 0
        self.last_update = pygame.time.get_ticks()

    def update_sprites(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time * 1000:
            self.last_update = now
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
    
    def draw(self, surface):
        surface.blit(self.sprites[self.current_sprite], (self.x, self.y))

class Projectile:
    def __init__(self, x, y, angle, speed=15, radius=5):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = radius

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

class Player(AnimatedEntity):
    def __init__(self, x, y):
        self.sprites = ['assets/flower1.png', 'assets/flower2.png']
        super().__init__(x, y, 50, 50, self.sprites)
        # Restante do código do Player

    def shoot(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        projectile = Projectile(self.x, self.y, angle)
        return projectile

# Basic Enemy Class
class Enemy(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = ['assets/enemy1.png']  # Example sprite
        super().__init__(x, y, 50, 50, sprite_paths)
        self.speed = 2

    def move_towards_player(self, player_x, player_y):
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

class GameManager:

    def __init__(self):


        self.player = Player(screen_w // 2, screen_h // 2)

        self.enemies = [Enemy(400, 300)]

        self.projectiles = []  # Lista para armazenar os projéteis ativos

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
       
    def draw(self, surface):
        super().draw(surface)



# The calls to create a game window and start the game loop will be uncommented after reviewing the code
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
