# Enable pygame_sdl2 if available (Android Kivy/Buildozer environment)
try:
    import pygame_sdl2
    # This replaces the standard pygame module with pygame_sdl2
    pygame_sdl2.import_as_pygame()
except ImportError:
    pass

import pygame
import random
import math
import sys
import os
import traceback
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import time
from collections import defaultdict

_font_cache = {}
def get_font(size):
    if size in _font_cache:
        return _font_cache[size]
    
    font = None
    # Intentar usar fuentes del sistema Android primero para evitar crasheos si falta freesansbold
    paths = [
        "/system/fonts/Roboto-Regular.ttf",
        "/system/fonts/DroidSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                font = pygame.font.Font(p, size)
                break
            except Exception:
                pass
    if not font:
        try:
            font = pygame.font.Font(None, size)
        except Exception:
            font = pygame.font.SysFont(None, size)
            
    _font_cache[size] = font
    return font

# --- Constantes Configurables ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
PROJECTILE_SPEED = 4
FPS = 60

# --- Colores (Estilo Boceto de LÃ¡piz) ---
BLACK = (30, 30, 30)
WHITE = (245, 245, 245)
GRAY = (150, 150, 150)

class VirtualButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_pressed = False
        self.font = get_font(40)
        
    def draw(self, surface):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        color = (150, 150, 150, 128) if not self.is_pressed else (200, 200, 200, 180)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=15)
        pygame.draw.rect(s, (0, 0, 0, 150), s.get_rect(), 2, border_radius=15)
        surface.blit(s, self.rect.topleft)
        
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Player:
    def __init__(self, x, y):
        # Ajustado para acomodar las formas del caniche
        self.width = 90
        self.height = 90
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.hp = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.on_ladder = False
        self.y_velocity = 0
        self.gravity = 0.5
        
        self.facing_right = True
        
        import os
        self.images = {}
        if os.path.exists(os.path.join(BASE_DIR, "player_frames/player_stand_right.png")):
            img = pygame.image.load(os.path.join(BASE_DIR, "player_frames/player_stand_right.png")).convert_alpha()
            self.images['right'] = pygame.transform.smoothscale(img, (self.width, self.height))
        if os.path.exists(os.path.join(BASE_DIR, "player_frames/player_stand_left.png")):
            img = pygame.image.load(os.path.join(BASE_DIR, "player_frames/player_stand_left.png")).convert_alpha()
            self.images['left'] = pygame.transform.smoothscale(img, (self.width, self.height))
            
        self.image = self.images.get('right', None)

    def update(self, keys, ladders, floor_rect):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_right = True
            
        if self.x < 0: 
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width: 
            self.x = SCREEN_WIDTH - self.width

        self.rect.x = self.x

        self.on_ladder = False
        current_ladder = None
        for ladder in ladders:
            if self.rect.colliderect(ladder):
                self.on_ladder = True
                current_ladder = ladder
                break

        if self.on_ladder:
            self.y_velocity = 0 
            if keys[pygame.K_UP]:
                self.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.y += self.speed
            
            # Jump off the ladder
            if keys[pygame.K_SPACE]:
                self.on_ladder = False
                self.y_velocity = -12
            
            if current_ladder and self.y < current_ladder.top:
                self.y = current_ladder.top
        else:
            # Jumping logic if touching the floor
            if keys[pygame.K_SPACE] and self.rect.bottom >= floor_rect.top:
                self.y_velocity = -12.0
                
            self.y_velocity += self.gravity
            self.y += self.y_velocity

        self.rect.y = self.y

        if self.rect.colliderect(floor_rect):
            if self.y_velocity > 0:
                self.rect.bottom = floor_rect.top
                self.y = self.rect.y
                self.y_velocity = 0

    def draw(self, surface):
        current_image = self.images.get('right') if self.facing_right else self.images.get('left')
        
        if current_image:
            surface.blit(current_image, (self.x, self.y))
        elif getattr(self, 'image', None):
            surface.blit(self.image, (self.x, self.y))
        else:
            # Perrito (Estilo Caniche del Boceto)
            center_x = self.x + self.width // 2
            
            # Cuerpo base
            pygame.draw.ellipse(surface, WHITE, (self.x + 5, self.y + 15, self.width - 10, self.height - 15))
            pygame.draw.ellipse(surface, BLACK, (self.x + 5, self.y + 15, self.width - 10, self.height - 15), 2)
            
            # Cabeza (esfera principal)
            head_y = self.y + 10
            pygame.draw.circle(surface, WHITE, (center_x, head_y), 15)
            pygame.draw.circle(surface, BLACK, (center_x, head_y), 15, 2)
            
            # Oreja izquierda
            pygame.draw.ellipse(surface, WHITE, (self.x - 5, head_y - 2, 16, 22))
            pygame.draw.ellipse(surface, BLACK, (self.x - 5, head_y - 2, 16, 22), 2)
            
            # Oreja derecha
            pygame.draw.ellipse(surface, WHITE, (self.x + self.width - 11, head_y - 2, 16, 22))
            pygame.draw.ellipse(surface, BLACK, (self.x + self.width - 11, head_y - 2, 16, 22), 2)
            
            # Pelo superior superior ("copete")
            pygame.draw.circle(surface, WHITE, (center_x, self.y), 12)
            pygame.draw.circle(surface, BLACK, (center_x, self.y), 12, 2)
            
            # Rostro
            pygame.draw.circle(surface, BLACK, (center_x, head_y + 5), 2) # Nariz
            pygame.draw.circle(surface, BLACK, (center_x - 5, head_y - 1), 2) # Ojo izq
            pygame.draw.circle(surface, BLACK, (center_x + 5, head_y - 1), 2) # Ojo der
            
            # Patitas inferiores
            pygame.draw.line(surface, BLACK, (self.x + 10, self.y + self.height), (self.x + 10, self.y + self.height - 8), 2)
            pygame.draw.line(surface, BLACK, (self.x + 20, self.y + self.height), (self.x + 20, self.y + self.height - 8), 2)
            pygame.draw.line(surface, BLACK, (self.x + 30, self.y + self.height), (self.x + 30, self.y + self.height - 8), 2)


