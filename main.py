import pygame
import sys
import math
import random
import time

# Inicialização do Pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 1500, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("teste 1")
game_over_img  = 'assets/gameover.png'
start_screen_image = 'assets/tela.png'
fundo_image = 'assets/fundo.png'
fundo_surface = pygame.image.load(fundo_image).convert_alpha()
start_screen_surface = pygame.image.load(start_screen_image)
game_over_surface = pygame.image.load(game_over_img)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)  # Cor para a vida extra

# Fonte
font = pygame.font.Font(None, 36)
#essa classe é para padronizar e facilitar a criação de  novos sprites para inimigos, é só passar o argumento dela e definir o caminho do sprite etc..
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

class StatusBar:
    def __init__(self, x, y, width, height, color, max_value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.max_value = max_value
        self.current_value = max_value

    def update(self, current_value):
        """Atualiza o valor atual da barra de status."""
        self.current_value = max(0, min(self.max_value, current_value))

    def draw(self, surface):
        """Desenha a barra de status na tela."""
        fill_width = (self.current_value / self.max_value) * self.width
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.color, (self.x, self.y, fill_width, self.height))

    def update_mana(self, current_mana, max_mana):
        """Atualiza a barra de mana."""
        self.update(current_mana)

    def draw_mana(self, surface):
        """Desenha a barra de mana."""
        fill_width = (self.current_value / self.max_value) * self.width
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (0, 0, 255), (self.x, self.y, fill_width, self.height))


