import pygame
import sys
import random
import math

# Inicialização do Pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Defesa da Flor")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  # Representando a cor da planta/flor

# Fonte
font = pygame.font.Font(None, 36)

import pygame

class ResourceManager:
    def __init__(self):
        self.sprites = {}

    def load_sprite(self, name, path):
        sprite = pygame.image.load(path).convert_alpha()  # Converte para um formato otimizado com transparência
        self.sprites[name] = sprite

    def get_sprite(self, name):
        return self.sprites.get(name)

class Flower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        # Adicione mais atributos conforme necessário (imagens, estágios de crescimento, etc.)

    def draw(self, surface):
        # Temporariamente, vamos desenhar a flor como um círculo
        pygame.draw.circle(surface, GREEN, (self.x, self.y), 30)
        # Adicione a lógica de desenho mais complexa aqui

    def shoot(self):
        # Retorna um novo projétil partindo da flor
        return Projectile(self.x, self.y, -math.pi / 2)  # Direção para cima
class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.radius = 5

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
def run_game():
    clock = pygame.time.Clock()
    flower = Flower(screen_width // 2, screen_height - 50)  # Posição inicial da flor
    projectiles = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    projectiles.append(flower.shoot())

        # Mover projéteis
        for projectile in projectiles:
            projectile.move()
            # Remover projéteis que saem da tela
            if projectile.y < 0:
                projectiles.remove(projectile)

        # Desenho
        screen.fill((0, 0, 0))  # Limpa a tela
        flower.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
