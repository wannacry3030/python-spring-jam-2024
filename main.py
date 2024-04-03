import pygame
import sys
import math
import random
import time

pygame.init()
pygame.mixer.init()
screen_width, screen_height = 1500, 750
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("teste 1")
game_over_img  = 'assets/gameover.png'
start_screen_image = 'assets/tela.png'
end_screen_image = pygame.image.load('assets/grats.png').convert_alpha()


# fundo_surface = pygame.image.load(fundo_image).convert_alpha()
fundo_aurora_surface = pygame.transform.scale(end_screen_image,(screen_width, screen_height))
start_screen_surface = pygame.image.load(start_screen_image)
game_over_surface = pygame.image.load(game_over_img)
# fundo_surface = pygame.transform.scale(fundo_surface,(screen_width,screen_height))
# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
# Fonte
font = pygame.font.Font(None, 36)

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
        self.max_health = 70
        self.current_health =self.max_health
        self.health_bar = StatusBar(10, 10, 50, 8, (251,242,54), self.max_health)  
        self.max_mana = 50
        self.current_mana = 20
        self.mana_bar = StatusBar(x, y - 20, 50, 8, (115,122,212), self.max_mana)  # Mana
        self.mana_cost = 10
#atributos do dash ----------------------------------------------------------------------------#
        self.dash_speed = 30
        self.mana_cost_for_dash = 25
        self.dash_duration = 200 # milissegundos
        self.dash_cooldown = 2000# 10 segundos
        self.last_dash_time = 0
        self.is_dashing = False
        self.dash_start_time = 0
#atributos special shot --------------------------------------------------------------------_--#
        self.special_shot_cooldown = 2000 # miliseg
        self.last_special_shot_time = 0

        self.dash_icon = pygame.transform.scale(pygame.image.load('assets/sprint.png').convert_alpha(), (64, 64))
        self.special_shot_icon = pygame.transform.scale(pygame.image.load('assets/leafsuper.png').convert_alpha(), (64, 64))
               
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
        icons = [self.dash_icon, self.special_shot_icon]  
        cooldowns = [(self.last_dash_time, self.dash_cooldown),
                    (self.last_special_shot_time, self.special_shot_cooldown),]


        total_width = sum(icon.get_width() for icon in icons) + (len(icons) - 1) * 10  # Espaço entre ícones = 10
        start_x = (screen_width - total_width) / 2  # Centralizar no eixo X
        y = screen_height - 110  # Posição fixa no eixo Y

        for index, icon in enumerate(icons):
            x = start_x + index * (icon.get_width() + 10)  # Calcula a posição X para cada ícone
            surface.blit(icon, (x, y))

            # Calcula a razão de cooldown
            current_time = pygame.time.get_ticks()
            last_use_time, cooldown_time = cooldowns[index]
            cooldown_ratio = min(max(current_time - last_use_time, 0) / cooldown_time, 1)
            
            if cooldown_ratio < 1:
                cooldown_height = icon.get_height() * (1 - cooldown_ratio)
                pygame.draw.rect(surface, (0, 0, 0, 127), (x, y + icon.get_height() - cooldown_height, icon.get_width(), cooldown_height))

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
                    return Projectile(self.x + self.width / 2, self.y + self.height / 2, angle, size=5, is_special=True, damage=3)
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
        return self.current_health > 0

    def draw(self, surface):
        super().draw(surface)  # Assume que AnimatedEntity tem um método draw
        self.health_bar.draw(surface)
        self.mana_bar.draw(surface)
        self.draw_ability_icons(surface) 

