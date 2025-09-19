import pygame
import os
import xml.etree.ElementTree as ET #to parse the tmx file
from settings import *
from player import Player #imports the player class
from overlay import Overlay
from sprites import Generic, Wildflower, Tree
from pytmx.util_pygame import load_pygame   #to load the tmx file

# Zoom factors for screen scaling
ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface() #gets the display surface

        self.collisionSprites = pygame.sprite.Group() #group for the collision sprites
        mapPath = os.path.join(os.path.dirname(__file__), "map.xml") #path to the tmx file
        self.loadXMLCollision(mapPath) ####

        #loads the tmx file to get map dimensions before creating camera
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y)

        self.allSprites = CameraGroup(self.mapRect) #draw and update all sprites
        self.collisionSprites = pygame.sprite.Group() #group for the collision sprites
        self.interactables = []

        # Transition attributes
        self.transitioning = False #whether the player is transitioning between maps
        self.transition_timer = 0  #timer for the transition
        self.transition_duration = 0.5  # half a second before map switches
        self.transition_target = None

        self.setup() #sets up the level

    def loadXMLCollision(self, mapFile):
        """Parses an XML file to create collision sprites"""
        tree = ET.parse(mapFile) #parses the tmx file
        root = tree.getroot() #gets the root of the tmx file

        for obj in root.findall(".//object"): #for each object in the tmx file
            x = float(obj.get('x', 0))
            y = float(obj.get('y', 0))
            width = float(obj.get('width', 0))
            height = float(obj.get('height', 0))

            if width > 0 and height > 0:
                sprite = pygame.sprite.Sprite()
                sprite.rect = pygame.Rect(x * ZOOM_X, y * ZOOM_Y, width * ZOOM_X, height * ZOOM_Y)
                self.collisionSprites.add(sprite)

    def setup(self):
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file

        #fence
        for x, y, surf in tmxData.get_layer_by_name("fence").tiles():  # for each tile in the fence layer
            # Scale tile surface according to zoom
            tile_surf = pygame.transform.smoothscale(
                surf,
                (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))
            )
            # Apply scaling to position as well
            pos = (x * tmxData.tilewidth * ZOOM_X, y * tmxData.tileheight * ZOOM_Y)
            sprite = Generic(pos, tile_surf, [self.allSprites, self.collisionSprites])

        #wildflowers
        for obj in tmxData.get_layer_by_name("decor"): #for each object in the wildflower layer 
            Wildflower((obj.x, obj.y), obj.image, [self.allSprites]) #creates a wildflower object (no collision)

        #trees
        for obj in tmxData.get_layer_by_name("tree"): #object layer
            surf = None
            if hasattr(obj, "gid") and obj.gid:
                surf = tmxData.get_tile_image_by_gid(obj.gid)
            if surf:
                tile_surf = pygame.transform.smoothscale(
                    surf, 
                    (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))
                )
                tile_sprite = Generic(
                    pos=(obj.x * ZOOM_X, obj.y * ZOOM_Y),
                    surf=tile_surf,
                    groups=[self.allSprites, self.collisionSprites], # tree is collidable
                    z=LAYERS['main']
                )
                # Add interactable for choppable trees
                if getattr(obj, "choppable", False):
                    self.interactables.append({
                        "rect": tile_sprite.rect,
                        "objectType": "tree",
                        "trigger": "chop",
                        "health": getattr(obj, "health", 4),
                        "sprite": tile_sprite
                    })

        #rocks
        for obj in tmxData.get_layer_by_name("rock"): #object layer
            surf = None
            if hasattr(obj, "gid") and obj.gid:
                surf = tmxData.get_tile_image_by_gid(obj.gid)
            if surf:
                tile_surf = pygame.transform.smoothscale(
                    surf, 
                    (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))
                )
                tile_sprite = Generic(
                    pos=(obj.x * ZOOM_X, obj.y * ZOOM_Y),
                    surf=tile_surf,
                    groups=[self.allSprites, self.collisionSprites], # rock is collidable
                    z=LAYERS['main']
                )
                # Add interactable for mining rocks
                self.interactables.append({
                    "rect": tile_sprite.rect,
                    "objectType": "rock",
                    "trigger": "mine",
                    "health": 3,
                    "sprite": tile_sprite
                })

        # Player spawn
        spawnPoint = None
        for obj in tmxData.objects: #for each object in the tmx file
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y) #gets the spawn point of the player
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)  # fallback default if no spawn point found

        # Now create the player with collisionSprites
        self.player = Player(spawnPoint, self.allSprites, self.collisionSprites)
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.player.setMapBounds(pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y))

        # Overlay after player exists
        self.overlay = Overlay(self.player)

        # Load ground image and scale to match map size
        ground_surf = pygame.image.load("coursework\\gameData\\graphics\\world\\myfarm.png").convert_alpha()
        map_w_scaled = int(map_w * ZOOM_X)
        map_h_scaled = int(map_h * ZOOM_Y)
        ground_surf = pygame.transform.smoothscale(ground_surf, (map_w_scaled, map_h_scaled))

        # Create the ground layer sprite
        Generic(
            pos=(0,0),
            surf=ground_surf,
            groups=self.allSprites,
            z=LAYERS['ground']
        ) # assigning the ground layer to the farm image

        # Find doors
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "door": #if the object is a door
                door_rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, obj.width * ZOOM_X, obj.height * ZOOM_Y) #scaled door rectangle
                self.interactables.append({
                    "rect": door_rect,
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", None),
                    "spawn_point": getattr(obj, "spawnPoint", None)
                })


    def loadMap(self, map_name, spawn_at=None):
        # Calculate map dimensions and scale
        tmxData = load_pygame(f'coursework\\gameData\\graphics\\world\\{map_name}.tmx')
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        map_w_scaled = int(map_w * ZOOM_X)
        map_h_scaled = int(map_h * ZOOM_Y)

        # Re-initialize the CameraGroup with the new mapRect
        self.mapRect = pygame.Rect(0, 0, map_w_scaled, map_h_scaled)
        self.allSprites = CameraGroup(self.mapRect)
        self.allSprites.add(self.player)  # Re-add the player to the new group

        # Set the player position
        if spawn_at:
            self.player.pos = pygame.math.Vector2(spawn_at)
        else:
            self.player.pos = pygame.math.Vector2(400 * ZOOM_X, 300 * ZOOM_Y)
        self.player.rect.center = self.player.pos

        # Load and scale ground image
        ground_surf = pygame.image.load(f"coursework\\gameData\\graphics\\world\\{map_name}.png").convert_alpha()
        ground_surf = pygame.transform.smoothscale(ground_surf, (map_w_scaled, map_h_scaled))

        Generic(
            pos=(0, 0),
            surf=ground_surf,
            groups=self.allSprites,
            z=LAYERS['ground']
        )

        # Set player boundaries to the new map size
        self.player.setMapBounds(self.mapRect)
        self.allSprites.mapRect = self.mapRect

    def updateTransition(self, deltaTime):
        if self.transitioning:
            self.transition_timer += deltaTime #increment the timer
            if self.transition_timer >= self.transition_duration: # if the timer is greater than the duration
                # Load new map after transition
                self.loadMap(
                    self.transition_target["destination"],
                    spawn_at=self.transition_target.get("spawn_point", None)
                )
                self.transitioning = False
                self.transition_target = None

    def run(self, deltaTime): 
        self.updateTransition(deltaTime)  # update smooth transition
        self.allSprites.customisedDraw(self.player)
        self.allSprites.update(deltaTime) #updates all the sprites (like the player) according to the time frame
        self.overlay.display() #displays the overlay (like the tool and seed)

class CameraGroup(pygame.sprite.Group): #camera group to follow the player
    def __init__(self, mapRect):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2() #initial offset of the camera
        self.mapRect = mapRect

    def customisedDraw(self, player): #follows the player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2 #centers the player in the middle of the screen (x coordinate)
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2 #centers the player in the middle of the screen (y coordinate)

        #Clamp the offset to the map boundaries
        maxOffsetX = self.mapRect.width - SCREEN_WIDTH #maximum offset of the camera
        maxOffsetY = self.mapRect.height - SCREEN_HEIGHT #maximum offset of the camera
        self.offset.x = max(0, min(self.offset.x, maxOffsetX)) #clamps the offset to the map boundaries (x coordinate)
        self.offset.y = max(0, min(self.offset.y, maxOffsetY)) #clamps the offset to the map boundaries (y coordinate)

        #Draw all sprites in order of z
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z): 
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)
