import pygame
import os
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Wildflower, Tree, Particle

# Zoom factors for screen scaling
ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface() #gets the display surface
        self.soilTiles = pygame.sprite.Group() #group for the soil tiles
        self.trees = pygame.sprite.Group() #group for the trees
        self.collisionSprites = pygame.sprite.Group() #group for the collision sprites
        self.interactables = []  # group for interactable objects
        self.particles = pygame.sprite.Group()  # group for leaf particles

        # Transition attributes
        self.mapTransitions = {} #dictionary to store the map transitions
        self.transitioning = False #whether the player is transitioning between maps
        self.transitionSpeed = 500 #speed of the transition
        self.transitionAlpha = 0 #alpha value for the transition

        #loads the tmx file to get map dimensions before creating camera
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y)

        self.allSprites = CameraGroup(self.mapRect) #draw and update all sprites

        self.setup() #sets up the level

    def tillSoil(self, targetPos): #tills the soil at the target position
        for tile in self.soilTiles: #for each soil tile
            if tile.rect.collidepoint(targetPos): #if the tile collides with the target position
                tile.till() #tills the soil
                break #stop after tilling one tile

    def chopTree(self, targetPos): #chops the tree at the target position
        for tree in self.trees: #for each tree
            if tree.rect.collidepoint(targetPos): #if the tree collides with the target position
                tree.chop(self.particles) #chops the tree and spawn leaves
                break #stop after chopping one tree

    def waterSoil(self, targetPos): #waters the soil at the target position
        for tile in self.soilTiles: #for each soil tile
            if tile.rect.collidepoint(targetPos): #if the tile collides with the target position
                tile.water() #waters the soil
                break #stop after watering one tile

    def setup(self):
        tmxData = load_pygame('coursework\\gameData\\graphics\\world\\myfarm.tmx') #loads the tmx file

        #fence
        for x, y, surf in tmxData.get_layer_by_name("fence").tiles():  # for each tile in the fence layer
            tile_surf = pygame.transform.smoothscale(
                surf,
                (int(tmxData.tilewidth * ZOOM_X), int(tmxData.tileheight * ZOOM_Y))
            )
            pos = (x * tmxData.tilewidth * ZOOM_X, y * tmxData.tileheight * ZOOM_Y)
            Generic(pos, tile_surf, [self.allSprites, self.collisionSprites])

        #wildflowers
        for obj in tmxData.get_layer_by_name("decor"): #for each object in the wildflower layer 
            Wildflower((obj.x, obj.y), obj.image, [self.allSprites]) #creates a wildflower object (no collision)

        # Player spawn
        spawnPoint = None
        for obj in tmxData.objects: #for each object in the tmx file
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y) #gets the spawn point of the player
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)  # fallback default if no spawn point found

        # Create the player with collisionSprites
        self.player = Player(spawnPoint, self.allSprites, self.collisionSprites, self)
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.player.setMapBounds(pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y))

        # Overlay after player exists
        self.overlay = Overlay(self.player)

        #trees
        for obj in tmxData.get_layer_by_name("tree"): #for each object in the tree layer
            tree = Tree(
                pos=(obj.x, obj.y), 
                surf=obj.image, 
                groups=[self.allSprites, self.trees, self.collisionSprites],  # include collision
                name=obj.name,
                playerAdded=self.playerAdded
            ) #creates a tree object
            self.trees.add(tree)

            # create a smaller collision hitbox for the tree
            hitboxSprite = pygame.sprite.Sprite()
            hitboxSprite.hitbox = pygame.Rect(0, 0, 12 * ZOOM_X, 16 * ZOOM_Y)
            hitboxSprite.hitbox.midbottom = (obj.x * ZOOM_X + tmxData.tilewidth * ZOOM_X / 2,
                                            obj.y * ZOOM_Y + tmxData.tileheight * ZOOM_Y)

            if tree.alive:  # only add hitbox if the tree is alive
                self.collisionSprites.add(hitboxSprite)

            tree.hitboxSprite = hitboxSprite  # link the hitbox to the tree for later use


        #rocks
        for obj in tmxData.get_layer_by_name("rock"):  # object layer
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), obj.image, [self.allSprites])
            hitboxSprite = pygame.sprite.Sprite()
            hitboxSprite.hitbox = pygame.Rect(0, 0, 16 * ZOOM_X, 16 * ZOOM_Y)
            hitboxSprite.hitbox.midbottom = (obj.x * ZOOM_X + tmxData.tilewidth * ZOOM_X / 2,
                                             obj.y * ZOOM_Y + tmxData.tileheight * ZOOM_Y)
            self.collisionSprites.add(hitboxSprite)

        #interactables (doors, etc.)
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "interactable":
                rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, obj.width * ZOOM_X, obj.height * ZOOM_Y)
                self.interactables.append({
                    "rect": rect,
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", "onPlayerTouch"),
                    "spawn_point": getattr(obj, "spawnPoint", None)
                })

        #ground layer
        groundSurf = pygame.image.load("coursework\\gameData\\graphics\\world\\myfarm.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(map_w * ZOOM_X), int(map_h * ZOOM_Y)))
        Generic((0, 0), groundSurf, self.allSprites, z=LAYERS['ground'])

    def loadMap(self, map_name, spawn_at=None):
        # Reload a new map (like setup, simplified)
        tmxData = load_pygame(f'coursework\\gameData\\graphics\\world\\{map_name}.tmx')
        map_w = tmxData.width * tmxData.tilewidth
        map_h = tmxData.height * tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, map_w * ZOOM_X, map_h * ZOOM_Y)
        self.allSprites = CameraGroup(self.mapRect)
        self.allSprites.add(self.player)

        # Set player position
        if spawn_at:
            self.player.pos = pygame.math.Vector2(spawn_at)
        else:
            self.player.pos = pygame.math.Vector2(400 * ZOOM_X, 300 * ZOOM_Y)
        self.player.rect.center = self.player.pos
        self.player.setMapBounds(self.mapRect)

        # Load ground
        groundSurf = pygame.image.load(f"coursework\\gameData\\graphics\\world\\barnInterior.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(map_w * ZOOM_X), int(map_h * ZOOM_Y)))
        Generic((0, 0), groundSurf, self.allSprites, z=LAYERS['ground'])

        self.interactables = []
        # reload interactables
        for obj in tmxData.objects:
            if getattr(obj, "objectType", None) == "interactable":
                rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, obj.width * ZOOM_X, obj.height * ZOOM_Y)
                self.interactables.append({
                    "rect": rect,
                    "destination": getattr(obj, "destination", None),
                    "trigger": getattr(obj, "trigger", "onPlayerTouch"),
                    "spawn_point": getattr(obj, "spawnPoint", None)
                })

    def playerAdded(self, item):
        # tries to add an item to the player's inventory
        if self.player.addItem(item):  # checks inventory and adds
            print(f"{item} added to inventory")  # successful addition, do anything else if needed
        else:
            print("Inventory is full")  # could trigger UI notification


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
                        if not self.transitioning:
                            self.transitioning = True
                            self.transition_timer = 0 #reset the timer
                            self.transition_target = {
                                "destination": obj["destination"],
                                "spawn_point": obj.get("spawn_point", None) #optional spawn point
                            }
                        break #stop after triggering transition

    def run(self, deltaTime): 
        self.updateTransition(deltaTime)  # update smooth transition
        self.allSprites.customisedDraw(self.player)
        self.allSprites.update(deltaTime) #updates all the sprites (like the player) according to the time frame

        # update and draw leaf particles
        # update and draw leaf particles
        self.particles.update(deltaTime)
        for particle in self.particles:
            offsetRect = particle.rect.copy()
            offsetRect.center -= self.allSprites.offset  # apply camera offset
            scaledImage = pygame.transform.smoothscale(
                particle.image,
                (int(particle.rect.width * ZOOM_X), int(particle.rect.height * ZOOM_Y))
            )
            scaled_rect = scaledImage.get_rect(center=offsetRect.center)
            self.displaySurface.blit(scaledImage, scaled_rect)