class AnimatedLife(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/sun{i}.png' for i in range(6)]
        super().__init__(x, y, 64, 64, sprite_paths, animation_time=0.1)
class ManaOrb(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/gota{i}.png' for i in range(6)]
        super().__init__(x, y, 50, 50, sprite_paths, animation_time=0.1)

class Enemy(AnimatedEntity):
    def __init__(self, x, y, width, height, sprite_paths, speed, damage):
        super().__init__(x, y, width, height, sprite_paths)
        self.original_speed = speed
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
        super().__init__(x, y, 100, 100, sprite_paths, speed=1.5, damage=4.5)
        self.lives = 3
        self.score_value = 3

class WhiteEnemy(Enemy):
    def __init__(self, x, y):
        sprite_paths = [f'assets/enemy{i}.png' for i in range(4)]
        super().__init__(x, y, 84, 36, sprite_paths, speed=0.5, damage=3)
        self.lives = 1
        self.score_value = 2

class ShootingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, [f'assets/corvo{i}.png' for i in range(4)], speed=1, damage=4)
        self.shoot_cooldown = 2000  # Cooldown de 2000 ms (2 segundos)
        self.last_shot_time = pygame.time.get_ticks()
        self.score_value = 4
        self.lives = 4

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
        super().__init__(x, y, 150, 150,[f'assets/bee{i}.png' for i in range(4)], 0.2)  
        self.max_lives =  300
        self.lives = self.max_lives
        self.damage = 0.001  
        self.speed = 1
        self.attack_pattern = 0
        self.phase = 1
        self.attack_cooldown = 3500
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
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            for angle in range(0, 360, 45):
                rad_angle = math.radians(angle)
                game_manager.spawn_projectile(self.x, self.y, rad_angle, is_special=True, owner="boss", speed=2)
            self.last_attack_time = current_time
                
    def draw(self, surface):
        super().draw(surface)
        self.update_sprites()
        # Calcula a largura da barra de vida com base na vida atual do boss
        life_bar_width = (self.lives / self.max_lives) * self.width
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, life_bar_width, 5))

    def update(self, player_x, player_y, game_manager):
        self.perform_attack(game_manager)
        # Atualiza a fase do boss com base em sua vida
        if self.lives <= 150 and self.phase == 1:
            self.phase = 2
            self.speed += 1.5
            self.attack_cooldown = 2500
            
        self.move_towards_player(player_x, player_y)
        
        # Realiza um ataque periodicamente
        if pygame.time.get_ticks() % 2000 < 50:  # A cada aproximadamente 2 segundos
            self.perform_attack(game_manager)
 
class NightBoss(AnimatedEntity):
    def __init__(self, x, y):
        super().__init__(x, y, 150, 150, [f'assets/coruja{i}.png' for i in range(4)], animation_time=0.2)
        self.max_lives = 300
        self.lives = self.max_lives
        self.speed = 3
        self.last_direction_change = pygame.time.get_ticks()
        self.direction_change_interval = 500  # Muda de direção a cada 2 segundos
        self.dx, self.dy = self.random_direction()
        self.attack_interval = 1700  # Ataca a cada 1 segundo
        self.last_attack_time = pygame.time.get_ticks()
        self.projectile_angle = 0
        self.damage = 0.001
        self.phase = 1

    def random_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        return math.cos(angle), math.sin(angle)

    def update(self, game_manager):
        now = pygame.time.get_ticks()
        if now - self.last_direction_change > self.direction_change_interval:
            self.dx, self.dy = self.random_direction()
            self.last_direction_change = now

        # Movimento
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # Mantém dentro da tela
        self.x = max(0, min(game_manager.screen_width - self.width, self.x))
        self.y = max(0, min(game_manager.screen_height - self.height, self.y))



        # Ataque
        if now - self.last_attack_time > self.attack_interval:
            self.attack(game_manager)
            self.last_attack_time = now

        self.projectile_angle += 10  # Aumenta o ângulo para o próximo projétil

        if self.lives <= 150 and self.phase == 1:
            self.phase = 2
            self.speed += 2
            self.attack_interval = 1700

    def attack(self, game_manager):
        for i in range(8):  # Dispara 8 projéteis em direções diferentes
            angle = math.radians(self.projectile_angle + i * 45)  # Espaçamento de 45 graus
            game_manager.spawn_projectile(self.x + self.width / 2, self.y + self.height / 2, angle, is_special=True, owner="night_boss", speed=2)

    def draw(self, surface):
        super().draw(surface)
        self.update_sprites()
        # Calcula a largura da barra de vida com base na vida atual do NightBoss
        life_bar_width = (self.lives / self.max_lives) * self.width
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, life_bar_width, 5))
 
