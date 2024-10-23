import pygame 
from pygame import mixer
import os
import random
import csv
import button 

mixer.init()
pygame.init()

# getting full path of the current file
file_path = os.path.realpath(__file__)

# extracting directory path
directory_path = os.path.dirname(file_path)

file_path = directory_path + '/'
screenset_WIDTH = 1200
screenset_HEIGHT = int(screenset_WIDTH * 0.65)

screenset = pygame.display.set_mode((screenset_WIDTH, screenset_HEIGHT))
pygame.display.set_caption('Rembo')

# setting framerate
clock = pygame.time.Clock()
FPS = 60

# defining game variables
GRAVITY = 0.75
SCROLL_THRESH = 200 
ROWS = 16
COLS = 150
TILE_SIZE = screenset_HEIGHT // ROWS
TILE_TYPES = 22
MAX_LEVELS = 3
screenset_scroll = 0 
bg_scroll = 0
level = 1
score = 0
start_game = False
start_intro = False

# defining player action variables 
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
boss = None
#load music/sounds
pygame.mixer.music.load(file_path + 'audio/Background.wav')
pygame.mixer.music.set_volume(0.3)  # Set the background music volume to 30%
pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=5000)  # Loop the music indefinitely with a 5-second fade-in

# Load and adjust the volume for various sound effects
jump_sound = pygame.mixer.Sound(file_path + 'audio/Jumping.wav')
jump_sound.set_volume(0.5)  # Set jump sound effect volume to 50%

shot_sound = pygame.mixer.Sound(file_path + 'audio/Shooting.wav')
shot_sound.set_volume(0.5)  # Set shooting sound effect volume to 50%

grenade_sound = pygame.mixer.Sound(file_path + 'audio/Exploding.wav')
grenade_sound.set_volume(0.5)  # Set explosion sound effect volume to 50%

