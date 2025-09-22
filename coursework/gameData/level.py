import pygame
import os
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import *

ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface()
        
        # Load soil images with scaling
        self.untiledSoil = pygame.transform.smoothscale(
            pygame.image.load('coursework/gameData/graphics/soil/untiled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )
        self.tilledSoilImage = pygame.transform.smoothscale(
            pygame.image.load('coursework/gameData/graphics/soil/tilled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )
        
        # Sprite groups - ADD PARTICLES GROUP HERE
        self.soilTiles = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.crops = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()  # ADD THIS LINE
        self.interactables = []

        # Map transition variables
        self.mapTransitions = {}
        self.transitioning = False
        self.transitionSpeed = 500
        self.transitionAlpha = 0
        self.playerAdded = False

        # Load TMX map data
        self.tmxData = load_pygame('coursework/gameData/graphics/world/myfarm.tmx')
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, mapWidth, mapHeight)

        # Main sprite group with camera
        self.allSprites = CameraGroup(self.mapRect)
        self.setup()
        
    def tillSoil(self, player):
        tileX, tileY = self._getTileInFront(player)

        # Check if soil tile already exists at this position
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if not tile.tilled:
                    tile.till()
                return  # Tile exists, no need to create new

        # Create new soil tile and till it
        pos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
        soilTile = SoilTile(pos,
                            groups=[self.allSprites, self.soilTiles],
                            untiledImage=self.untiledSoil,
                            tilledImage=self.tilledSoilImage)
        soilTile.till()

    def waterSoil(self, targetPos):
        for tile in self.soilTiles:
            if tile.rect.collidepoint(targetPos):
                tile.water()
                break

    def chopTree(self, tileX, tileY):        
        # Convert tile coordinates to scaled screen coordinates
        targetScreenX = tileX * TILE_SIZE * ZOOM_X
        targetScreenY = tileY * TILE_SIZE * ZOOM_Y
        
        # Create collision area around target tile
        targetArea = pygame.Rect(targetScreenX, targetScreenY, TILE_SIZE * ZOOM_X, TILE_SIZE * ZOOM_Y)
                
        # Check all trees for collision with target area
        for tree in self.trees:
            if hasattr(tree, 'hitboxSprite'):
                # Check collision between tree hitbox and target area
                if tree.alive and tree.hitboxSprite.rect.colliderect(targetArea):
                    tree.chop(self.particles)  # PASS PARTICLES GROUP HERE
                    return  # Stop after finding one tree

    def isPlantable(self, tilePos):
        for crop in self.crops:
            if (crop.rect.x // TILE_SIZE, crop.rect.y // TILE_SIZE) == tilePos:
                return False
        return True

    def plantCrop(self, cropName, player):
        tileX, tileY = self._getTileInFront(player)
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if tile.tilled:
                    cropPos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
                    crop = Crop(cropPos, cropName, [self.allSprites, self.crops])
                    self.crops.add(crop)
                return

    def _getTileInFront(self, player):
        tileX = player.rect.centerx // TILE_SIZE
        tileY = player.rect.centery // TILE_SIZE

        # Extract base direction by removing tool suffixes and "Idle"
        direction = player.status
        
        # Remove "Idle" if present
        if 'Idle' in direction:
            direction = direction.replace('Idle', '')
        
        # Remove tool suffixes by checking common tool names
        tools = ['Axe', 'Water', 'Hoe']
        for tool in tools:
            if direction.endswith(tool):
                direction = direction[:-len(tool)]
                break
        
        # Adjust target tile based on direction
        if direction == 'up':
            tileY -= 1
        elif direction == 'down':
            tileY += 1
        elif direction == 'left':
            tileX -= 1
        elif direction == 'right':
            tileX += 1

        return int(tileX), int(tileY)

    def setup(self):
        # Draw ground
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        groundSurf = pygame.image.load("coursework/gameData/graphics/world/myfarm.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(mapWidth * ZOOM_X), int(mapHeight * ZOOM_Y)))
        Generic((0, 0), groundSurf, [self.allSprites], z=LAYERS['ground'])

        # Spawn obstacles
        self.spawnObstacles()

        # Find player spawn point
        spawnPoint = None
        for obj in self.tmxData.objects:
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y)
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)

        # Create player
        self.player = Player(spawnPoint, [self.allSprites], self.collisionSprites, self)
        self.player.setMapBounds(self.mapRect)

        # Create overlay
        self.overlay = Overlay(self.player)

    def spawnObstacles(self):
        # Spawn fences
        for x, y, surf in self.tmxData.get_layer_by_name("fence").tiles():
            if surf:
                pos = (x * self.tmxData.tilewidth * ZOOM_X, y * self.tmxData.tileheight * ZOOM_Y)
                Generic(pos, surf, [self.allSprites, self.collisionSprites])

        # Spawn trees
        for obj in self.tmxData.get_layer_by_name("tree"):
            tree = Tree(
                pos=(obj.x * ZOOM_X, obj.y * ZOOM_Y),
                surf=obj.image,
                groups=[self.allSprites, self.trees],
                name=obj.name,
                playerAdded=self.playerAdded
            )
            # Create hitbox for tree collision
            trunkWidth = int(tree.rect.width * 0.2)
            trunkHeight = int(tree.rect.height * 0.25)
            hitboxSprite = pygame.sprite.Sprite()
            hitboxSprite.image = pygame.Surface((1, 1))
            hitboxSprite.rect = pygame.Rect(
                tree.rect.centerx - trunkWidth // 2,
                tree.rect.bottom - trunkHeight,
                trunkWidth,
                trunkHeight
            )
            self.collisionSprites.add(hitboxSprite)
            tree.hitboxSprite = hitboxSprite

        # Spawn rocks
        for obj in self.tmxData.get_layer_by_name("rock"):
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), obj.image, [self.allSprites])
            hitboxSprite = pygame.sprite.Sprite()
            hitboxSprite.rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, 16 * ZOOM_X, 16 * ZOOM_Y)
            self.collisionSprites.add(hitboxSprite)

    def run(self, deltaTime):
        # Update all sprites first
        self.allSprites.update(deltaTime)
        self.crops.update(deltaTime)
        self.particles.update(deltaTime)  # UPDATE PARTICLES
        
        # Then draw everything
        self.allSprites.customisedDraw(self.player)
        
        # Draw particles on top
        for particle in self.particles:
            if particle.alive:
                offsetPos = particle.rect.topleft - self.allSprites.offset
                self.displaySurface.blit(particle.image, offsetPos)

        self.overlay.display()
        self.player.inventory.draw(self.displaySurface)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, mapRect):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()  # Camera offset
        self.mapRect = mapRect

    def customisedDraw(self, player):
        # Center camera on player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

        # Clamp camera to map boundaries
        maxOffsetX = self.mapRect.width - SCREEN_WIDTH
        maxOffsetY = self.mapRect.height - SCREEN_HEIGHT
        self.offset.x = max(0, min(self.offset.x, maxOffsetX))
        self.offset.y = max(0, min(self.offset.y, maxOffsetY))

        # Draw all sprites sorted by layer and y-position
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.z, sprite.rect.centery)):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)