class DragaoAncestral(AnimatedEntity):
    def __init__(self, x, y):
        sprite_paths = [f'assets/lastboss{i}.png' for i in range(4)]  # Substitua com os caminhos corretos para suas sprites
        super().__init__(x, y, 150, 150, sprite_paths, animation_time=0.2)
        self.max_lives = 400
        self.lives = self.max_lives
        self.speed = 1.7
        self.attack_cooldown = 1500  # 3 segundos entre ataques
        self.last_attack_time = 0
        self.angulo_de_ataque = 0
        
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

    def perform_fire_breath(self, game_manager):
        angle_to_player = math.atan2(game_manager.player.y - self.y, game_manager.player.x - self.x)
        fire_breath_count = 5  # Quantidade de chamas lançadas
        fire_breath_spread = 0.3  # Variação no ângulo para espalhar o fogo
        
        for i in range(fire_breath_count):
            angle_variation = random.uniform(-fire_breath_spread, fire_breath_spread)
            fire_angle = angle_to_player + angle_variation
            
            # Ajuste os parâmetros do projétil conforme necessário
            projectile = Projectile(self.x, self.y, fire_angle, size=2, speed=3, radius=10, damage=2, owner="cogu", is_special=True)
            game_manager.projectiles.append(projectile)

    def perform_call_of_the_elders(self, game_manager):
        meteor_count = 6  # Define quantos meteoros serão invocados por vez
        for _ in range(meteor_count):
            # Escolha posições aleatórias para cada meteoro cair
            x_pos = random.randint(0, game_manager.screen_width)
            y_pos = 0  # Começa do topo da tela
            angle = math.pi / 2  # Ângulo para cair verticalmente
            
            # Criação do projétil do meteoro
            projectile = Projectile(x_pos, y_pos, angle, size=2, speed=4, radius=15, damage=3, owner="cogu", is_special=True)
            game_manager.projectiles.append(projectile)

    def perform_spiral_attack(self, game_manager):
        # Define o número de projéteis no ataque espiral
        numero_de_projeteis = 16  # 36 --- Exemplo: cria um círculo completo com um projétil a cada 10 graus
        angulo_inicial = 0  # Começando de 0 graus

        for i in range(numero_de_projeteis):
            angulo = math.radians(angulo_inicial + (i * (360 / numero_de_projeteis)))
            game_manager.spawn_projectile(self.x + self.width / 2, self.y + self.height / 2, angulo, is_special=True, owner="cogu", speed=1.7)

    def perform_attack(self):
        # Implemente os ataques do Dragão Ancestral aqui
        pass

    def update(self, player_x, player_y, game_manager):
        # Atualiza posição e verifica se pode atacar
        self.move_towards_player(player_x, player_y)
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_attack_time > self.attack_cooldown:
            # Adicionando 'spiral_attack' às opções de ataque
            attack_choice = random.choice(["fire_breath", "call_of_the_elders", "spiral_attack"])
            if attack_choice == "fire_breath":
                self.perform_fire_breath(game_manager)
            elif attack_choice == "call_of_the_elders":
                self.perform_call_of_the_elders(game_manager)
            elif attack_choice == "spiral_attack":
                self.perform_spiral_attack(game_manager)  # Implementar este método
            self.last_attack_time = current_time
  
    def draw(self, surface):
            super().draw(surface)  # Chama o método draw da classe base para desenhar o sprite
            self.update_sprites()  # Atualiza para o próximo sprite, se necessário
            
            # Renderiza a barra de vida
            vida_porcentagem = self.lives / self.max_lives
            life_bar_width = vida_porcentagem * self.width
            pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 20, life_bar_width, 10))    
        
