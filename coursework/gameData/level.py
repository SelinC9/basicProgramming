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
        self.soilTiles = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.crops = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.interactables = []
        self.particles = pygame.sprite.Group()

        self.mapTransitions = {}
        self.transitioning = False
        self.transitionSpeed = 500
        self.transitionAlpha = 0
        self.playerAdded = False

        self.tmxData = load_pygame('coursework/gameData/graphics/world/myfarm.tmx')
        map_w = self.tmxData.width * self.tmxData.tilewidth
        map_h = self.tmxData.height * self.tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, map_w, map_h)

        self.allSprites = CameraGroup(self.mapRect)

        # Load untiled soil image
        soilFolder = 'coursework/gameData/graphics/soil/'
        self.untiledSoil = pygame.transform.smoothscale(
            pygame.image.load(os.path.join(soilFolder, 'untiled.png')).convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )

        self.setup()

    def tillSoil(self, targetPos):
        for tile in self.soilTiles:
            if tile.rect.collidepoint(targetPos):
                tile.till()
                break

    def waterSoil(self, targetPos):
        for tile in self.soilTiles:
            if tile.rect.collidepoint(targetPos):
                tile.water()
                break

    def chopTree(self, targetPos):
        for tree in self.trees:
            if tree.alive and tree.hitboxSprite.rect.collidepoint(targetPos):
                tree.chop(self.particles)
                break

    def isPlantable(self, tilePos):
        for crop in self.crops:
            if (crop.rect.x // TILE_SIZE, crop.rect.y // TILE_SIZE) == tilePos:
                return False
        return True

    def plantCrop(self, cropName, targetPos):
        tileX = int(targetPos[0] // TILE_SIZE)
        tileY = int(targetPos[1] // TILE_SIZE)
        tilePos = (tileX, tileY)

        if not self.isPlantable(tilePos):
            print("Cannot plant here.")
            return

        cropPos = (tileX * TILE_SIZE, tileY * TILE_SIZE)
        Crop(cropPos, cropName, [self.allSprites, self.crops])
        print(f"Planted {cropName} at {tilePos}")

    def setup(self):
        # Draw ground
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        groundSurf = pygame.image.load("coursework/gameData/graphics/world/myfarm.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(mapWidth * ZOOM_X), int(mapHeight * ZOOM_Y)))
        Generic((0, 0), groundSurf, [self.allSprites], z=LAYERS['ground'])

        # Spawn obstacles
        self.spawnObstacles()

        # Player spawn
        spawnPoint = None
        for obj in self.tmxData.objects:
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y)
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)

        self.player = Player(spawnPoint, [self.allSprites], self.collisionSprites, self)
        self.player.setMapBounds(self.mapRect)

        self.overlay = Overlay(self.player)

    def spawnObstacles(self):
        # Fences
        for x, y, surf in self.tmxData.get_layer_by_name("fence").tiles():
            if surf:
                pos = (x * self.tmxData.tilewidth * ZOOM_X, y * self.tmxData.tileheight * ZOOM_Y)
                Generic(pos, surf, [self.allSprites, self.collisionSprites])

        # Trees
        for obj in self.tmxData.get_layer_by_name("tree"):
            tree = Tree(
                pos=(obj.x * ZOOM_X, obj.y * ZOOM_Y),
                surf=obj.image,
                groups=[self.allSprites, self.trees],
                name=obj.name,
                playerAdded=self.playerAdded
            )
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

        # Rocks
        for obj in self.tmxData.get_layer_by_name("rock"):
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), obj.image, [self.allSprites])
            hitboxSprite = pygame.sprite.Sprite()
            hitboxSprite.rect = pygame.Rect(obj.x * ZOOM_X, obj.y * ZOOM_Y, 16 * ZOOM_X, 16 * ZOOM_Y)
            self.collisionSprites.add(hitboxSprite)

    def run(self, deltaTime):
        self.allSprites.customisedDraw(self.player)
        self.crops.update(deltaTime)
        self.allSprites.update(deltaTime)
        self.particles.update(deltaTime)
        for particle in self.particles:
            offsetRect = particle.rect.copy()
            offsetRect.center -= self.allSprites.offset
            self.displaySurface.blit(particle.image, offsetRect)
        self.overlay.display()
        self.player.inventory.draw(self.displaySurface)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, mapRect):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.mapRect = mapRect

    def customisedDraw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

        maxOffsetX = self.mapRect.width - SCREEN_WIDTH
        maxOffsetY = self.mapRect.height - SCREEN_HEIGHT
        self.offset.x = max(0, min(self.offset.x, maxOffsetX))
        self.offset.y = max(0, min(self.offset.y, maxOffsetY))

        for sprite in sorted(self.sprites(), key=lambda s: getattr(s, "z", 0)):
            offsetRect = sprite.rect.copy()
            offsetRect.center -= self.offset
            self.displaySurface.blit(sprite.image, offsetRect)