#load images 
#button images
# Load button images and convert them with alpha transparency
start_img = pygame.image.load(file_path + 'img/start_btn.png').convert_alpha()
exit_img = pygame.image.load(file_path + 'img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load(file_path + 'img/restart_btn.png').convert_alpha()

# Load background images with alpha transparency
cloud_img = pygame.image.load(file_path + 'img/Background/clouds.jpg').convert_alpha()
pine1_img = pygame.image.load(file_path + 'img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load(file_path + 'img/Background/pine2.png').convert_alpha()

mountain_img = pygame.image.load(file_path + 'img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load(file_path + 'img/Background/sky_cloud.png').convert_alpha()
img_list = []
for tile_index in range(TILE_TYPES):
    tile_img = pygame.image.load(f'{file_path}img/Tile/{tile_index}.png')  # Load each tile image
    tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))    # Resize to the specified size
    img_list.append(tile_img)  # Add each scaled tile to the list

# Load icons with transparency
bullet_img = pygame.image.load(f'{file_path}img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load(f'{file_path}img/icons/grenade.png').convert_alpha()

# Load and assign pickup box images
health_box_img = pygame.image.load(f'{file_path}img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load(f'{file_path}img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load(f'{file_path}img/icons/grenade_box.png').convert_alpha()

# Store the pickup box images in a dictionary for easy reference
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}
#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#define font
font = pygame.font.SysFont('Futura', 30)

# Function to render and display text on the screen
def draw_text(text, font, color, x, y):
    # Render the provided text using the specified font and color, with anti-aliasing enabled for smoother edges
    text_image = font.render(text, True, color)
    # Place the rendered text on the screen at the given (x, y) coordinates
    screenset.blit(text_image, (x, y))


# Function to draw and manage the scrolling background layers
def draw_bg():
    # First, fill the entire screen with the background color (BG)
    screenset.fill(BG)
    # Get the width of the sky image to calculate how many times it needs to be repeated horizontally
    sky_layer_width = sky_img.get_width()

    # Loop through a range to draw multiple copies of background elements to create a scrolling effect
    for i in range(5):
        # Draw the sky image repeatedly, scrolling slowly at half the speed of the background scroll
        screenset.blit(sky_img, ((i * sky_layer_width) - bg_scroll * 0.5, 0))
        # Draw the mountain layer slightly faster, positioned lower on the screen
        screenset.blit(mountain_img, ((i * sky_layer_width) - bg_scroll * 0.6, screenset_HEIGHT - mountain_img.get_height() - 300))
        # Draw the first pine tree layer, further down, with a quicker scroll speed
        screenset.blit(pine1_img, ((i * sky_layer_width) - bg_scroll * 0.7, screenset_HEIGHT - pine1_img.get_height() - 150))
        # Draw the second pine tree layer at the bottom of the screen, with the fastest scroll speed
        screenset.blit(pine2_img, ((i * sky_layer_width) - bg_scroll * 0.8, screenset_HEIGHT - pine2_img.get_height()))




def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #creating empty tile list 
    data = [[-1] * COLS for _ in range(ROWS)]
    return data


class PLAYER(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed 
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0  
        self.grenades = grenades 
        self.health = 100
        self.max_health = self.health     
        self.direction = 1
        self.vel_y = 0 
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0 
        self.action = 0 
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0 
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0 
        
        # loads all images for player animations
        self.load_animations(char_type, scale)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

  def load_animations(self, character_type, scale_factor):
    """Loads the animation images for the player character."""
    # List of animation states to be loaded (e.g., Idle, Running, Jumping, Dying)
    animation_states = ['Idle', 'Run', 'Jump', 'Death']
    
    # Iterate through each animation state
    for state in animation_states:
        frame_list = []  # Temporary list to store all frames for the current animation
        # Get the number of frames by counting the images in the animation folder
        total_frames = len(os.listdir(f'{file_path}img/{character_type}/{state}'))
        
        # Load each frame of the current animation
        for frame in range(total_frames):
            # Load the image file for the current frame, ensuring it supports transparency (alpha channel)
            img = pygame.image.load(f'{file_path}img/{character_type}/{state}/{frame}.png').convert_alpha()
            # Resize the image according to the given scale factor
            img = pygame.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            frame_list.append(img)  # Add the processed frame to the temporary list
        
        # Append the full list of frames for this animation state to the player's animation list
        self.animation_list.append(frame_list)

    def update(self):
        """updates player state and check for cooldowns"""
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, move_left, move_right):
    """Manages the player’s movement and detects collisions with obstacles."""
    
    # Initialize variables for movement and screen scrolling
    screen_scroll = 0  # Tracks screen scrolling (if applicable)
    dx = 0  # Horizontal distance to move
    dy = 0  # Vertical distance to move

    # Determine movement direction based on player input
    if move_left:  # If the player is moving left
        dx = -self.speed  # Move left by subtracting the speed from the x-coordinate
        self.flip = True  # Flip the character sprite to face left
        self.direction = -1  # Set direction indicator to left (-1)
    if move_right:  # If the player is moving right
        dx = self.speed  # Move right by adding the speed to the x-coordinate
        self.flip = False  # Keep the sprite facing right
        self.direction = 1  # Set direction indicator to right (1)

    # Handle jumping: If the player presses jump and is on the ground
    if self.jump and not self.in_air:
        self.vel_y = -15  # Apply a negative vertical velocity to simulate jumping
        self.jump = False  # Reset the jump flag so the player can't jump again mid-air
        self.in_air = True  # Mark the player as airborne

    # Apply gravity: Increase the vertical velocity to simulate the effect of gravity
    self.vel_y += GRAVITY  # Continuously increase the downward velocity (falling)
    dy += min(self.vel_y, 10)  # Apply the falling movement with a maximum speed limit

    # Check for collisions with obstacles in the game world
    for obstacle in world.obstacle_list:
        # Check for horizontal collisions (moving left or right)
        if obstacle[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
            dx = 0  # Stop horizontal movement if there’s a collision
            # If the character is an enemy, reverse its direction upon hitting a wall
            if self.char_type == 'enemy':
                self.direction *= -1  # Invert the direction
                self.move_counter = 0  # Reset the movement counter for the AI

        # Check for vertical collisions (jumping or falling)
        if obstacle[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
            # If jumping and colliding with an object above
            if self.vel_y < 0:
                self.vel_y = 0  # Stop upward movement upon collision
                dy = obstacle[1].bottom - self.rect.top  # Adjust position to stop at the obstacle's bottom
            # If falling and colliding with the ground or another object below
            elif self.vel_y >= 0:
                self.vel_y = 0  # Stop downward movement upon landing
                self.in_air = False  # Mark the player as back on the ground
                dy = obstacle[1].top - self.rect.bottom  # Adjust position to rest on top of the obstacle

      


        #collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0 

        #collision with exit 
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True 

        #checking if fall off the map
        if self.rect.bottom > screenset_HEIGHT:
            self.health = 0 


        #checking if going off the edges of the screenset
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > screenset_WIDTH:
                dx = 0 
        
        #updating the rectangle position 
        self.rect.x += dx
        self.rect.y += dy

        #updating scroll based on player postion 
        if self.char_type == 'player':
            if (self.rect.right > screenset_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - screenset_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screenset_scroll = -dx 

        return screenset_scroll, level_complete

    def shoot(self):
        """shoots a bullet if the player has ammo and is not on cooldown"""
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_sound.play()

    def ai(self):
        """ enemy AI movement and shooting."""
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #0: idle
                self.idling = True
                self.idling_counter = 50

            #if the AI is near the player
            if self.vision.colliderect(player.rect):
                self.update_action(0) #0: idle
                # Ai going to shoot the player
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) #1: run 
                    self.move_counter += 1
                    #updating AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1 
                        self.move_counter *= -1
                else: 
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll 
        self.rect.x += screenset_scroll

    def update_animation(self):
        """updates the player's animation frame"""
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        """updates the player's action state"""
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        """checking if the player is alive"""
        if self.health <= 0:
            self.health = 0
            self.speed = 0 
            self.alive = False
            self.update_action(3)

    def draw(self):
        """drawing the player on the screen"""
        screenset.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Enemy(PLAYER):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__(char_type, x, y, scale, speed, ammo, grenades) 
        self.health = 50 # Enemy Health
        self.max_health = 50  # Enemy Max Health
        self.alive = True

    def check_alive(self):
        """checking if the enemy is alive"""
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False

    def update(self):
        """updating the enemy's state"""
        super().update() 
        if self.health <= 0:
            self.alive = False

    def draw(self):
        """drawing the enemy on the screen"""
        screenset.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        """handling enemy AI movement and shooting"""
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50

            #checking if the AI is near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)  # 0: idle
                #shoot
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += screenset_scroll

class Boss(PLAYER):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__(char_type, x, y, scale * 3, speed, ammo, grenades * 5) 
        self.health = 300  # Enemy Boss Health
        self.max_health = 300  # Enemy Boss Max Health
        self.alive = True

    def check_alive(self):
        """checking if the boss is alive"""
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False

    def update(self):
        """updates the boss's state"""
        super().update()  
        if self.health <= 0:
            self.alive = False

    def draw(self):
        """drawing the boss on the screen"""
        screenset.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        """boss AI movement and shooting"""
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50

            #checking if the AI is near the player
            if self.vision.colliderect(player.rect):
                self.update_action(0)  # 0: idle
                # shoot
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screenset_scroll

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        """process level data and create world objects"""
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: #create player 
                        player = PLAYER('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: #create enemies
                        enemy = Enemy('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: #create ammo box 
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: #create grenade box 
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: #create health box 
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 21:  # create the Boss
                            global boss
                            boss = Boss('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 5)
                            enemy_group.add(boss)

        return player, health_bar


    def draw(self):
        """drawing the world on the screen"""
        for tile in self.obstacle_list:
            tile[1][0] += screenset_scroll
            screenset.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """updates the decoration's position"""
        self.rect.x += screenset_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """updates the water's position"""
        self.rect.x += screenset_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        """updates the exit's positions"""
        self.rect.x += screenset_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """updates the item box's position and check for collision with the player"""
        self.rect.x += screenset_scroll
        #if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #type of box  
            if self.item_type == 'Health':              
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health               
            elif self.item_type =='Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3 
            #delete itembox
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y 
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        """showing the health bar on the screen"""
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screenset, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screenset, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screenset, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10 
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction 

    def update(self):
        """bullet's position and checking for collision with the level and enemies"""
        self.rect.x += (self.direction * self.speed) + screenset_scroll
        #if bullet goes off screenset
        if self.rect.right < 0 or self.rect.left > screenset_WIDTH:
            self.kill()
        #collisons with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        #collisions with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25               
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -15
        self.speed = 7 
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction 

    def update(self):
        """grenade's position and checking for collision with the level"""
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y 
        #collision with level
        for tile in world.obstacle_list:
            #collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #collision in the y direction
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0 
                #if below the ground (thrown up)
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                #if above the groun (falling) 
                elif self.vel_y >= 0:
                    self.vel_y = 0                  
                    dy = tile[1].top - self.rect.bottom       
        #updating grenade position 
        self.rect.x += dx + screenset_scroll
        self.rect.y += dy 
        #countdown timer untill explode
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_sound.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #damaging anyone nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    
                    

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(file_path + f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))) 
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]         
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0 

    def update(self):
        """updates the explosion's animation and position"""      
        self.rect.x += screenset_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0 
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class screensetFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0 

    def fade(self):
        """fades the screen in or out"""
        fade_complete = False 
        self.fade_counter += self.speed
        if self.direction == 1: #whole screenset fade
            pygame.draw.rect(screenset, self.colour, (0 - self.fade_counter, 0, screenset_WIDTH // 2, screenset_HEIGHT))
            pygame.draw.rect(screenset, self.colour, (screenset_WIDTH // 2 + self.fade_counter, 0, screenset_WIDTH, screenset_HEIGHT))
            pygame.draw.rect(screenset, self.colour, (0, 0 - self.fade_counter, screenset_WIDTH, screenset_HEIGHT // 2))
            pygame.draw.rect(screenset, self.colour, (0, screenset_HEIGHT // 2 + self.fade_counter, screenset_WIDTH, screenset_HEIGHT))
        if self.direction == 2: #vertical screenset down
            pygame.draw.rect(screenset, self.colour, (0, 0, screenset_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= screenset_WIDTH:
            fade_complete = True
        return fade_complete

def display_score():
    """displays score on the screen"""
    text = f'Score: {score}'
    text_width, text_height = font.size(text)
    x = screenset_WIDTH - text_width - 10
    y = 10
    draw_text(text, font, WHITE, x, y)
    pygame.display.update()

def reset_game():
    """resets the game state"""
    global score, level, start_game, boss, world, player, health_bar, shoot
    score = 0
    level = 1
    start_game = True
    boss = None
    shoot = False
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)
    with open(file_path + f'level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
    world = World()
    player, health_bar = world.process_data(world_data)
    #resets background scrolling
    bg_scroll = 0
    main_game_loop()

def game_over_screenset():
    """displays the game over screen"""
    screenset.fill(BG)
    display_score()
    restart_button = button.Button(screenset_WIDTH // 2 - 50, screenset_HEIGHT // 2 + 70, restart_img, 1)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()  #if the window closes, then exit the program completely
            if event.type == pygame.MOUSEBUTTONDOWN:
                #if the mouse clicked on restart button
                if restart_button.isOver(pygame.mouse.get_pos()):
                    waiting = False  #ends the wait and starts a new game

        # Draw buttons
        if restart_button.draw(screenset):
            reset_game()  
            waiting = False  #if the button clicked, then the new game starts
        pygame.display.update()


#screenset fades
intro_fade = screensetFade(1, WHITE, 4)
death_fade = screensetFade(2, RED, 4)

#buttons
start_button = button.Button(screenset_WIDTH // 2 - 130, screenset_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(screenset_WIDTH // 2 - 110, screenset_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(screenset_WIDTH // 2 - 100, screenset_HEIGHT // 2 - 50, restart_img, 2)

#sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#loading level data and creating world
world_data = reset_level()
with open(file_path + f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

#main game loop
run = True
def main_game_loop():
    global run, start_game
while run:

    clock.tick(FPS)

    if start_game == False:
        #shows  menu
        screenset.fill(BG) 
        #adds buttons
        if start_button.draw(screenset):
            start_game = True
            start_intro = True
        if exit_button.draw(screenset):
            run = False
    else:
        #updates the background
        draw_bg()
        #draws the world map 
        world.draw()
        #shows the player health
        health_bar.draw(player.health)
        #shows the amount of ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screenset.blit(bullet_img, (90 + (x * 10), 40))
        #shows the ammount of grenade
        draw_text('GRENADE: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screenset.blit(grenade_img, (135 + (x * 15), 60))


        player.update()
        player.draw()
    
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #updates and draws groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screenset)
        grenade_group.draw(screenset)
        explosion_group.draw(screenset)
        item_box_group.draw(screenset)
        decoration_group.draw(screenset)
        water_group.draw(screenset)
        exit_group.draw(screenset)

        #shows the intro 
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        #updates player actions 
        if player.alive:
            #shoots the bullet
            if shoot:
                player.shoot()   
            #throws the grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True                             
            if player.in_air:
                player.update_action(2) #2: jump 
            elif moving_left or moving_right:
                player.update_action(1) #1: run 
            else:
                player.update_action(0) #0: idle
            screenset_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screenset_scroll
            #if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0 
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    #loads in level data and creates the world
                    with open(file_path + f'level{level}_data.csv', newline= '') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)       
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screenset_scroll = 0 
            if death_fade.fade():
                if restart_button.draw(screenset):
                    death_fade.fade_counter = 0 
                    start_intro = True
                    bg_scroll = 0 
                    world_data = reset_level()
                    #loads in level data and creates world
                    with open(file_path + f'level{level}_data.csv', newline= '') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)       
                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
                jump_sound.play()
            if event.key == pygame.K_ESCAPE:
                run = False



        #keyboard button releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
    for enemy in enemy_group:
        if not enemy.alive:
            score += 5
            enemy_group.remove(enemy)
    for item in item_box_group:
        if pygame.sprite.collide_rect(player, item):
            score += 10  #increase the score
            item.kill()
    #screenset_WIDTH
    text = f'Score: {score}'
    text_width, text_height = font.size(text)  
    x = screenset_WIDTH - text_width - 10  
    y = 10  

    draw_text(text, font, WHITE, x, y)
    #if the boss is defeated at the appropriate place in the game's main loop

    if boss is not None and not boss.alive:
        game_over_screenset()  
        start_game = True  

    pygame.display.update()

pygame.quit()
