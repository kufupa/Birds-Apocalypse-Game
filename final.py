import pygame
import random
import os
import csv
import operator

# pygame.init() # initiliase all pygame modules
pygame.font.init()  # for displaying text

# name of window
pygame.display.set_caption("Bird\'s Apolcoypse v1")

# define window constants
FPS = 144
WIDTH = 1280
HEIGHT = 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

#load images
# background
BG_SKY_IMG = pygame.image.load(os.path.join("assets", "bg_sky.jpg")).convert()

# bird
BIRD_IMG = pygame.image.load(os.path.join("assets", "bird.png")).convert_alpha() # load bird image
BIRD_SIZE = (40, 40) # tuple for image size of bird
BIRD_IMAGE = pygame.transform.flip(
    pygame.transform.scale(BIRD_IMG, BIRD_SIZE), True, False
).convert_alpha() # transform image to what we want - convert alpha allows for transparency and makes it more optimised according to stackoverflow thread :)

# buttons
#start button
START_BUTTON_SCALE =  1
START_BUTTON_IMG = pygame.image.load(os.path.join("assets", "start_btn.png"))

START_BUTTON_IMG_WIDTH = START_BUTTON_IMG.get_width()
START_BUTTON_IMG_HEIGHT= START_BUTTON_IMG.get_height()

START_BUTTON_IMAGE = pygame.transform.scale(START_BUTTON_IMG, (int(START_BUTTON_IMG_WIDTH * START_BUTTON_SCALE), int(START_BUTTON_IMG_HEIGHT * START_BUTTON_SCALE)))

# exit button
EXIT_BUTTON_SCALE =  1
EXIT_BUTTON_IMG = pygame.image.load(os.path.join("assets", "exit_btn.png"))

EXIT_BUTTON_IMG_WIDTH = START_BUTTON_IMG.get_width()
EXIT_BUTTON_IMG_HEIGHT= START_BUTTON_IMG.get_height()

EXIT_BUTTON_IMAGE = pygame.transform.scale(EXIT_BUTTON_IMG, (int(EXIT_BUTTON_IMG_WIDTH * EXIT_BUTTON_SCALE), int(EXIT_BUTTON_IMG_HEIGHT * EXIT_BUTTON_SCALE)))



# define game constants

BIRD_FREQUENCY = 750 # time between bird spawns in milliseconds

PLATFORM_WIDTH, PLATFORM_HEIGHT = 120, 20
PLATFORM_MID_X = WIDTH // 2 
PLATFORM_MID_Y = HEIGHT // 2 + PLATFORM_HEIGHT
platform_coords = ( (PLATFORM_MID_X-150, PLATFORM_MID_Y-200), (PLATFORM_MID_X+150, PLATFORM_MID_Y-200), (PLATFORM_MID_X-300, PLATFORM_MID_Y), (PLATFORM_MID_X, PLATFORM_MID_Y), (PLATFORM_MID_X+300, PLATFORM_MID_Y), (PLATFORM_MID_X-150, PLATFORM_MID_Y+200), (PLATFORM_MID_X+150, PLATFORM_MID_Y+200) )


#define variables
bird_deaths_score = 0

# define pygame events
you_lost_event = pygame.USEREVENT + 1
# pygame.event.post(pygame.event.Event(you_lost_event)) - to announce event - implemented in player class update when checking if hit ground

#define groups
platform_group = pygame.sprite.Group() # 
bird_group = pygame.sprite.Group() # Bird group to keep manage all birds that have been spawned
player_group = pygame.sprite.Group()

#define fonts
SCORE_FONT = pygame.font.SysFont("comicsans", 40)
YOU_LOST_FONT = pygame.font.SysFont("comicsans", 150)

#define colours
WHITE_RGB = (255, 255, 255)
BLACK_RGB = (0, 0, 0) # pygame.draw.rect(SCREEN, BLACK_RGB, platform)
RED_RGB = (255, 0, 0)
PINK_RGB = (255, 0, 255)
BABY_BLUE_RGB = (202, 228, 241)

START_BG_RGB = BABY_BLUE_RGB
YOU_LOST_RGB = PINK_RGB
SCORE_FONT_RGB = RED_RGB

# define sounds
# DEATH_SOUND = pygame.mixer.Sound(os.path.join())
# JUMP_SOUND = pygame.mixer.Sound(os.path.join()) 

