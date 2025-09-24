import pygame
import os
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import *
from overlay import Overlay

ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface()
        
        # Load soil images
        self.untiledSoil = pygame.transform.smoothscale(
            pygame.image.load('graphics/soil/untiled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )
        self.tilledSoilImage = pygame.transform.smoothscale(
            pygame.image.load('graphics/soil/tilled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )

        # Sprite groups
        self.allSprites = CameraGroup(pygame.Rect(0, 0, 0, 0))
        self.soilTiles = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.crops = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        # Map
        self.tmxData = load_pygame('graphics/world/myfarm.tmx')
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, mapWidth, mapHeight)
        self.allSprites.mapRect = self.mapRect

        self.playerAdded = False
        self.setup()
    
    # ------------------------- PLAYER / TILE INTERACTIONS -------------------------
    def getTileInFront(self, player):
        tileX = player.rect.centerx // TILE_SIZE
        tileY = player.rect.centery // TILE_SIZE
        direction = player.status
        if "Idle" in direction:
            direction = direction.replace("Idle", "")
        for tool in ["Axe", "Water", "Hoe"]:
            if direction.endswith(tool):
                direction = direction[:-len(tool)]
                break
        if direction == "up": tileY -= 1
        if direction == "down": tileY += 1
        if direction == "left": tileX -= 1
        if direction == "right": tileX += 1
        return int(tileX), int(tileY)

    def tillSoil(self, player):
        tileX, tileY = self.getTileInFront(player)
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if not tile.tilled:
                    tile.till()
                return
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
        targetArea = pygame.Rect(
            tileX * TILE_SIZE * ZOOM_X - TILE_SIZE * ZOOM_X,
            tileY * TILE_SIZE * ZOOM_Y - TILE_SIZE * ZOOM_Y,
            TILE_SIZE * ZOOM_X * 3,
            TILE_SIZE * ZOOM_Y * 3
        )
        for tree in self.trees:
            if tree.rect.colliderect(targetArea) and tree.alive and not tree.isChopped:
                tree.chop(self.particles, self.allSprites)
                return True
        return False

    def isPlantable(self, tilePos):
        for crop in self.crops:
            if (crop.rect.x // TILE_SIZE, crop.rect.y // TILE_SIZE) == tilePos:
                return False
        return True

    def plantCrop(self, cropName, player):
        tileX, tileY = self.getTileInFront(player)
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if tile.tilled and self.isPlantable((tileX, tileY)):
                    cropPos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
                    Crop(cropPos, cropName, [self.allSprites, self.crops])
                return

    # ------------------------- SETUP -------------------------
    def setup(self):
        # Ground layer
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        groundSurf = pygame.image.load("graphics/world/myfarm.png").convert_alpha()
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

        from player import Player  # delayed import to avoid circular import
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
            # Add invisible trunk for collisions
            trunkW, trunkH = int(tree.rect.width*0.2), int(tree.rect.height*0.25)
            hitboxSurf = pygame.Surface((trunkW, trunkH), pygame.SRCALPHA)
            hitboxSprite = Generic(
                (tree.rect.centerx-trunkW//2, tree.rect.bottom-trunkH),
                hitboxSurf,
                [self.collisionSprites],
                z=LAYERS['main']
            )
            tree.hitboxSprite = hitboxSprite
        # Rocks
        for obj in self.tmxData.get_layer_by_name("rock"):
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), obj.image, [self.allSprites])
            rockHitbox = pygame.Surface((int(16 * ZOOM_X), int(16 * ZOOM_Y)), pygame.SRCALPHA)
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), rockHitbox, [self.collisionSprites])

    # ------------------------- RUN -------------------------
    def run(self, deltaTime):
        self.allSprites.update(deltaTime)
        self.crops.update(deltaTime)
        self.particles.update(deltaTime)
        self.trees.update(deltaTime)

        keys = pygame.key.get_pressed()
        for sprite in [s for s in self.allSprites if getattr(s, 'pickup', False)]:
            if self.player.rect.colliderect(sprite.rect):
                if keys[pygame.K_f]:
                    added = self.player.inventory.addItem(sprite.pickupKey, 1, getattr(sprite, 'icon', None))
                    if added: sprite.kill()

        self.allSprites.customisedDraw(self.player)
        self.overlay.display()
        self.player.inventory.draw(self.displaySurface)


# ------------------------- CAMERA -------------------------
class CameraGroup(pygame.sprite.Group):
    def __init__(self, mapRect):
        super().__init__()
        self.mapRect = mapRect
        self.offset = pygame.math.Vector2(0,0)
        self.displaySurface = pygame.display.get_surface()

    def customisedDraw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/2
        self.offset.x = max(0, min(self.offset.x, self.mapRect.width - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.mapRect.height - SCREEN_HEIGHT))
        for sprite in sorted(self.sprites(), key=lambda spr: spr.z):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)