class Player(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/flower{i}.png' for i in range(1, 3)]
        super().__init__(x, y, 50, 50, sprite_paths)  # Ajuste a largura, altura e sprite_paths conforme necessário
        self.speed = 8
        self.lives = 5
        self.max_health = 5
        self.current_health =self.max_health
        self.health_bar = StatusBar(10, 10, 50, 8, (212, 115, 115), self.max_health)  
        self.max_mana = 20
        self.current_mana = 20
        self.mana_bar = StatusBar(x, y - 20, 50, 8, (115,122,212), self.max_mana)  # Mana
            

    def move(self, keys):
        # Mover o jogador e garantir que ele não saia da tela
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < screen_height - self.height:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < screen_width - self.width:
            self.x += self.speed
        self.update_health_bar_position()
        self.update_mana_bar_position()
            
    def update_health_bar_position(self):
        self.health_bar.x = self.x
        self.health_bar.y = self.y + 60
    def update_mana_bar_position(self):
        self.mana_bar.x = self.x
        self.mana_bar.y = self.y + 70

    def lose_life(self, damage=1):
        self.current_health -= damage
        self.current_health = max(0, self.current_health)  # Evita saúde negativa
        self.health_bar.update(self.current_health)  # Atualiza a barra de vida

    def is_alive(self):
        return self.lives > 0

    def draw(self, surface):
        super().draw(surface)  # Assume que AnimatedEntity tem um método draw
        self.health_bar.draw(surface)
        self.mana_bar.draw(surface)
                
class Life:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(0, screen_width - self.width)
        self.y = random.randint(0, screen_height - self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, PINK, (self.x, self.y, self.width, self.height))

class Enemy(AnimatedEntity):
    def __init__(self, x, y, width, height, sprite_paths, speed, damage):
        super().__init__(x, y, width, height, sprite_paths)
        self.speed = speed
        self.lives = 3
        self.damage = damage

        
    def move_towards_player(self, player_x, player_y):
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
    def draw(self, surface):
        surface.blit(self.sprites[self.current_sprite], (self.x, self.y))
    def lose_life(self):
        self.lives -= 1
    def is_alive(self):
        return self.lives > 0

class RedEnemy(Enemy):
    def __init__(self, x, y):
        sprite_paths = [f'assets/enemy{i}.png' for i in range(1)]
        super().__init__(x, y, 100, 100, sprite_paths, speed=3, damage=2)

        self.score_value = 2

class WhiteEnemy(Enemy):
    def __init__(self, x, y):
        sprite_paths = [f'assets/enemy{i}.png' for i in range(1)]
        super().__init__(x, y, 60, 60, sprite_paths, speed=2, damage=1)
        self.lives = 1
        self.score_value = 1

        
class Projectile:
    # O construtor e o método move() permanecem os mesmos
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 15
        self.angle = angle
        self.radius = 10

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

class GameManager:
    def __init__(self):
        self.reset_game()
        self.current_score = 0
        self.high_score = self.load_high_score()
        
    def reset_game(self):
        self.game_over = False
        self.current_score = 0
        self.player = Player(screen_width // 2, screen_height // 2)
        self.enemies = []
        self.projectiles = []
        self.lives = []
        self.last_life_spawn = time.time()
            
    def update_high_score(self):
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()

    def save_high_score(self):
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except IOError as e:
            print(f"Erro ao salvar o high score: {e}")

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def spawn_lives(self):
        current_time = time.time()
        if current_time - self.last_life_spawn > 5:
          self.lives.append(Life())
          self.last_life_spawn = current_time    
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.reset_game()  # Reinicia o jogo.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(mouse_y - self.player.y, mouse_x - self.player.x)
                projectile = Projectile(self.player.x + self.player.width / 2, self.player.y + self.player.height / 2, angle)
                self.projectiles.append(projectile)
   
    def spawn_enemies(self):
        # O código permanece o mesmo
        if len(self.enemies) < 5 and random.randint(0, 60) == 0:
            enemy = WhiteEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
        if len(self.enemies) < 5 and random.randint(0, 120) == 0:
            enemy = RedEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
            
    def apply_knock_back(self, enemy, intensity=70):
        # Calcular a direção do knock back
        dx = enemy.x - self.player.x
        dy = enemy.y - self.player.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        # Evitar divisão por zero
        if dist == 0: dist = 1
        
        # Calcular o novo x e y baseado na intensidade do knock back
        new_x = enemy.x + (dx / dist) * intensity
        new_y = enemy.y + (dy / dist) * intensity
        
        # Assegurar que o inimigo não saia da tela
        enemy.x = max(0, min(screen_width - enemy.width, new_x))
        enemy.y = max(0, min(screen_height - enemy.height, new_y))
        
    def run(self):
        draw_start_screen()  # Mostra a tela de início
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting_for_input = False
        while True:
            if self.game_over:
                self.show_game_over_screen()
            else:
                keys = pygame.key.get_pressed()
                self.handle_events()
                self.spawn_lives()
                self.update(keys)
                self.draw(screen)
            pygame.time.Clock().tick(60)
            
    def update(self, keys):
        self.player.move(keys)
        self.player.update_sprites()
        
        # if not self.player.is_alive():
        #     self.game_over = True
        #     return
        if self.player.current_health <= 0:
            self.game_over = True
            
        for life in self.lives[:]:
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(life.x, life.y, life.width, life.height)):
                self.player.current_health += 1  # Aumenta a saúde do jogador
                self.player.current_health = min(self.player.current_health, self.player.max_health)  # Não permite que a saúde exceda o máximo
                self.player.health_bar.update(self.player.current_health)  # Atualiza a barra de saúde
                self.lives.remove(life)
                    
        for enemy in self.enemies[:]:
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                self.player.lose_life(enemy.damage)  # O jogador perde vidas com base no dano do inimigo
                self.apply_knock_back(enemy) 
                             
        for enemy in self.enemies:
            enemy.move_towards_player(self.player.x, self.player.y)  # Atualiza posição dos inimigos

        for projectile in self.projectiles[:]:
            projectile.move()
            if not (0 <= projectile.x <= screen_width and 0 <= projectile.y <= screen_height):
                self.projectiles.remove(projectile)
            else:
                for enemy in self.enemies[:]:
                    if pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height).colliderect(pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2)):
                        enemy.lose_life()  # O inimigo perde uma vida
                        if not enemy.is_alive():  # Se o inimigo não estiver mais vivo, remova-o
                            self.current_score += enemy.score_value
                            self.enemies.remove(enemy)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)

        self.spawn_enemies()
    
    def draw(self,surface):
        screen.blit(fundo_surface, (0, 0))
        for projectile in self.projectiles:
            projectile.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for life in self.lives:
            life.draw(screen)
        self.player.draw(surface)
        # Desenha a pontuação atual
        score_text = font.render(f"Score: {self.current_score}", True, WHITE)
        surface.blit(score_text, (screen_width - 180, 10))  # Ajuste a posição conforme necessário
        
        # Desenha a pontuação máxima
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        surface.blit(high_score_text, (screen_width - 180, 30))  # Ajuste a posição conforme necessário
        pygame.display.flip()    
        
    def show_game_over_screen(self):
        screen.blit(game_over_surface, (0, 0))  # Ajuste a posição conforme necessário
        pygame.display.flip()
        self.update_high_score()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                        return  # Retorna ao jogo
            
def draw_start_screen():
    screen.blit(start_screen_surface, (0, 0))  # Desenha a imagem na tela inteira
    pygame.display.flip()

    
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
