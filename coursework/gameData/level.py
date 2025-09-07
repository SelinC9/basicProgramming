import pygame
from settings import *
from player import Player #imports the player class
from overlay import Overlay
from sprites import Generic
from pytmx.util_pygame import load_pygame   #to load the tmx file

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface() #gets the display surface
        self.all_sprites = CameraGroup() #draw and update all sprites
        self.interactables = []

        # Transition attributes
        self.transitioning = False #whether the player is transitioning between maps
        self.transition_timer = 0  #timer for the transition
        self.transition_duration = 0.5  # half a second before map switches
        self.transition_target = None

        self.setup() #sets up the level
        self.overlay = Overlay(self.player) #overlay for the player (like the time and tools)

    def setup(self):
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file

        #player
        self.player = Player((640,360), self.all_sprites) #instance of the class player

        Generic(
            pos = (0,0),
            surf = pygame.image.load("coursework\\gameData\\graphics\\world\\myfarm.png").convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
        ) # assigning the ground layer to the farm image
        #I randomly assigned a position as a tuple. It's the middle of the screen

        # Set player boundaries to the ground size
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.map_rect = pygame.Rect(0, 0, map_w, map_h)
        self.player.setMapBounds(self.map_rect)


        # Find the door object
        self.interactables = []
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "door":
                door_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.interactables.append({
                    "rect": door_rect,
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", None),
                    "spawn_point": getattr(obj, "spawnPoint", None)  # optional for door exit
                })

    def loadMap(self, map_name, spawn_at=None):
        tmxData = load_pygame(f'coursework\\gameData\\graphics\\world\\{map_name}.tmx')

        self.all_sprites.empty()  # Clear existing sprites
        self.all_sprites.add(self.player)  # Re-add the player to the new map

        # Set the player position
        if spawn_at:
            self.player.pos = pygame.math.Vector2(spawn_at)
        else:
            self.player.pos = pygame.math.Vector2(400, 300)  # fallback default
        self.player.rect.center = self.player.pos

        Generic(
            pos = (0,0),
            surf = pygame.image.load(f"coursework\\gameData\\graphics\\world\\{map_name}.png").convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
        ) # assigning the ground layer to the map image

        # Set player boundaries to the new map size
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.map_rect = pygame.Rect(0, 0, map_w, map_h)
        self.player.setMapBounds(self.map_rect)


        #loading interactables for the new map
        self.interactables = []
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "door":
                door_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.interactables.append({
                    "rect": door_rect,
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", None),
                    "spawn_point": getattr(obj, "spawnPoint", None)
                })

    def updateTransition(self, deltaTime):
        if self.transitioning:
            self.transition_timer += deltaTime
            if self.transition_timer >= self.transition_duration:
                # Load new map after transition
                self.loadMap(
                    self.transition_target["destination"],
                    spawn_at=self.transition_target.get("spawn_point", None)
                )
                self.transitioning = False
                self.transition_target = None

    def handleInteractions(self): #checks for interactions with the interactable objects
        for obj in self.interactables: #for each interactable object
            if self.player.rect.colliderect(obj["rect"]):
                if obj["trigger"] == "onPlayerTouch":
                    if obj["destination"]: #if the object has a destination
                         # Start smooth transition
                        if not self.transitioning:
                            self.transitioning = True
                            self.transition_timer = 0 #reset the timer
                            self.transition_target = {
                                "destination": obj["destination"],
                                "spawn_point": obj.get("spawn_point", None) #optional spawn point
                            }
                        break #stop after triggering transition

    def triggerAction(self, obj):
        if obj["trigger"] == "enter" and obj["objectType"] == "door":
            new_pos = (640, 100) #example position, can be set per door
            print(f"🚪 Entering door... teleporting to {new_pos}")
            self.player.rect.topleft = new_pos #teleports the player to the new position

    def run(self, deltaTime): 
        self.updateTransition(deltaTime)  # update smooth transition
        self.all_sprites.customisedDraw(self.player)
        self.all_sprites.update(deltaTime) #updates all the sprites (like the player) according to the time frame
        keys = pygame.key.get_pressed() #checks if any key is pressed
        self.handleInteractions() #checks for interactions
        self.overlay.display() #displays the overlay (like the tool and seed)


class CameraGroup(pygame.sprite.Group): #camera group to follow the player
    def __init__(self):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2() #initial offset of the camera
    
    def customisedDraw(self, player): #follows the player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2 #centers the player in the middle of the screen (x coordinate)
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2 #centers the player in the middle of the screen (y coordinate)
        
        for layer in LAYERS.values(): #for each layer in the layers dictionary
            for sprite in self.sprites():
                if sprite.z == layer:
                    offsetRect = sprite.rect.copy() #copy of the rectangle of the sprite
                    offsetRect.center -= self.offset #centers the rectangle of the sprite according to the offset
                    self.displaySurface.blit(sprite.image, offsetRect) #blits the image of the sprite to the display surface according to the offset