class Projectile:
    def __init__(self, x, y, angle, size=1, speed=15, radius=5, damage=1, owner="player", is_special=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.size = size
        self.radius = radius * self.size
        self.damage = damage if size == 1 else damage * 3
        self.owner = owner
        self.sprites = []
        self.current_sprite = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100
        
        if owner == "player" and not is_special:
            self.original_sprite = pygame.image.load("assets/semente.png").convert_alpha()
            self.sprites.append(pygame.transform.scale(self.original_sprite, (34,34)))
        elif owner == "player" and is_special:
            self.original_sprite = pygame.image.load("assets/leaf.png").convert_alpha()
            self.sprites.append(pygame.transform.scale(self.original_sprite, (100,100)))
        elif owner == "enemy":
            self.original_sprite = pygame.image.load("assets/pena.png").convert_alpha()
            self.sprites.append(pygame.transform.scale(self.original_sprite, (30,30)))
        elif owner == "boss":
            self.original_sprite = pygame.image.load("assets/sting.png").convert_alpha()
            self.sprites.append(pygame.transform.scale(self.original_sprite, (45,60)))
        elif owner == "night_boss":  # Adiciona a condição para o NightBoss
            sprite_paths = [f"assets/lua{i}.png" for i in range(4)]  # Ajuste o range conforme o número de sprites
            self.sprites = [pygame.transform.scale(pygame.image.load(path).convert_alpha(), (50, 50)) for path in sprite_paths]
        elif owner == "cogu":
            self.original_sprite = pygame.image.load("assets/veneno.png").convert_alpha()
            self.sprites.append(pygame.transform.scale(self.original_sprite, (50,50)))

        # self.sprite = self.original_sprite
        self.sprite = self.sprites[self.current_sprite]
        self.angle_degrees = -math.degrees(angle) - 90

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
            self.sprite = self.sprites[self.current_sprite]

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, surface):
        # Atualiza o sprite antes de desenhar
        self.update()
        # Rotaciona o sprite baseado no ângulo do tiro
        rotated_sprite = pygame.transform.rotate(self.sprite, self.angle_degrees)
        rect = rotated_sprite.get_rect(center=(self.x, self.y))
        surface.blit(rotated_sprite, rect.topleft)
        