class CameraGroup(pygame.sprite.Group): #camera group to follow the player
    def __init__(self, mapRect):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2() #initial offset of the camera
        self.mapRect = mapRect

    def customisedDraw(self, player):
        # Center the camera on the player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

        # Clamp the camera offset so it doesn't go outside the map
        maxOffsetX = self.mapRect.width - SCREEN_WIDTH
        maxOffsetY = self.mapRect.height - SCREEN_HEIGHT
        self.offset.x = max(0, min(self.offset.x, maxOffsetX))
        self.offset.y = max(0, min(self.offset.y, maxOffsetY))

        # Draw sprites layer by layer
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):  # Sort sprites by Y position
                if getattr(sprite, "z", LAYERS['main']) == layer:  # Only draw sprites in the current layer
                    # Offset sprite rect for camera position
                    offsetRect = sprite.rect.copy()
                    offsetRect.center -= self.offset

                    # Scale the sprite image according to zoom
                    scaledImage = pygame.transform.smoothscale(
                        sprite.image,
                        (int(sprite.rect.width * ZOOM_X), int(sprite.rect.height * ZOOM_Y))
                    )
                    scaled_rect = scaledImage.get_rect(center=offsetRect.center)

                    # Draw the sprite
                    self.displaySurface.blit(scaledImage, scaled_rect)