class Enemy:
    def __init__(self, x, y):
        self.width = 160 # Gato gigante
        self.height = 140
        self.x = x
        self.y = y
        self.speed = ENEMY_SPEED
        self.hp = 6
        self.max_hp = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.direction = 1
        self.y_velocity = 0
        self.gravity = 0.5
        
        self.shoot_timer = 0
        self.jump_timer = 0
        self.state = "idle" # idle, jump, shoot, damage
        
        import os
        self.images = {}
        if os.path.exists(os.path.join(BASE_DIR, "boss_square.png")):
            img = pygame.image.load(os.path.join(BASE_DIR, "boss_square.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (self.width, self.height))
        else:
            self.image = None

    def update(self, floor_rect, player, projectiles):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        
        limit_left = SCREEN_WIDTH // 2 - 200
        limit_right = SCREEN_WIDTH // 2 + 200 - self.width
        
        if self.x < limit_left:
            self.x = limit_left
            self.direction = 1
        elif self.x > limit_right:
            self.x = limit_right
            self.direction = -1

        self.jump_timer += 1
        if self.jump_timer > 120:
            if random.random() < 0.6 and self.y_velocity == 0.0:
                self.y_velocity = -12.0  
                self.state = "angry"
            self.jump_timer = 0
        
        self.y_velocity += self.gravity
        self.y += self.y_velocity
        self.rect.y = self.y

        if self.rect.colliderect(floor_rect):
            if self.y_velocity > 0:
                self.rect.bottom = floor_rect.top
                self.y = self.rect.y
                self.y_velocity = 0
                if self.state == "angry":
                    self.state = "idle"

        self.shoot_timer += 1
        # Prepare attack animation brief before shooting
        if self.shoot_timer > 80:
             if self.state != "angry":
                 self.state = "attack"
             
        if self.shoot_timer > 90:  
            self.shoot(player, projectiles)
            self.shoot_timer = 0
            if self.state == "attack":
                self.state = "idle"

    def shoot(self, player, projectiles):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2
        
        dx = player_center_x - center_x
        dy = player_center_y - center_y
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1  
        
        dir_x = (dx / dist) * PROJECTILE_SPEED
        dir_y = (dy / dist) * PROJECTILE_SPEED
        
        proj = Projectile(center_x, center_y, dir_x, dir_y)
        projectiles.append(proj)

    def draw(self, surface):
        if getattr(self, 'image', None):
            surface.blit(self.image, (self.x, self.y))
        else:
            # Fallback a Cara cuadrada del boceto si no encuentra la imagen
            pygame.draw.rect(surface, WHITE, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 2)
            
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Ojos rectangulares (\ /)
            eye_w, eye_h = 30, 20
            left_eye_x = self.x + 35
            right_eye_x = self.x + self.width - 35 - eye_w
            eye_y = self.y + 40
            
            # Ojo izquierdo
            pygame.draw.rect(surface, BLACK, (left_eye_x, eye_y, eye_w, eye_h), 2)
            pygame.draw.circle(surface, BLACK, (left_eye_x + eye_w // 2, eye_y + eye_h // 2), 4)
            
            # Ojo derecho
            pygame.draw.rect(surface, BLACK, (right_eye_x, eye_y, eye_w, eye_h), 2)
            pygame.draw.circle(surface, BLACK, (right_eye_x + eye_w // 2, eye_y + eye_h // 2), 4)
            
            # Cejas enojadas
            pygame.draw.line(surface, BLACK, (center_x - 35, eye_y - 15), (center_x - 10, eye_y), 2)
            pygame.draw.line(surface, BLACK, (center_x + 35, eye_y - 15), (center_x + 10, eye_y), 2)
            
            # Nariz y lÃ­nea central
            pygame.draw.circle(surface, BLACK, (center_x, center_y + 10), 3)
            pygame.draw.line(surface, BLACK, (center_x, center_y + 12), (center_x, center_y + 35), 2)
            
            # Boca
            pygame.draw.line(surface, BLACK, (center_x - 20, center_y + 35), (center_x + 20, center_y + 35), 2)
            pygame.draw.line(surface, BLACK, (center_x - 20, center_y + 30), (center_x - 20, center_y + 35), 2)
            pygame.draw.line(surface, BLACK, (center_x + 20, center_y + 30), (center_x + 20, center_y + 35), 2)
            
            # Bigotes de gato
            pygame.draw.line(surface, BLACK, (center_x - 50, center_y + 15), (center_x - 25, center_y + 19), 2)
            pygame.draw.line(surface, BLACK, (center_x - 50, center_y + 25), (center_x - 25, center_y + 23), 2)
            pygame.draw.line(surface, BLACK, (center_x + 50, center_y + 15), (center_x + 25, center_y + 19), 2)
            pygame.draw.line(surface, BLACK, (center_x + 50, center_y + 25), (center_x + 25, center_y + 23), 2)


class Candy:
    def __init__(self, ladders):
        self.radius = 24
        self.ladders = ladders
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        import os
        if os.path.exists(os.path.join(BASE_DIR, "candy.png")):
            self.image = pygame.image.load(os.path.join(BASE_DIR, "candy.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (self.radius * 2, self.radius * 2))
        else:
            self.image = None
        self.spawn()

    def spawn(self):
        chosen_ladder = random.choice(self.ladders)
        self.x = chosen_ladder.x + chosen_ladder.width // 2
        # Aparece siempre en la cima de la escalera (como en el dibujo)
        self.y = chosen_ladder.top + self.radius + 5
        
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        pass

    def draw(self, surface):
        if getattr(self, 'image', None):
            surface.blit(self.image, (self.x - self.radius, self.y - self.radius))
        else:
            # CÃ­rculo con el guiÃ³n "-" dibujado dentro
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
            # GuiÃ³n "menos" en el interior
            pygame.draw.line(surface, BLACK, (self.x - 6, self.y), (self.x + 6, self.y), 2)


class Projectile:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 12 # Hacer el proyectil mas grande
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        
        import os
        if os.path.exists(os.path.join(BASE_DIR, "fireball.png")):
            self.image = pygame.image.load(os.path.join(BASE_DIR, "fireball.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (self.radius * 4, self.radius * 2))
            # The original image faces right. If shooting left, flip it.
            if self.dx < 0:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = None

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        
    def out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

    def draw(self, surface):
        if getattr(self, 'image', None):
            # Centrar la imagen elongada sobre el hitbox circular
            surface.blit(self.image, (self.x - self.radius * 2, self.y - self.radius))
        else:
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)


class Game:
    def __init__(self):
        pygame.init()
        # En Android, Kivy/Pygame maneja el tamaÃ±o automÃ¡ticamente
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arcade Prototipo - Dibujo en Servilleta")
        self.clock = pygame.time.Clock()
        
        # Load background image
        import os
        if os.path.exists(os.path.join(BASE_DIR, "background.jpg")):
            bg_img = pygame.image.load(os.path.join(BASE_DIR, "background.jpg")).convert()
            self.background = pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background = None

        # Load heart sprite for health
        if os.path.exists(os.path.join(BASE_DIR, "heart.png")):
            heart_img = pygame.image.load(os.path.join(BASE_DIR, "heart.png")).convert_alpha()
            # Scale down to a reasonable UI size (e.g. 30x30)
            self.heart_sprite = pygame.transform.smoothscale(heart_img, (30, 30))
        else:
            self.heart_sprite = None
            
        # Load boss health bar sprite
        if os.path.exists(os.path.join(BASE_DIR, "boss_bar.png")):
            boss_bar_img = pygame.image.load(os.path.join(BASE_DIR, "boss_bar.png")).convert_alpha()
            # It's originally 1028 px wide; scale it down to appropriate screen width
            self.boss_bar_width = 400
            self.boss_bar_height = 30
            self.boss_bar_sprite = pygame.transform.smoothscale(boss_bar_img, (self.boss_bar_width, self.boss_bar_height))
        else:
            self.boss_bar_sprite = None
            
        self.ground_y = 520
        self.floor_rect = pygame.Rect(0, self.ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.ground_y)
        
        # Escaleras mÃ¡s altas llegando al tope
        ladder_width = 80
        ladder_height = 480
        ladder_y = self.ground_y - ladder_height
        
        self.ladder_left = pygame.Rect(80, ladder_y, ladder_width, ladder_height)
        self.ladder_right = pygame.Rect(SCREEN_WIDTH - 160, ladder_y, ladder_width, ladder_height)
        self.ladders = [self.ladder_left, self.ladder_right]
        
        if os.path.exists(os.path.join(BASE_DIR, "ladder.png")):
            self.ladder_img = pygame.image.load(os.path.join(BASE_DIR, "ladder.png")).convert_alpha()
        else:
            self.ladder_img = None

        if os.path.exists(os.path.join(BASE_DIR, "ground.png")):
            self.ground_img = pygame.image.load(os.path.join(BASE_DIR, "ground.png")).convert_alpha()
            # Stretch the ground sprite to match the floor rectangle dimensions
            self.ground_img = pygame.transform.smoothscale(
                self.ground_img,
                (self.floor_rect.width, self.floor_rect.height)
            )
        else:
            self.ground_img = None

        self.player = Player(80, self.ground_y - 40)
        self.enemy = Enemy(SCREEN_WIDTH // 2 - 80, self.ground_y - 140)
        
        self.projectiles = []
        self.candy = Candy(self.ladders)

        # Controles Virtuales
        self.active_touches = {}
        border = 20
        btn_size = 70
        dpad_x = border + btn_size
        dpad_y = SCREEN_HEIGHT - border - btn_size * 2
        
        self.btn_up = VirtualButton(dpad_x, dpad_y - btn_size, btn_size, btn_size, "^")
        self.btn_down = VirtualButton(dpad_x, dpad_y + btn_size, btn_size, btn_size, "v")
        self.btn_left = VirtualButton(dpad_x - btn_size, dpad_y, btn_size, btn_size, "<")
        self.btn_right = VirtualButton(dpad_x + btn_size, dpad_y, btn_size, btn_size, ">")
        
        self.btn_jump = VirtualButton(SCREEN_WIDTH - border - int(btn_size * 2.5), dpad_y, int(btn_size * 2.5), btn_size, "SALTO")
        
        self.buttons = [self.btn_up, self.btn_down, self.btn_left, self.btn_right, self.btn_jump]

        self.state = "PLAYING" 
        self.jump_requested = False

    def reset(self):
        self.player = Player(80, self.ground_y - 40)
        self.enemy = Enemy(SCREEN_WIDTH // 2 - 80, self.ground_y - 140)
        self.projectiles = []
        self.candy = Candy(self.ladders)
        self.state = "PLAYING"

    def eval_buttons(self):
        for btn in self.buttons:
            btn.is_pressed = False
            
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            for btn in self.buttons:
                if btn.rect.collidepoint(mouse_pos):
                    btn.is_pressed = True
                    
        for touch_id, pos in self.active_touches.items():
            abs_pos = (pos[0] * SCREEN_WIDTH, pos[1] * SCREEN_HEIGHT)
            for btn in self.buttons:
                if btn.rect.collidepoint(abs_pos):
                    btn.is_pressed = True

    def update(self):
        self.eval_buttons()
        raw_keys = pygame.key.get_pressed()
        
        inputs = {
            pygame.K_LEFT: raw_keys[pygame.K_LEFT],
            pygame.K_RIGHT: raw_keys[pygame.K_RIGHT],
            pygame.K_UP: raw_keys[pygame.K_UP],
            pygame.K_DOWN: raw_keys[pygame.K_DOWN],
            pygame.K_SPACE: raw_keys[pygame.K_SPACE],
            pygame.K_RETURN: raw_keys[pygame.K_RETURN]
        }
            
        inputs[pygame.K_LEFT] = inputs[pygame.K_LEFT] or self.btn_left.is_pressed
        inputs[pygame.K_RIGHT] = inputs[pygame.K_RIGHT] or self.btn_right.is_pressed
        inputs[pygame.K_UP] = inputs[pygame.K_UP] or self.btn_up.is_pressed
        inputs[pygame.K_DOWN] = inputs[pygame.K_DOWN] or self.btn_down.is_pressed
        
        # El botÃ³n de salto tambiÃ©n comprueba si se presionÃ³ al instante (jump_requested)
        inputs[pygame.K_SPACE] = inputs[pygame.K_SPACE] or self.btn_jump.is_pressed or self.jump_requested
        self.jump_requested = False # Consume event
        
        if self.state != "PLAYING":
            if inputs[pygame.K_RETURN] or any(btn.is_pressed for btn in self.buttons):
                self.reset()
            return

        self.player.update(inputs, self.ladders, self.floor_rect)
        self.enemy.update(self.floor_rect, self.player, self.projectiles)
        self.candy.update()

        for proj in self.projectiles[:]:
            proj.update()
            if proj.out_of_bounds():
                self.projectiles.remove(proj)
            elif self.player.rect.colliderect(proj.rect):
                self.player.hp -= 1
                self.projectiles.remove(proj)
                if self.player.hp <= 0:
                    self.state = "LOSE"

        if self.player.rect.colliderect(self.candy.rect):
            self.enemy.hp -= 1
            self.candy.spawn()
            if self.enemy.hp <= 0:
                self.state = "WIN"

    def draw_text_centered(self, text, x, y, color, size):
        font = get_font(size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        # 3 Vidas en forma de corazÃ³n a la izquierda
        for i in range(self.player.hp):
            hx = 60 + i * 40
            hy = 40
            
            if getattr(self, 'heart_sprite', None):
                # We center the sprite approximately where the polygon was
                self.screen.blit(self.heart_sprite, (hx - 15, hy - 15))
            else:
                # Dibujar un corazÃ³n usando polÃ­gonos (Fallback)
                points = [
                    (hx, hy + 12),       # Punta abajo
                    (hx - 12, hy),       # Extremo izquierdo
                    (hx - 12, hy - 6),   # Superior izquierdo
                    (hx - 6, hy - 10),   # Arco izquierdo
                    (hx, hy - 4),        # Hendidura central
                    (hx + 6, hy - 10),   # Arco derecho
                    (hx + 12, hy - 6),   # Superior derecho
                    (hx + 12, hy)        # Extremo derecho
                ]
                pygame.draw.polygon(self.screen, WHITE, points)
                pygame.draw.polygon(self.screen, BLACK, points, 2)
            
        # Barra de vida del Jefe (Sprite customizado)
        bar_x = (SCREEN_WIDTH - 400) // 2
        bar_y = 30
        
        if getattr(self, 'boss_bar_sprite', None):
            # Calculate the percentage of health remaining
            health_ratio = self.enemy.hp / self.enemy.max_hp
            
            # The width of the visible part of the full bar
            visible_width = int(self.boss_bar_width * health_ratio)
            
            if visible_width > 0:
                # Create a subsurface representing the left portion of the image based on HP
                visible_rect = pygame.Rect(0, 0, visible_width, self.boss_bar_height)
                subsurface = self.boss_bar_sprite.subsurface(visible_rect)
                
                # Draw the cropped sprite
                self.screen.blit(subsurface, (bar_x, bar_y))
        else:
            # Fallback - Barra de vida segmentada
            bar_width = 400
            segment_width = bar_width // self.enemy.max_hp
            bar_height = 20
            
            for i in range(self.enemy.max_hp):
                rect = (bar_x + i * segment_width, bar_y, segment_width, bar_height)
                color = GRAY if i < self.enemy.hp else WHITE
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                
        for btn in self.buttons:
            btn.draw(self.screen)

    def draw(self):
        # Background
        if getattr(self, 'background', None):
            self.screen.blit(self.background, (0, 0))
        else:
            # Color del fondo simulando la textura pÃ¡lida
            self.screen.fill(WHITE)

        # Suelo
        if getattr(self, 'ground_img', None):
            # Alinear el sprite con el rectangulo del piso
            self.screen.blit(self.ground_img, (self.floor_rect.x, self.floor_rect.y))
        else:
            pygame.draw.rect(self.screen, WHITE, self.floor_rect)
            pygame.draw.line(self.screen, BLACK, (0, self.ground_y), (SCREEN_WIDTH, self.ground_y), 2)

        # Escaleras dibujadas con sprite o lineas de respaldo
        for ladder in self.ladders:
            if getattr(self, 'ladder_img', None):
                scaled_ladder = pygame.transform.smoothscale(self.ladder_img, (ladder.width, ladder.height))
                self.screen.blit(scaled_ladder, (ladder.x, ladder.y))
            else:
                pygame.draw.rect(self.screen, WHITE, ladder)
                # Rieles
                pygame.draw.line(self.screen, BLACK, (ladder.left, ladder.top), (ladder.left, ladder.bottom), 2)
                pygame.draw.line(self.screen, BLACK, (ladder.right, ladder.top), (ladder.right, ladder.bottom), 2)
                
                # PeldaÃ±os espaciados
                for y_step in range(ladder.top + 30, ladder.bottom, 30):
                    pygame.draw.line(self.screen, BLACK, (ladder.left, y_step), (ladder.right, y_step), 2)

        # Entidades
        if self.state != "WIN":
            self.enemy.draw(self.screen)
        
        self.candy.draw(self.screen)
        
        for proj in self.projectiles:
            proj.draw(self.screen)
            
        self.player.draw(self.screen)

        # UI
        self.draw_ui()

        # States
        if self.state == "WIN":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            self.screen.blit(overlay, (0,0))
            self.draw_text_centered("Â¡VICTORIA!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, BLACK, 80)
            self.draw_text_centered("Presiona ENTER para jugar de nuevo", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, BLACK, 30)
            
        elif self.state == "LOSE":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            self.screen.blit(overlay, (0,0))
            self.draw_text_centered("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, BLACK, 80)
            self.draw_text_centered("Presiona ENTER para reintentar", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, BLACK, 30)

        pygame.display.flip()

    def run(self):
        running = True
        self.jump_requested = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.btn_jump.rect.collidepoint(event.pos):
                        self.jump_requested = True
                elif event.type == pygame.FINGERDOWN:
                    self.active_touches[event.finger_id] = (event.x, event.y)
                    # ComprobaciÃ³n instantÃ¡nea para toque
                    abs_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
                    if self.btn_jump.rect.collidepoint(abs_pos):
                        self.jump_requested = True
                elif event.type == pygame.FINGERMOTION:
                    self.active_touches[event.finger_id] = (event.x, event.y)
                elif event.type == pygame.FINGERUP:
                    if event.finger_id in self.active_touches:
                        del self.active_touches[event.finger_id]
            
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def show_crash_and_exit(crash_text):
    import pygame
    pygame.init()
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except:
        screen = pygame.display.set_mode((800, 600))
        
    screen.fill((150, 0, 0))
    
    try:
        font = pygame.font.SysFont(None, 30)
    except Exception:
        font = pygame.font.Font(pygame.font.get_default_font(), 30)
        
    y = 20
    for line in crash_text.split('\n'):
        # Wrapear lineas largas para que se lean en el celu
        while len(line) > 50:
            chunk = line[:50]
            line = line[50:]
            txt = font.render(chunk, True, (255, 255, 255))
            screen.blit(txt, (20, y))
            y += 35
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (20, y))
        y += 35
        
    pygame.display.flip()
    
    import time
    start_time = time.time()
    while time.time() - start_time < 20:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                start_time = 0 # force exit
        pygame.time.delay(50)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import os
    import sys
    import traceback
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Intentar guardar el crash en un lugar público de Android para que el usuario pueda leerlo
    try:
        from android.storage import primary_external_storage_path
        public_dir = os.path.join(primary_external_storage_path(), "Documents")
        if not os.path.exists(public_dir):
            os.makedirs(public_dir, exist_ok=True)
        crash_file = os.path.join(public_dir, "arcade_game_crash.txt")
    except Exception:
        # Fallback a local
        app_dir = os.path.dirname(os.path.abspath(__file__))
        crash_file = os.path.join(app_dir, "internal_crash.txt")
    
    # 1. Chequear si hubo un crash en la sesion anterior
    if os.path.exists(crash_file):
        with open(crash_file, "r") as f:
            old_crash = f.read()
        try:
            os.remove(crash_file)
        except Exception:
            pass
        show_crash_and_exit("LAST CRASH:\n" + old_crash)
        
    # 2. Correr el juego normal
    try:
        game = Game()
        game.run()
    except Exception as e:
        crash_text = traceback.format_exc()
        # Escribir el log para leerlo despues (o mostrarlo en el proximo arranque)
        try:
            with open(crash_file, "w") as f:
                f.write("CRASH LOG:\n" + crash_text)
        except Exception as write_e:
            pass
            
        print("CRASH FATAL:", crash_text)
        
        # Logging de Android
        try:
            from jnius import autoclass
            Log = autoclass('android.util.Log')
            Log.e("ArcadeGame", "Crash: " + crash_text)
        except Exception:
            pass
            
        # Intentar mostrarlo ahora mismo si es posible
        try:
            show_crash_and_exit("CRASH AHORA:\n" + crash_text)
        except Exception:
            sys.exit(1)