class GameManager:
    def __init__(self, screen_width, screen_height):
        pygame.mixer.init()
        pygame.mouse.set_visible(False)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_paused = False
        
        self.boss = None
        self.night_boss = None
        self.night_boss_defeated = False
        self.aurora_started = False
        self.dragao_ancestral = None
        self.dragao_defeated = False
        
        self.current_score = 0
        self.high_score = self.load_high_score()
        
        self.mana_recharge_rate = 0.07
        self.damage_indicators = []
        self.mana_orbs = []
        
        self.animated_cursor = AnimatedEntity(0, 0, 60, 60, [f'assets/mira{i}.png' for i in range(1,5)], 0.5)
        
        self.fundo_day_surface = pygame.image.load('assets/fundo.png').convert()
        self.fundo_night_surface = pygame.image.load('assets/noite.png').convert()
        self.fundo_aurora_surface = pygame.image.load('assets/aurora.png').convert()

       
        self.fundo_aurora_surface = pygame.transform.scale(self.fundo_aurora_surface,(screen_width, screen_height))
        self.fundo_day_surface = pygame.transform.scale(self.fundo_day_surface, (screen_width, screen_height))
        self.fundo_night_surface = pygame.transform.scale(self.fundo_night_surface, (screen_width, screen_height))
        
        self.fundo_surface = self.fundo_day_surface
        self.font = pygame.font.Font(None, 36)
        self.data_time = 0
        self.is_night = False
        
        self.night_music_playing = False
        self.day_music = "assets/day.mp3"
        self.night_music = "assets/night.mp3"
        self.energy_sound = pygame.mixer.Sound("assets/pick.wav")
        self.water_sound = pygame.mixer.Sound("assets/pick2.wav")
        self.shoot_sound = pygame.mixer.Sound("assets/tiro.wav")
        
        pygame.mixer.music.load(self.day_music)  
        pygame.mixer.music.play(-1)    
        pygame.mixer.music.set_volume(0.2)     
        
        self.reset_game()
        
    def reset_game(self):
        self.game_over = False
        self.boss_defeated = False
        self.night_boss_defeated = False
        self.dragao_defeated = False
        self.aurora_started = False
        self.is_night = False
        self.fundo_surface = self.fundo_day_surface
        self.boss = None
        self.night_boss = None
        self.dragao_ancestral = None
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
            self.lives.append(AnimatedLife(random.randint(0, screen_width - 30), random.randint(0, screen_height - 30)))
            self.last_life_spawn = current_time

    def spawn_boss(self):
        # Condição para spawnar o boss
        if self.current_score > 1 and self.boss is None and not self.boss_defeated:
            self.boss = Boss(screen_width // 2, 100)  # posição de spawn

    def spawn_night_boss(self):
        # Somente spawnar o NightBoss se ainda não foi derrotado e as outras condições forem atendidas
        if not self.night_boss and not self.night_boss_defeated:
            self.night_boss = NightBoss(self.screen_width // 2, self.screen_height // 4)

    def spawn_projectile(self, x, y, angle, is_special, owner="",speed=15):
        size = 3 if is_special else 1
        radius = 10 if is_special else 5
        damage = 3 if is_special else 4 
        if owner == "enemy":
            speed = 3

        new_projectile = Projectile(x, y, angle, size, speed, radius, damage, owner)
        self.projectiles.append(new_projectile)

    def draw_pause_screen(self, surface):
        pause_overlay = pygame.Surface((self.screen_width, self.screen_height))
        pause_overlay.fill((0, 0, 0))
        pause_overlay.set_alpha(128)  # Semi-transparente
        surface.blit(pause_overlay, (0, 0))
        
        # Substitua isso pela imagem de comandos se desejar
        text = self.font.render('Jogo Pausado', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(text, text_rect)

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
                if event.key == pygame.K_p:  # Usando P para pausar/despausar
                    self.is_paused = not self.is_paused
                    if self.is_paused:

                        pygame.mixer.music.pause()
                    else:
                        # Retomar música ou sons
                        pygame.mixer.music.unpause()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.shoot_sound.play()
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

    def spawn_enemies(self):
        # Define o modificador de velocidade baseado no ciclo atual

        if len(self.enemies) < 6 and random.randint(0, 60) == 0:
            enemy = WhiteEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
        if len(self.enemies) < 4 and random.randint(0, 120) == 0:
            enemy = RedEnemy(random.randint(0, screen_width - 50), random.randint(0, screen_height - 50))
            self.enemies.append(enemy)
        if len(self.enemies) < 6 and random.randint(0, 1000) < 5:
            enemy = ShootingEnemy(random.randint(0, screen_width - 60), random.randint(0, screen_height - 60))
            self.enemies.append(enemy)

    def apply_knock_back(self, enemy, intensity=70):
        # Calcular a direção do knock back
        dx = enemy.x - self.player.x
        dy = enemy.y - self.player.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        # Evitar divisão por zero
        if dist == 0: dist = 1
        # Calcular o novo x e y baseado na intensidade
        new_x = enemy.x + (dx / dist) * intensity
        new_y = enemy.y + (dy / dist) * intensity
        # Assegurar que o inimigo não saia da tela
        enemy.x = max(0, min(screen_width - enemy.width, new_x))
        enemy.y = max(0, min(screen_height - enemy.height, new_y))

    def run(self):
        clock = pygame.time.Clock()
        draw_start_screen()
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting_for_input = False

        self.is_paused = False  # Inicializa a variável de pausa
        last_time = pygame.time.get_ticks()  # Inicializa a última marca de tempo
        while True:
            current_time = pygame.time.get_ticks()  # Obtém a marca de tempo atual
            self.delta_time = (current_time - last_time) / 1000.0  # Calcula o delta_time em segundos
            last_time = current_time  # Atualiza a última marca de tempo para a próxima iteração

            self.handle_events()  # Garanta que este método possa alterar self.is_paused

            if self.game_over:
                self.show_game_over_screen()
            if not self.game_over and not self.is_paused:
                keys = pygame.key.get_pressed()
                self.handle_events()
                self.spawn_lives()
                self.update(keys)  # Garanta que a pausa é checada dentro deste método também
                self.draw(screen)

                
            # Desenha o FPS na tela
            fps = clock.get_fps()
            fps_text = font.render(f"FPS: {fps:.2f}", True, pygame.Color('white'))
            screen.blit(fps_text, (10,5))
            
            pygame.display.flip()  # Atualiza a tela
            clock.tick(60)  # Limita o jogo a 60 FPS

    def update(self, keys):
        # 1. Atualização do jogador
        pygame.mixer.init()
        if self.is_paused:
            return
        self.player.move(keys)
        self.player.update_sprites()
        self.player.current_mana = min(self.player.current_mana + self.mana_recharge_rate, self.player.max_mana)
        self.player.mana_bar.update(self.player.current_mana)     
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.animated_cursor.x = mouse_x
        self.animated_cursor.y = mouse_y
        self.animated_cursor.update_sprites()
        
        # Ajusta a velocidade dos inimigos baseado na fase (dia ou noite)
        for enemy in self.enemies:
            self.update
            if self.is_night:
                enemy.speed = enemy.original_speed / 2
            else:
                enemy.speed = enemy.original_speed


            
        # 2. Tentativa de spawnar o boss
        self.spawn_boss()
        self.player.speed = 3 if self.is_night else 6
        # 3. Atualizar o boss, se ele existir
        if self.boss:
            self.boss.update(self.player.x, self.player.y, self)

        if self.current_score > 10 and self.boss_defeated and not self.night_boss:
            self.spawn_night_boss()
        if self.current_score > 25 and not self.dragao_ancestral and self.aurora_started:
            # Só spawnar o dragao_ancestral se a aurora já tiver começado
            self.dragao_ancestral = DragaoAncestral(self.screen_width // 2, 100)
        if self.dragao_ancestral:
            self.dragao_ancestral.update(self.player.x, self.player.y, self)
        if self.dragao_ancestral and self.dragao_ancestral.lives <= 0:
                self.dragao_defeated = True
                self.dragao_ancestral  = None
                self.show_end_screen(screen)
            



        # Atualiza o NightBoss, se ele existir
        if self.night_boss:
            self.night_boss.update(self)
            if self.night_boss and self.night_boss.lives <= 0:
                self.night_boss = None
                self.night_boss_defeated = True
                self.is_night = False
                self.update_music()# Marca como derrotado
                            # Implemente quaisquer ações adicionais necessárias aqui
                
        # Checagem de colisão entre o jogador e o boss
        if self.boss and pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)):
            damage = self.boss.damage  # Supondo que boss.damage contém o dano que o boss causa
            self.player.lose_life(damage)
            # Correção: Criação do indicador de dano ao jogador quando atingido pelo boss
            self.damage_indicators.append(DamageIndicator(self.player.x, self.player.y, damage, self.font))


        if self.night_boss and pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(self.night_boss.x, self.night_boss.y, self.night_boss.width, self.night_boss.height)):
            damage = self.night_boss.damage  # Aqui, supomos que o NightBoss tem um atributo 'damage'
            self.player.lose_life(damage)
            self.damage_indicators.append(DamageIndicator(self.player.x, self.player.y, damage, self.font))



                # Processamento de projéteis
        for projectile in self.projectiles[:]:
            projectile.move()
            if not (0 <= projectile.x <= screen_width and 0 <= projectile.y <= screen_height):
                self.projectiles.remove(projectile)
                continue

            proj_rect = pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2)

            if projectile.owner == "player" and self.boss and proj_rect.colliderect(pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)):
                # Aplica dano ao boss
                self.boss.lives -= projectile.damage
                # Adiciona indicador de dano
                self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                # Remove o projétil após colidir com o boss
                self.projectiles.remove(projectile)
                if self.boss.lives <= 0:
                    self.boss_defeated = True
                    self.boss = None  # Remove o boss do jogosssss
            
            if projectile.owner == "player":
                # Verifica se o NightBoss existe antes de checar colisões
                if self.night_boss and proj_rect.colliderect(pygame.Rect(self.night_boss.x, self.night_boss.y, self.night_boss.width, self.night_boss.height)):
                    self.night_boss.lives -= projectile.damage
                    self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                    self.projectiles.remove(projectile)
                    if self.night_boss and self.night_boss.lives <= 0:
                        self.night_boss = None
                        self.night_boss_defeated = True

            if projectile.owner == "player" and self.dragao_ancestral:
                dragao_rect = pygame.Rect(self.dragao_ancestral.x, self.dragao_ancestral.y, self.dragao_ancestral.width, self.dragao_ancestral.height)
                if proj_rect.colliderect(dragao_rect):
                    self.dragao_ancestral.lives -= projectile.damage
                    self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                    self.projectiles.remove(projectile)
                    if self.dragao_ancestral.lives <= 0:
                        # Handle dragao_ancestral defeat here
                        pass

                        
            elif projectile.owner == "night_boss":
                # Ignora projéteis do NightBoss colidindo com ele mesmo
                # Certifique-se de que o NightBoss existe antes de verificar a colisão
                if self.night_boss and proj_rect.colliderect(pygame.Rect(self.night_boss.x, self.night_boss.y, self.night_boss.width, self.night_boss.height)):
                    continue
                            
            # Checagem para projéteis do boss, inimigos comuns ou Night Boss atingindo o jogador
            if projectile.owner in ["boss", "enemy", "night_boss", "cogu"] and proj_rect.colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                self.player.lose_life(projectile.damage)
                # Adiciona indicador de dano ao jogador
                self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                self.projectiles.remove(projectile)


        for life in self.lives[:]: 
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(life.x, life.y, life.width, life.height)):
                self.player.current_health += 6  
                self.player.current_health = min(self.player.current_health, self.player.max_health)
                self.player.health_bar.update(self.player.current_health)
                
                self.lives.remove(life)
                self.energy_sound.play() 
                                     
        for enemy in self.enemies[:]:
            if pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height).colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                damage_indicator = DamageIndicator(enemy.x, enemy.y, enemy.damage, self.font)
                self.damage_indicators.append(damage_indicator)
                self.player.lose_life(enemy.damage)
                self.apply_knock_back(enemy) 
                             
        for enemy in self.enemies:
            enemy.move_towards_player(self.player.x, self.player.y)  # Atualiza posição dos inimigos
            enemy.update_sprites()
        
        for orb in self.mana_orbs[:]:
            orb.update_sprites()
            
        for orb in self.mana_orbs[:]:
            # Verifica se a distância entre os centros dos objetos é menor que a soma de seus raios
            if math.sqrt((self.player.x + self.player.width / 2 - (orb.x + orb.width / 2))**2 + (self.player.y + self.player.height / 2 - (orb.y + orb.height / 2))**2) < (self.player.width / 2 + orb.width / 2):
                # Se houver colisão
                self.mana_orbs.remove(orb)
                self.player.current_mana += 10  # Adiciona mana ao jogador
                self.player.current_mana = min(self.player.current_mana, self.player.max_mana)  # Garante que a mana não exceda o máximo
                self.water_sound.play()
        
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
                    self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                    self.projectiles.remove(projectile)
            # Para projéteis do jogador, verificar colisão com inimigos e boss
            elif projectile.owner == "player":
                for enemy in self.enemies[:]:
                    if pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height).colliderect(pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2)):
                        enemy.lose_life(projectile.damage)
                        if not enemy.is_alive():
                            self.enemies.remove(enemy)
                        self.projectiles.remove(projectile)
                        self.damage_indicators.append(DamageIndicator(projectile.x, projectile.y, projectile.damage, self.font))
                        self.current_score += enemy.score_value
                        if random.random() < 0.3:  # Exemplo de chance de 30% de dropar vida
                            self.lives.append(AnimatedLife(enemy.x, enemy.y))
                        if random.random() < 0.3:  # Exemplo de chance de 30% de dropar mana
                            self.mana_orbs.append(ManaOrb(enemy.x, enemy.y))
                        break  # Previne múltiplas colisões com o mesmo projétil         
        # Exemplo simplificado de verificação de game over
        if not self.player.is_alive():
            self.game_over = True
        
        if self.boss_defeated and not self.is_night:
            self.is_night = True
            self.fundo_surface = self.fundo_night_surface  # Altera para fundo noturno
            
        if self.night_boss_defeated:
            # Transita para o dia
            self.is_night = False
            self.fundo_surface = self.fundo_aurora_surface
            self.aurora_started = True
            # self.update_music()
        self.update_music()
        self.spawn_enemies()

    def update_music(self):
        if self.is_night and not self.night_music_playing:
            pygame.mixer.music.load(self.night_music)
            pygame.mixer.music.play(-1)
            self.night_music_playing = True
        elif not self.is_night and self.night_music_playing:
            pygame.mixer.music.load(self.day_music)
            pygame.mixer.music.play(-1)
            self.night_music_playing = False
  
    def draw(self, surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.animated_cursor.x = mouse_x - self.animated_cursor.width / 2
        self.animated_cursor.y = mouse_y - self.animated_cursor.height / 2
        surface.blit(self.fundo_surface, (0, 0))
        
        for indicator in self.damage_indicators[:]:
            indicator.update()
            indicator.draw(surface)  # Alterado para 'surface' em vez de 'screen'
            if indicator.is_expired():
                self.damage_indicators.remove(indicator)
        
        for projectile in self.projectiles:
            projectile.draw(surface)  # Alterado para 'surface' em vez de 'screen'
        
        for enemy in self.enemies:
            enemy.draw(surface)  # Alterado para 'surface' em vez de 'screen'
            if isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.x, self.player.y, self)
        
        for life in self.lives:
            life.draw(surface)  # Alterado para 'surface' em vez de 'screen'
            life.update_sprites()
        
        for orb in self.mana_orbs:
            surface.blit(orb.sprites[orb.current_sprite], (orb.x, orb.y))  # Alterado para 'surface' em vez de 'screen'
        
        if self.boss:
            self.boss.draw(surface)
        self.player.draw(surface)
        
        if self.night_boss:
            self.night_boss.draw(surface)  # Alterado para 'surface'
        if self.dragao_ancestral:
            self.dragao_ancestral.draw(surface)  # Alterado para 'surface'

        score_text = self.font.render(f"Score: {self.current_score}", True, WHITE)
        surface.blit(score_text, (self.screen_width - 180, 10))
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        surface.blit(high_score_text, (self.screen_width - 180, 30))

        if self.is_paused:
            # Aqui chamamos o método que desenha a tela de pausa
            self.draw_pause_screen(surface)
        
        # Isso garante que qualquer coisa desenhada após este ponto seja exibida por cima do jogo
        # Então, se o draw_pause_screen não estiver funcionando, isso deveria funcionar como um teste
        if self.is_paused:
            # Exemplo simples para teste: Desenha um retângulo vermelho grande no meio da tela
            pygame.draw.rect(surface, (255, 0, 0), (100, 100, self.screen_width - 200, self.screen_height - 200))
            pause_text = self.font.render('PAUSA', True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(pause_text, text_rect)
                
        self.animated_cursor.draw(surface)
        pygame.display.flip()

    def show_game_over_screen(self):
        screen.blit(game_over_surface, (0, 0))
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

    def show_end_screen(self, surface):
        surface.blit(end_screen_image, (0, 0))  # Ajuste a posição conforme necessário
        pygame.display.update()  # Atualiza a tela para mostrar a imagem

        # Espera pelo input do jogador para reiniciar ou sair
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Supondo que SPACE reinicia o jogo
                        self.reset_game()  # Reinicia o jogo
                        waiting_for_input = False
                    elif event.key == pygame.K_ESCAPE:  # Supondo que ESC saia do jogo
                        pygame.quit()
                        exit()
            
def draw_start_screen():
    screen.blit(start_screen_surface, (0, 0))
    pygame.display.flip()



if __name__ == "__main__":
    game_manager = GameManager(screen_width,screen_height)
    game_manager.run()