#button class
class Button():

  def __init__(self, x, y, image):
    self.image = image
    self.rect = image.get_rect()
    self.rect.topleft = (x, y)
    self.clicked = False
    # self.activated = False

  def draw(self, pos):
		#get mouse position
    self.pos = pos # pygame.mouse.get_pos()

		#check mouseover and clicked conditions
    if self.rect.collidepoint(self.pos) and pygame.mouse.get_pressed()[0] == 1: #  and self.clicked == False - old code, no longer needed as check is conducted in draw loop
      self.clicked = True

    # if pygame.mouse.get_pressed()[0] == 0:
    #   self.clicked = False # if button not currently pressed set to false

		#draw button on screen
    SCREEN.blit(self.image, (self.rect.x, self.rect.y))


def gen_start_buttons():
  x_gap = 40 # for start button take awap x_gap to move it left i.e away from centre, and vice versa for exit button
  start_button = Button(int(WIDTH // 2 - START_BUTTON_IMAGE.get_width() - x_gap), (HEIGHT // 2 - START_BUTTON_IMAGE.get_height()//2), START_BUTTON_IMAGE)

  exit_button = Button(int(WIDTH // 2 + x_gap), (HEIGHT // 2 - EXIT_BUTTON_IMAGE.get_height()//2), EXIT_BUTTON_IMAGE) # old code for x parameter: + EXIT_BUTTON_IMAGE.get_width()
  
  reset_button = Button(int(WIDTH // 2- EXIT_BUTTON_IMAGE.get_width()// 2), (HEIGHT // 2- EXIT_BUTTON_IMAGE.get_height()//2), EXIT_BUTTON_IMAGE) # old code for x parameter: + EXIT_BUTTON_IMAGE.get_width()

  
  return start_button, exit_button, reset_button

def draw_buttons(start_button, exit_button):
  if start_button.clicked or exit_button.clicked:
    pass # dont draw them
  # otherwise draw them
  else:
    SCREEN.fill(START_BG_RGB) # background
    pos = pygame.mouse.get_pos()
    start_button.draw(pos)
    exit_button.draw(pos)

def has_game_started(start_button):
  return start_button.clicked # if start button has been clicked

def has_game_ended(exit_button):
  return exit_button.clicked




# Platform section
class platform(pygame.sprite.Sprite):

  def __init__( self, x, y ):
    pygame.sprite.Sprite.__init__(self) 
    self.rect = pygame.Rect(x - PLATFORM_WIDTH // 2 , y, PLATFORM_WIDTH, PLATFORM_HEIGHT) # x,y, width, height
    self.rect.center = (x, y)

  def update(self):
    pygame.draw.rect(SCREEN, BLACK_RGB, self.rect)
  

def generate_platforms():
  for i in platform_coords: # iterate through all coordinates in platform coords
    plat = platform(i[0], i[1]) # create platform object with coords currently being iterated through
    platform_group.add(plat) # add newly generated platform to group
  

def draw_platforms():
  platform_group.update()


# BIRD SECTION
# OOP for properties randomly generated birds
class bird(pygame.sprite.Sprite):
  
  def __init__(self):
    pygame.sprite.Sprite.__init__(self) # allows to use pygame's sprite classes methods i.e blit

    self.image = BIRD_IMAGE

    self.x_vel = 8 # speed bird can move horizontally

    self.rect = self.image.get_rect()
    self.x = -self.rect.width # spawns off the left side of screen
    self.y = random.randint(5, (HEIGHT - self.rect.height )) # pick random y coordinate
    self.rect.center = (self.x , self.y)
    

  def update(self):
    self.rect.x += self.x_vel # Travel from left to right
    if self.rect.x > WIDTH - 50: # if off of screen, delete
      self.kill()
      update_score()
      

def generate_birds(last_bird_time):

  time_now = pygame.time.get_ticks() # obtains current time
  if (time_now - last_bird_time) >  BIRD_FREQUENCY: #checks if it is time to spawn the next bird
    bird_generated = bird()
    bird_group.add(bird_generated)#adds the generated bird to the group
    return time_now
  return last_bird_time

def draw_birds():
  bird_group.update() # update them i.e allow them to move
  bird_group.draw(SCREEN)

# Player section
# OOP for actual player object
class player(pygame.sprite.Sprite):

  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)

    PLAYER_SIZE = (40, 40)
    PLAYER_IMG = pygame.image.load(os.path.join("assets", "player.png")).convert_alpha() # ADD IMAGE
    self.image = pygame.transform.rotate(
        pygame.transform.scale(PLAYER_IMG, PLAYER_SIZE), 0
    )

    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    
    self.x_vel = 7

    self.y_vel = 0
    self.UP_pressed = False

    # self.in_air = False
    self.jump = 0

  def update(self, keys_pressed): # override update function built in with pygame "Sprite" class
      # gravity's affect on players y position
      self.y_vel += 0.25 # accelerates downwards
      # displace bird by current velocity
      if self.rect.bottom < (HEIGHT - 10): # if its above ground
        
          if self.rect.top > 0: # and if its below top
            self.rect.y += int(self.y_vel) # only then move it - so it cant go below ground or above top
          else:
            self.rect.top = 1 # make sure it doesnt go above top of screen
            self.y_vel = 0 # set velocity to zero so it doesnt continue moving up
          
          if self.y_vel > 4: # terminal velocity downwards
              self.y_vel = 4
          if self.y_vel < -10: # terminal velocity upwards
              self.y_vel = -10
              
          # jump
          if keys_pressed[pygame.K_UP]:
              if (self.UP_pressed == False) and (self.jump < 2):
                  self.jump += 1
                  self.UP_pressed = True
                  self.y_vel -= 10
          else:
              self.UP_pressed = False # For not letting them hold the button

          # horizontal movement
            # arrow keys used to let player move
          if (
            keys_pressed[pygame.K_LEFT] and ((self.rect.x - self.x_vel) > 0 )
          ):  # left, decreasing x axis
            self.rect.x -= self.x_vel
          if (
            keys_pressed[pygame.K_RIGHT] and (self.rect.x + self.x_vel + self.rect.width < WIDTH)
          ):  # right, increasing x axis
            self.rect.x += self.x_vel
      else:
        pygame.event.post(pygame.event.Event(you_lost_event))

      # PLATFORM - PLAYER INTERACTIONS
      # check for collision with platform
      for plat in platform_group:
        #check collision in the x direction
        if plat.rect.colliderect(self.rect.x + self.x_vel, self.rect.y, self.rect.width, self.rect.height):
          self.dx = 0
        #check for collision in the y direction
        if plat.rect.colliderect(self.rect.x, self.rect.y + self.y_vel, self.rect.width, self.rect.height):
          #check if below the ground, i.e. jumping
          if self.y_vel < 0:
            self.y_vel = 0
            self.rect.y += plat.rect.bottom - self.rect.top
          #check if above the ground, i.e. falling
          elif self.y_vel >= 0:
            self.y_vel = 0
            # self.in_air = False # notify its on a platform - for jump condition
            self.jump = 0 # reset jump counter
            self.rect.y += plat.rect.top - self.rect.bottom
        # else:
        #   self.in_air = True # notify its not on a platform - for jump condition
  
  def reset(self, x, y):

    self.rect.center = (x, y)
    
    self.x_vel = 7

    self.y_vel = 0
    self.UP_pressed = False

    # self.in_air = False
    self.jump = 0


def draw_background():
  SCREEN.blit(BG_SKY_IMG, (0, 0))

def update_score():
    global bird_deaths_score
    bird_deaths_score += 1

def draw_score(): # this constantly draws score
    draw_text = SCORE_FONT.render(f"Score = {bird_deaths_score}", 1, SCORE_FONT_RGB)
    SCREEN.blit(
        draw_text,
        (
            (WIDTH - draw_text.get_width()), # To ensure text is in top right
            0, # y == 0 since top
        ),
    )    


# Text for if you lost - died in void
def draw_you_lost():

    draw_text = YOU_LOST_FONT.render("You lost!", 1, YOU_LOST_RGB)
    SCREEN.blit(
        draw_text,
        (
            (WIDTH / 2 - draw_text.get_width() // 2), # To ensure text is in centre
            (HEIGHT / 2 - draw_text.get_height() // 2),
        ),
    )
    pygame.display.update()
    pygame.time.delay(1000)
    

def read_csv():
  # Read the csv.
  top_scores = [] # list for the 5 in order
  with open('leaderboard.csv', 'r', newline='') as file:
      score_list = list(csv.reader(file, delimiter=","))
      sort=sorted(score_list,key=operator.itemgetter(0),reverse=True) # sort them in descending order of score
      for i in (0, len (score_list)):
          for row in sort:
              if i>=5 or i == len (score_list):
                  break
              else:
                top_scores.append(str(int(row[0])) + " " + row[1])
                i = i+1
  return top_scores
  

def leaderboard(player_name, bird_deaths_score):
  with open('leaderboard.csv', 'a', newline='') as file:
    line = csv.writer(file)
    line.writerow(((str(bird_deaths_score).rjust(4, '0')), player_name))

  # # Read the csv.
  # with open('leaderboard.csv', 'r', newline='') as file:
  #     score_list = list(csv.reader(file, delimiter=","))
  #     sort=sorted(score_list,key=operator.itemgetter(0),reverse=True)
  #     for i in (0, len (score_list)):
  #         for row in sort:
  #             if i>=5 or i == len (score_list):
  #                 break
  #             else:
  #               print(str(int(row[0])) + " " + row[1])
  #               i = i+1

def check_reset(reset_button):
  pos = pygame.mouse.get_pos()
  reset_button.draw(pos)
  pygame.display.update()
  return not(reset_button.clicked)

def draw_everything():
  draw_background()
  draw_platforms()

  draw_birds()
  player_group.draw(SCREEN)

  draw_score()

def reset_game():

  global bird_deaths_score
  bird_deaths_score = 0

  # update this last to avoid drawing them ontop
  global player_group
  for i in player_group:
    i.reset(WIDTH // 2, HEIGHT // 2)

  global bird_group
  bird_group.empty()

def get_username(player_name):
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_BACKSPACE: # if they want to delete a character
        player_name = player_name[:-1] # remove singular digit
      else:
        player_name += event.unicode
  return "Dave"
  return player_name
  

def draw_top_players():
  SCREEN.fill((255,0,0)) # full red screen
  top_players = read_csv()
  spacing = 20
  height = 0

  for i in top_players:
    score = i[:i.find(" ")] # number is before space
    name = i[i.find(" ")+1:] # name is after space
    name_text = YOU_LOST_FONT.render(name, 1, (0,0,255))
    score_text = YOU_LOST_FONT.render(score, 1, (0,0,255))
    # print(name_text.get_height())
    dHeight = name_text.get_height() + spacing # 
    # print(height)
    height += dHeight
    SCREEN.blit(
      name_text,
      (
          spacing, # To ensure text is in top right
          height, # y == 0 since top
      ),
    ) 
    SCREEN.blit(
      score_text,
      (
          WIDTH - spacing - score_text.get_width(), # To ensure text is in top right
          height, # y == 0 since top
      ),
    )

    pygame.display.update()
    pygame.time.delay(200)
  pygame.time.delay(2000)  


# main game loop
def game():
  player_name = "Dave" # empty variable that will later ask for input
  # clock variable for FPS cap
  clock = pygame.time.Clock()

  # declare you_lost variable
  you_lost = False  

  # create player instance
  player_group.add(player(WIDTH // 2, HEIGHT // 2)) # group is declared at top

  # generate platforms ONCE - since they are static
  generate_platforms() # generate platforms

  start_button, exit_button, reset_button = gen_start_buttons()
  
  # main run loop
  run = True
  while run: 
    clock.tick(FPS) # FPS cap

    for event in pygame.event.get():
      # quit game
      if event.type == pygame.QUIT:
        run = False
      elif event.type == you_lost_event:
        you_lost = True
        draw_you_lost()
        # leaderboard(player_name, bird_deaths_score) # save 
        draw_everything()


    if you_lost == True:
      player_name = get_username(player_name)
      you_lost = check_reset(reset_button)
      if you_lost == False:
        reset_game()
        last_bird_time = pygame.time.get_ticks()  # assigning it to lastest time game hasnt Restarted so birds dont instantly spawn
        reset_button.clicked = False # reset for next time player loses
        leaderboard(player_name, bird_deaths_score) # save username name and score
        player_name = "" # empty variable that will later ask for input
        draw_top_players()
        pygame.display.update()



    elif has_game_started(start_button) == False: # if game hasnt started
      draw_buttons(start_button, exit_button)

      # Declare and assign bird time - to check if its time to spawn birds
      if has_game_ended(exit_button):
        run = False
      last_bird_time = pygame.time.get_ticks()  # assigning it to lastest time game hasnt started so birds dont instantly spawn

    else: #
    # Draw everything
      
      draw_everything()

      # Generate new things
      last_bird_time = generate_birds(last_bird_time) # generate birds and update variable for last bird spawn

      #look for collision - Birds And Player
      if pygame.sprite.groupcollide(bird_group, player_group, False, False):
        pygame.event.post(pygame.event.Event(you_lost_event))

      # Handle player movement
      keys_pressed = pygame.key.get_pressed()
      player_group.update(keys_pressed)

    pygame.display.update()


  # NO LONGER IN WHILE run LOOP CODE:
  
  pygame.quit() # After exisiting run loop

if __name__ == "__main__":
  game()

