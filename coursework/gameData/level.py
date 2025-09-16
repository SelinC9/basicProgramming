import pygame
from settings import *
from player import Player #imports the player class
from overlay import Overlay
from sprites import Generic
from pytmx.util_pygame import load_pygame   #to load the tmx file

# Zoom factors for screen scaling
ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface() #gets the display surface

        #loads the tmx file to get map dimensions before creating camera
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y)

        self.allSprites = CameraGroup(self.mapRect) #draw and update all sprites
        self.interactables = []

        # Transition attributes
        self.transitioning = False #whether the player is transitioning between maps
        self.transition_timer = 0  #timer for the transition
        self.transition_duration = 0.5  # half a second before map switches
        self.transition_target = None

        self.setup() #sets up the level

    def setup(self):
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file

        # Load ground image and scale to match map size
        ground_surf = pygame.image.load("coursework\\gameData\\graphics\\world\\myfarm.png").convert_alpha()
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        map_w_scaled = int(map_w * ZOOM_X)
        map_h_scaled = int(map_h * ZOOM_Y)

        # Scale the ground surface to match the map size
        ground_surf = pygame.transform.smoothscale(ground_surf, (map_w_scaled, map_h_scaled))

        # Create the ground layer sprite
        Generic(
            pos=(0,0),
            surf=ground_surf,
            groups=self.allSprites,
            z=LAYERS['ground']
        ) # assigning the ground layer to the farm image

        # Player spawn
        spawnPoint = None
        for obj in tmxData.objects: #for each object in the tmx file
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y) #gets the spawn point of the player
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)  # fallback default if no spawn point found

        # Now create the player
        self.player = Player(spawnPoint, self.allSprites)
        self.player.setMapBounds(pygame.Rect(0, 0, map_w_scaled, map_h_scaled))

        # Overlay after player exists
        self.overlay = Overlay(self.player)

        # Load other layers (trees, rocks, objects)
        for layerName in ["lake object", "tree", "decor","rock","interactables","house","barn"]: #for each layer in the tmx file
            try:
                layer = tmxData.get_layer_by_name(layerName) #gets the layer by name
            except ValueError:
                continue  # Skip if the layer doesn't exist

            if hasattr(layer, "tiles"):  # Tile layer
                for x, y, gid in layer.tiles(): #for each tile in the layer
                    surf = tmxData.get_tile_image_by_gid(gid)
                    if surf is None:
                        continue
                    # Scale each tile surface proportionally
                    tile_surf = pygame.transform.smoothscale(surf, (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y)))
                    tilePos = (x * tmxData.tilewidth * ZOOM_X, y * tmxData.tileheight * ZOOM_Y)
                    tileSprite = Generic(
                        pos = tilePos, #position of the tile
                        surf = tile_surf, #surface of the tile
                        groups = self.allSprites, #adds the tile to the allSprites group
                        z = LAYERS.get(layerName.lower(),LAYERS['main']) #sets the layer of the tile to objects
                    )

                    # Add tree interactables from Tiled properties
                    props = layer.properties_at(x, y)
                    if layerName == "tree" and props.get("choppable", False):
                        self.interactables.append({
                            "rect": tileSprite.rect,
                            "objectType": "tree",
                            "trigger": "chop",
                            "health": props.get("health", 4),
                            "sprite": tileSprite
                        })

                    # Add rocks as interactables with default properties
                    if layerName == "rock":
                        self.interactables.append({
                            "rect": tileSprite.rect,
                            "objectType": "rock",
                            "trigger": "mine",
                            "health": 3,
                            "sprite": tileSprite
                        })

            elif hasattr(layer, "objects"):  # Object layer
                for obj in layer:  # for each object in the layer
                    surf = None
                    if hasattr(obj, "gid") and obj.gid:  # If the object has a tile image
                        surf = tmxData.get_tile_image_by_gid(obj.gid)
                    if surf:
                        # Scale object surface if needed
                        tile_surf = pygame.transform.smoothscale(surf, (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))) #scales the tile surface
                        tileSprite = Generic(
                            pos=(obj.x * ZOOM_X, obj.y * ZOOM_Y),
                            surf=tile_surf,
                            groups=self.allSprites,
                            z=LAYERS.get(layerName.lower(), LAYERS['main'])
                        )
                        if layerName == "tree":
                            self.interactables.append({
                                "rect": tileSprite.rect,
                                "objectType": "tree",
                                "trigger": "chop",
                                "health": getattr(obj, "health", 4),
                                "sprite": tileSprite
                            })
                        if layerName == "rock":
                            self.interactables.append({
                                "rect": tileSprite.rect,
                                "objectType": "rock",
                                "trigger": "mine",
                                "health": 3,
                                "sprite": tileSprite
                            })

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
        tmxData = load_pygame(f'coursework\\gameData\\graphics\\world\\{map_name}.tmx')

        self.allSprites.empty()  # Clear existing sprites
        self.allSprites.add(self.player)  # Re-add the player to the new map

        # Set the player position
        if spawn_at:
            self.player.pos = pygame.math.Vector2(spawn_at) #set player position to the spawn point
        else:
            self.player.pos = pygame.math.Vector2(400 * ZOOM_X, 300 * ZOOM_Y)  # fallback default
        self.player.rect.center = self.player.pos #update the rectangle of the player

        # Load and scale ground image
        ground_surf = pygame.image.load(f"coursework\\gameData\\graphics\\world\\{map_name}.png").convert_alpha() #loads the ground image
        map_w = tmxData.width * tmxData.tilewidth #width of the map
        map_h = tmxData.height * tmxData.tileheight #height of the map
        map_w_scaled = int(map_w * ZOOM_X) #scaled width of the map
        map_h_scaled = int(map_h * ZOOM_Y) #scaled height of the map
        ground_surf = pygame.transform.smoothscale(ground_surf, (map_w_scaled, map_h_scaled)) #scales the ground surface to match the map size

        Generic(
            pos=(0,0),
            surf=ground_surf,
            groups=self.allSprites,
            z=LAYERS['ground']
        ) # assigning the ground layer to the map image

        # Set player boundaries to the new map size
        self.mapRect = pygame.Rect(0, 0, map_w_scaled, map_h_scaled)
        self.player.setMapBounds(self.mapRect)

        # Update camera group with new map rect
        self.allSprites.mapRect = self.mapRect

        # Load interactables for the new map
        self.interactables = []
        for layerName in ["tree","rock"]: #only loading tree and rock layers for interactables
            try:
                layer = tmxData.get_layer_by_name(layerName) #gets the layer by name
            except ValueError:
                continue
            for x, y, gid in layer.tiles():
                surf = tmxData.get_tile_image_by_gid(gid) #gets the tile image by gid
                if surf is None:
                    continue
                tile_surf = pygame.transform.smoothscale(surf, (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))) #scales the tile surface
                tilePos = (x * tmxData.tilewidth * ZOOM_X, y * tmxData.tileheight * ZOOM_Y) #position of the tile
                tileSprite = Generic(
                    pos = tilePos,
                    surf = tile_surf,
                    groups = self.allSprites,
                    z = LAYERS.get(layerName.lower(),LAYERS['main']) #sets the layer of the tile
                )

                if layerName == "tree": #tree properties from Tiled
                    props = layer.properties_at(x, y)
                    if props.get("choppable", False):
                        self.interactables.append({
                            "rect": tileSprite.rect,
                            "objectType": "tree",
                            "trigger": "chop",
                            "health": props.get("health", 4),
                            "sprite": tileSprite
                        })
                if layerName == "rock": #default rock properties
                    self.interactables.append({
                        "rect": tileSprite.rect,
                        "objectType": "rock",
                        "trigger": "mine",
                        "health": 3,
                        "sprite": tileSprite
                    })

        # Doors
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "door":
                door_rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, obj.width * ZOOM_X, obj.height * ZOOM_Y) #scaled door rectangle
                self.interactables.append({ #door data
                    "rect": door_rect, 
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", None),
                    "spawn_point": getattr(obj, "spawnPoint", None)
                })

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
        self.allSprites.customisedDraw(self.player)
        self.allSprites.update(deltaTime) #updates all the sprites (like the player) according to the time frame
        keys = pygame.key.get_pressed() #checks if any key is pressed
        self.handleInteractions() #checks for interactions
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

        for layer in LAYERS.values(): #for each layer in the layers dictionary
            for sprite in self.sprites():
                if sprite.z == layer:
                    offsetRect = sprite.rect.copy() #copy of the rectangle of the sprite
                    offsetRect.center -= self.offset #centers the rectangle of the sprite according to the offset
                    scaledImage = pygame.transform.smoothscale(sprite.image, 
                                    (int(sprite.rect.width * ZOOM_X), int(sprite.rect.height * ZOOM_Y))) #scales the image of the sprite according to the zoom factors
                    scaled_rect = scaledImage.get_rect(center=offsetRect.center) #gets the rectangle of the scaled image
                    self.displaySurface.blit(scaledImage, scaled_rect) #blits the scaled image to the display surface