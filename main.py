import pygame
import sys
import math
import random
import time

# Inicialização do Pygame
pygame.init()


# Configurações da tela

screen_width, screen_height = 1500, 750
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("teste 1")
game_over_img  = 'assets/gameover.png'
start_screen_image = 'assets/tela.png'
fundo_image = 'assets/fundo.png'
fundo_surface = pygame.image.load(fundo_image).convert_alpha()
start_screen_surface = pygame.image.load(start_screen_image)
game_over_surface = pygame.image.load(game_over_img)
fundo_surface = pygame.transform.scale(fundo_surface,(screen_width,screen_height))

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

class DamageIndicator:
    def __init__(self, x, y, damage, font, duration=1000):
        self.x = x
        self.y = y
        self.damage = damage
        self.font = font
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        # Reduz a posição y para o texto subir
        self.y -= 1

    def draw(self, screen):
        damage_text = self.font.render(str(self.damage), True, RED)
        screen.blit(damage_text, (self.x, self.y))

    def is_expired(self):
        # Verifica se a duração do indicador expirou
        return pygame.time.get_ticks() - self.creation_time > self.duration

class Player(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/flower{i}.png' for i in range(7)]
        super().__init__(x, y, 100, 100, sprite_paths)
        self.speed = 7
        self.lives = 5
        self.max_health = 200
        self.current_health =self.max_health
        self.health_bar = StatusBar(10, 10, 50, 8, (251,242,54), self.max_health)  
        self.max_mana = 20
        self.current_mana = 20
        self.mana_bar = StatusBar(x, y - 20, 50, 8, (115,122,212), self.max_mana)  # Mana
        self.mana_cost = 10
#atributos do dash ----------------------------------------------------------------------------#
        self.dash_speed = 30
        self.mana_cost_for_dash = 10
        self.dash_duration = 200 # milissegundos
        self.dash_cooldown = 3000# 10 segundos
        self.last_dash_time = 0
        self.is_dashing = False
        self.dash_start_time = 0
#atributos special shot --------------------------------------------------------------------_--#
        self.special_shot_cooldown = 3000 # miliseg
        self.last_special_shot_time = 0
        
        self.dash_icon = pygame.transform.scale(pygame.image.load('assets/icone.png').convert_alpha(), (64, 64))
        self.special_shot_icon = pygame.transform.scale(pygame.image.load('assets/icone.png').convert_alpha(), (64, 64))
                
    def start_dash(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= self.dash_cooldown:
            if self.current_mana >= self.mana_cost_for_dash:
                if not self.is_dashing:
                    self.is_dashing = True
                    self.dash_start_time = current_time
                    self.last_dash_time = current_time
                    self.current_mana -= self.mana_cost_for_dash
                    
    def draw_ability_icons(self, surface):
        icons = [self.dash_icon, self.special_shot_icon]  # Lista de ícones
        total_width = sum(icon.get_width() for icon in icons) + (len(icons) - 1) * 10  # Espaço entre ícones = 10
        start_x = (screen_width - total_width) / 2  # Centralizar no eixo X
        y = screen_height - 110  # Posição fixa no eixo Y
        
        for index, icon in enumerate(icons):
            x = start_x + index * (icon.get_width() + 10)  # Calcula a posição X para cada ícone
            surface.blit(icon, (x, y))
            
            # Para o Dash, desenha o overlay de cooldown se necessário
            if icon == self.dash_icon:
                cooldown_ratio = (pygame.time.get_ticks() - self.last_dash_time) / self.dash_cooldown
                if cooldown_ratio < 1:
                    cooldown_height = icon.get_height() * (1 - cooldown_ratio)
                    pygame.draw.rect(surface, (0, 0, 0, 127), (x, y + icon.get_height() - cooldown_height, icon.get_width(), cooldown_height))
        # Para o projétil especial, desenha o overlay de cooldown se necessário
            if icons[index] == self.special_shot_icon:
                cooldown_ratio = max(0, min((pygame.time.get_ticks() - self.last_special_shot_time) / self.special_shot_cooldown, 1))
                if cooldown_ratio < 1:
                    cooldown_height = icons[index].get_height() * (1 - cooldown_ratio)
                    pygame.draw.rect(surface, (0, 0, 0, 127), (x, y + icons[index].get_height() - cooldown_height, icons[index].get_width(), cooldown_height))


    def move(self, keys):
        current_time =  pygame.time.get_ticks()
        if self.is_dashing:
            speed = self.dash_speed
            if current_time - self.dash_start_time > self.dash_duration:
                self.is_dashing = False
        else:
            speed = self.speed
        
        if keys[pygame.K_w] and self.y > 0:
            self.y -= speed
        if keys[pygame.K_s] and self.y < screen_height - self.height:
            self.y += speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= speed
        if keys[pygame.K_d] and self.x < screen_width - self.width:
            self.x += speed
            
        self.update_health_bar_position()
        self.update_mana_bar_position()
        self.x = max(0, min(screen_width - self.width, self.x))
        self.y = max(0, min(screen_height - self.height, self.y))

    def shoot(self, target_x, target_y, is_special=False):
        current_time = pygame.time.get_ticks()
        angle = math.atan2(target_y - self.y, target_x - self.x)

        if is_special:
            # Verifica se o cooldown do tiro especial foi respeitado
            if current_time - self.last_special_shot_time >= self.special_shot_cooldown:
                if self.current_mana >= self.mana_cost:
                    self.current_mana -= self.mana_cost
                    self.last_special_shot_time = current_time  # Atualiza o tempo do último tiro especial
                    # Cria e retorna um projétil especial com rotação
                    return Projectile(self.x + self.width / 2, self.y + self.height / 2, angle, size=5, is_special=True)
        else:
            # Cria e retorna um projétil normal com rotação
            return Projectile(self.x + self.width / 2, self.y + self.height / 2, angle)
        return None  # Retorna None se o tiro especial estiver em cooldown


            
    def update_health_bar_position(self):
        self.health_bar.x = self.x + (self.width - self.health_bar.width) / 2
        self.health_bar.y = self.y + self.height + 10
    def update_mana_bar_position(self):
        self.mana_bar.x = self.x + (self.width - self.mana_bar.width) / 2
        self.mana_bar.y = self.y + self.height + 20

    def lose_life(self, damage):
        self.current_health -= damage
        self.current_health = max(0, self.current_health)  # Evita saúde negativa
        self.health_bar.update(self.current_health)  # Atualiza a barra de vida

    def is_alive(self):
        return self.lives > 0

    def draw(self, surface):
        super().draw(surface)  # Assume que AnimatedEntity tem um método draw
        self.health_bar.draw(surface)
        self.mana_bar.draw(surface)
        self.draw_ability_icons(surface) 

class AnimatedLife(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = ['assets/sol1.png', 'assets/sol2.png']  # Adicione os caminhos para suas imagens de coração aqui
        super().__init__(x, y, 50, 50, sprite_paths, animation_time=0.3)  # Ajuste animation_time para controlar a velocidade da animação

class ManaOrb(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/gota{i}.png' for i in range(6)]  # Adicione os caminhos para suas imagens de animação aqui
        super().__init__(x, y, 50, 50, sprite_paths, animation_time=0.3)  # Ajuste animation_time para controlar a velocidade da animação


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
        
    def lose_life(self,damage):
        self.lives -= damage
        
    def is_alive(self):
        return self.lives > 0

class RedEnemy(Enemy):
    def __init__(self, x, y):
        sprite_paths = [f'assets/rat{i}.png' for i in range(3)]
        super().__init__(x, y, 100, 100, sprite_paths, speed=1, damage=2)
        self.lives = 3
        self.score_value = 2

class WhiteEnemy(Enemy):
    def __init__(self, x, y):
        sprite_paths = [f'assets/enemy{i}.png' for i in range(4)]
        super().__init__(x, y, 84, 36, sprite_paths, speed=0.5, damage=1)
        self.lives = 1
        self.score_value = 1

class ShootingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, [f'assets/corvo{i}.png' for i in range(4)], speed=1, damage=1)
        self.shoot_cooldown = 2000  # Cooldown de 2000 ms (2 segundos) entre tiros
        self.last_shot_time = pygame.time.get_ticks()
        self.score_value = 2
        self.lives = 5

    def attempt_to_shoot(self, game_manager):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            # Calcula a direção do tiro em relação ao jogador
            dx = game_manager.player.x - self.x
            dy = game_manager.player.y - self.y
            angle = math.atan2(dy, dx)
            # Adiciona o projétil à lista de projéteis do jogo
            game_manager.spawn_projectile(self.x + self.width / 2, self.y + self.height / 2, angle, False, owner="enemy")

    def update(self, player_x, player_y, game_manager):
        super().move_towards_player(player_x, player_y)
        self.attempt_to_shoot(game_manager)

class Boss(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/boss{i}.png' for i in range(1, 2)]  # Adicione o caminho para os sprites do boss
        super().__init__(x, y, 150, 150, sprite_paths, 0.2)  # Tamanho e tempo de animação ajustáveis
        self.max_lives = 100
        self.lives = self.max_lives
        self.damage = 3  # Dano que o boss causa
        self.speed = 2  # Velocidade de movimento do boss
        self.attack_pattern = 0  # Padrão de ataque atual do boss 
        self.phase = 1
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        
    def move_towards_player(self, player_x, player_y):
        # Calcula a direção em direção ao jogador
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # Normaliza a direção
        dx, dy = dx / dist, dy / dist
        
        # Aplica a velocidade ao boss e move-o em direção ao jogador
        self.x += dx * self.speed
        self.y += dy * self.speed

    def perform_attack(self, game_manager):
        # Dispara projéteis em várias direções
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            for angle in range(0, 360, 45):  # Exemplo: dispara em 8 direções diferentes
                rad_angle = math.radians(angle)
                game_manager.spawn_projectile(self.x, self.y, rad_angle, is_special=True, owner="boss")
            self.last_attack_time = current_time
                
    def draw(self, surface):
        super().draw(surface)
        # Calcula a largura da barra de vida com base na vida atual do boss
        life_bar_width = (self.lives / self.max_lives) * self.width
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, life_bar_width, 5))

    def update(self, player_x, player_y, game_manager):
        self.perform_attack(game_manager)
        # Atualiza a fase do boss com base em sua vida
        if self.lives < self.max_lives / 2 and self.phase == 1:
            self.phase = 2
            # Muda para uma fase mais agressiva
            self.speed += 2
            
        
        # Move o boss em direção ao jogador
        self.move_towards_player(player_x, player_y)
        
        # Realiza um ataque periodicamente
        if pygame.time.get_ticks() % 2000 < 50:  # A cada aproximadamente 2 segundos
            self.perform_attack(game_manager)
      
class Projectile:
    # O construtor e o método move() permanecem os mesmos
    def __init__(self, x, y, angle, size=1, speed=15, radius=5, damage=1, owner ="player", is_special=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.size = size
        self.radius = radius * self.size
        self.damage = damage if size == 1 else damage * 3  # Aumenta o dano se for um projétil especial
        self.owner = owner
        
        if owner == "player" and not is_special:
            self.original_sprite = pygame.image.load("assets/semente.png").convert_alpha()
            self.original_sprite = pygame.transform.scale(self.original_sprite, (24,24))
        elif owner == "player" and is_special:
            self.original_sprite = pygame.image.load("assets/bossT.png").convert_alpha()
            self.original_sprite = pygame.transform.scale(self.original_sprite, (100,100))  # Tamanho maior para projéteis especiais
        elif owner == "enemy":
            # Sprite específico para projéteis disparados pelos inimigos comuns
            self.original_sprite = pygame.image.load("assets/semente.png").convert_alpha()
            self.original_sprite = pygame.transform.scale(self.original_sprite, (30,30))  # Ajuste o tamanho conforme necessário
        else:
            # Sprite padrão para projéteis do boss, se necessário
            self.original_sprite = pygame.image.load("assets/bossT.png").convert_alpha()
            self.original_sprite = pygame.transform.scale(self.original_sprite, (50,50))
        self.sprite = self.original_sprite
        self.angle_degrees = -math.degrees(angle) - 90

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        
    def draw(self, surface):
        # Rotaciona o sprite baseado no ângulo do tiro cada vez antes de desenhar
        self.sprite = pygame.transform.rotate(self.original_sprite, self.angle_degrees)
        rect = self.sprite.get_rect(center=(self.x, self.y))
        surface.blit(self.sprite, rect.topleft)
        
class GameManager:
    def __init__(self):
        self.reset_game()
        self.boss = None
        self.current_score = 0
        self.high_score = self.load_high_score()
        self.mana_recharge_rate = 0.03
        self.damage_indicators = []
        self.mana_orbs = []
        pygame.mouse.set_visible(False)
        self.animated_cursor = AnimatedEntity(0, 0, 60, 60, [f'assets/mira{i}.png' for i in range(1,5)], 0.5)

    


        self.font = pygame.font.Font(None, 36)
        
    def reset_game(self):
        self.game_over = False
        self.boss_defeated = False
        self.boss = None
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
        if current_time - self.last_life_spawn > 5:  # Ajuste o tempo conforme necessário
            self.lives.append(AnimatedLife(random.randint(0, screen_width - 30), random.randint(0, screen_height - 30)))
            self.last_life_spawn = current_time

    def spawn_boss(self):
        # Condição para spawnar o boss, por exemplo, alcançar um certo score
        if self.current_score > 100 and self.boss is None and not self.boss_defeated:
            self.boss = Boss(screen_width // 2, 100)  # Ajuste a posição de spawn
            
    def spawn_projectile(self, x, y, angle, is_special, owner=""):
        size = 3 if is_special else 1
        speed = 20 if is_special else 15
        radius = 10 if is_special else 5
        damage = 3 if is_special else 1 

        new_projectile = Projectile(x, y, angle, size, speed, radius, damage, owner)
        self.projectiles.append(new_projectile)
                        
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
                    self.reset_game() 
                elif event.key == pygame.K_e:
                    self.player.start_dash()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Ajusta para o centro do cursor
                adjusted_x = mouse_x - self.animated_cursor.width / 2
                adjusted_y = mouse_y - self.animated_cursor.height / 2
                if event.button == 1:  # Botão esquerdo
                    projectile = self.player.shoot(adjusted_x, adjusted_y)
                elif event.button == 3:  # Botão direito
                    projectile = self.player.shoot(adjusted_x, adjusted_y, is_special=True)
                if projectile:
                    self.projectiles.append(projectile)

                    
    def shoot(self, x, y):
        # Código para criar e adicionar um novo tiro na posição (x, y)
        pass
   
    def spawn_enemies(self):
        # O código permanece o mesmo
        if len(self.enemies) < 5 and random.randint(0, 60) == 0:
            enemy = WhiteEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
        if len(self.enemies) < 5 and random.randint(0, 120) == 0:
            enemy = RedEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
        if len(self.enemies) < 5 and random.randint(0,1000) < 5:  # Chance de 10% a cada tick
            enemy = ShootingEnemy(random.randint(0, screen_width - 60), random.randint(0, screen_height - 60))
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
        clock = pygame.time.Clock()
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
                
                # Desenha o FPS na tela
                fps = clock.get_fps()
                fps_text = font.render(f"FPS: {fps:.2f}", True, pygame.Color('white'))
                screen.blit(fps_text, (10,5))

                # Atualiza a tela
                pygame.display.flip()

                # Limita o jogo a 60 FPS
                clock.tick(60)

            
    def update(self, keys):
        # 1. Atualização do jogador
        self.player.move(keys)
        self.player.update_sprites()
        self.player.current_mana = min(self.player.current_mana + self.mana_recharge_rate, self.player.max_mana)
        self.player.mana_bar.update(self.player.current_mana)     
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.animated_cursor.x = mouse_x
        self.animated_cursor.y = mouse_y
        self.animated_cursor.update_sprites()


        # 2. Tentativa de spawnar o boss
        self.spawn_boss()

        # 3. Atualizar o boss, se ele existir
        if self.boss:
            self.boss.update(self.player.x, self.player.y, self)

        # 4. Checagem de colisão entre o jogador e o boss (aplicar dano ao jogador)
        if self.boss and pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)):
            self.player.lose_life(self.boss.damage)

        # 5. Processamento de projéteis do jogador
        for projectile in self.projectiles[:]:
            projectile.move()
            # Remove projéteis que saíram da tela
            if not (0 <= projectile.x <= screen_width and 0 <= projectile.y <= screen_height):
                self.projectiles.remove(projectile)
                continue

            # Checagem de colisão com o boss para projéteis do jogador
            if projectile.owner == "player" and self.boss:
                if pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)):
                    damage_indicator = DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font)
                    self.damage_indicators.append(damage_indicator)
                    self.boss.lives -= projectile.damage
                    self.projectiles.remove(projectile)
                    if self.boss.lives <= 0:
                        self.boss = None
                        self.boss_defeated = True

            # Checagem de colisão com o jogador para projéteis do boss
            elif projectile.owner == "boss":
                if pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                    damage_indicator = DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font)
                    self.damage_indicators.append(damage_indicator)
                    self.player.lose_life(projectile.damage)  # Aplica o dano corretamente
                    self.projectiles.remove(projectile)
            # checagem de colisao com o jogador dos projeteis do enemy       
            elif projectile.owner == "enemy"and pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                if pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                    damage_indicator = DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font)
                    self.damage_indicators.append(damage_indicator)
                    self.damage_indicators.append(damage_indicator)
                    self.player.lose_life(projectile.damage)  # Aplica o dano corretamente
                    self.projectiles.remove(projectile)
                                    
        if self.player.current_health <= 0:
            self.game_over = True
            
        for life in self.lives[:]: 
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(life.x, life.y, life.width, life.height)):
                self.player.current_health += 5  
                self.player.current_health = min(self.player.current_health, self.player.max_health)
                self.player.health_bar.update(self.player.current_health)
                self.lives.remove(life) 
                            
        for enemy in self.enemies[:]:
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                damage_indicator = DamageIndicator(enemy.x, enemy.y, enemy.damage, self.font)
                self.damage_indicators.append(damage_indicator)
                self.player.lose_life(enemy.damage)  # O jogador perde vidas com base no dano do inimigo
                self.apply_knock_back(enemy) 
                             
        for enemy in self.enemies:
            enemy.move_towards_player(self.player.x, self.player.y)  # Atualiza posição dos inimigos
        
        for orb in self.mana_orbs[:]:
            orb.update_sprites()
            
        for orb in self.mana_orbs[:]:  # Use uma cópia da lista para evitar problemas ao remover itens
            # Verifica se a distância entre os centros dos objetos é menor que a soma de seus raios
            if math.sqrt((self.player.x + self.player.width / 2 - (orb.x + orb.width / 2))**2 + (self.player.y + self.player.height / 2 - (orb.y + orb.height / 2))**2) < (self.player.width / 2 + orb.width / 2):
                # Se houver colisão
                self.mana_orbs.remove(orb)
                self.player.current_mana += 5  # Adiciona mana ao jogador
                self.player.current_mana = min(self.player.current_mana, self.player.max_mana)  # Garante que a mana não exceda o máximo
        
        for projectile in self.projectiles[:]:
            projectile.move()

            # Remove projéteis que saíram da tela
            if not (0 <= projectile.x <= screen_width and 0 <= projectile.y <= screen_height):
                self.projectiles.remove(projectile)
                continue

            # Para projéteis de inimigos, verificar colisão apenas com o jogador
            if projectile.owner == "enemy":
                if pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                    # Aplica dano ao jogador
                    self.player.lose_life(projectile.damage)
                    self.projectiles.remove(projectile)

            # Para projéteis do jogador, verificar colisão com inimigos e boss
            elif projectile.owner == "player":
                for enemy in self.enemies[:]:
                    if pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height).colliderect(pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2)):
                        # Aplica dano ao inimigo
                        enemy.lose_life(projectile.damage)
                        if not enemy.is_alive():
                            self.enemies.remove(enemy)
                        self.projectiles.remove(projectile)
                        break  # Previne múltiplas colisões com o mesmo projétil
                                    
        self.spawn_enemies()
    
    def draw(self,surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.animated_cursor.x = mouse_x - self.animated_cursor.width / 2
        self.animated_cursor.y = mouse_y - self.animated_cursor.height / 2
        screen.blit(fundo_surface, (0, 0))
        for indicator in self.damage_indicators[:]:
            indicator.update()
            indicator.draw(screen)
            if indicator.is_expired():
                self.damage_indicators.remove(indicator)  
        for projectile in self.projectiles:
            projectile.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
            enemy.update_sprites()
            
        for enemy in self.enemies:
            if isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.x, self.player.y, self)
            else:
                enemy.move_towards_player(self.player.x, self.player.y)
                    
        for life in self.lives:
            life.draw(screen)
            life.update_sprites()
        for orb in self.mana_orbs:
            screen.blit(orb.sprites[orb.current_sprite], (orb.x, orb.y))

        
        if self.boss:
            self.boss.draw(surface)
        self.player.draw(surface)
        # Desenha a pontuação atual
        
        score_text = font.render(f"Score: {self.current_score}", True, WHITE)
        surface.blit(score_text, (screen_width - 180, 10))  # Ajuste a posição conforme necessário

        # Desenha a pontuação máxima
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        surface.blit(high_score_text, (screen_width - 180, 30))  # Ajuste a posição conforme necessário

        # Desenha o cursor animado na posição atualizada antes de atualizar a tela
        self.animated_cursor.draw(surface)

        # Atualiza a tela inteira
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
