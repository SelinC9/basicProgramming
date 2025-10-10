import pygame
import os
import random
from settings import *
from timer import Timer

ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        self.pickup = False
        self.pickupKey = None
        self.icon = None
        self.alive = True

    def destroy(self):
        self.alive = False
        self.kill()

class Wildflower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, velocity, duration=3000, z=LAYERS['abovePlayer']):
        super().__init__(groups)
        self.originalImage = surf.copy()
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.math.Vector2(velocity[0], velocity[1])
        self.duration = duration
        self.startTime = pygame.time.get_ticks()
        self.z = z

    def update(self, deltaTime):
        self.rect.x += self.velocity.x * deltaTime * 20
        self.rect.y += self.velocity.y * deltaTime * 20
        elapsed = pygame.time.get_ticks() - self.startTime
        if elapsed < self.duration:
            alpha = 255 - (elapsed * 255 // self.duration)
            self.image = self.originalImage.copy()
            self.image.set_alpha(max(0, alpha))
        else:
            self.kill()

class Stump(Generic):
    def __init__(self, pos, surf, groups, z=LAYERS['main'], duration=None):
        super().__init__(pos, surf, groups, z)
        self.duration = duration
        self.start = pygame.time.get_ticks() if duration else None

    def update(self, deltaTime):
        if self.duration is None:
            return
        if pygame.time.get_ticks() - self.start >= self.duration:
            self.kill()

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, name, playerAdded):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        self.z = LAYERS['main']
        self.name = name
        self.maxHealth = 5
        self.health = self.maxHealth
        self.alive = True
        self.isChopped = False
        self.logsSpawned = False
        self.playerAdded = playerAdded
        self.hitboxSprite = None
        self.invulDuration = 300
        self.invulStart = 0
        stumpPath = os.path.join("graphics", "stump", "0.png")
        if os.path.exists(stumpPath):
            stump = pygame.image.load(stumpPath).convert_alpha()
            self.stumpSurf = pygame.transform.scale(
                stump,
                (int(stump.get_width() * ZOOM_X), int(stump.get_height() * ZOOM_Y))
            )
        else:
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            self.stumpSurf = surf

    def chop(self, particlesGroup=None, allSpritesGroup=None, player=None):
        now = pygame.time.get_ticks()
        if now - self.invulStart < self.invulDuration:
            return False
        if not self.alive or self.isChopped:
            return False
        self.health -= 1
        self.invulStart = now
        if particlesGroup and allSpritesGroup:
            self.spawnLeaves(particlesGroup, allSpritesGroup)
        if self.health <= 0:
            self.alive = False
            self.isChopped = True
            if self.hitboxSprite:
                self.hitboxSprite.kill()
                self.hitboxSprite = None
            if not self.logsSpawned:
                self.logsSpawned = True
                if player and allSpritesGroup:
                    numLogs = random.randint(2, 3)
                    for _ in range(numLogs):
                        offset_x = random.randint(-10, 10)
                        offset_y = -10
                        logPos = (self.rect.centerx + offset_x, self.rect.bottom + offset_y)
                        groups = [allSpritesGroup]
                        if hasattr(player.level, 'itemsGroup'):
                            groups.append(player.level.itemsGroup)
                        Wood(logPos, player.level.woodSurf if hasattr(player.level, 'woodSurf') else pygame.Surface((16,16)), groups)
                        player.inventory.addItem('wood', 1)
            if allSpritesGroup:
                stumpPos = (self.rect.left, self.rect.bottom - self.stumpSurf.get_height())
                Stump(stumpPos, self.stumpSurf, [allSpritesGroup], z=LAYERS['main'])
            self.kill()
        return True

    def spawnLeaves(self, particlesGroup, allSpritesGroup):
        leafFolder = os.path.join("graphics", "leaves")
        if not os.path.exists(leafFolder):
            return
        leafFiles = [f"{i}.png" for i in range(5)]
        for _ in range(random.randint(5, 8)):
            leafPath = os.path.join(leafFolder, random.choice(leafFiles))
            if os.path.exists(leafPath):
                leafSurf = pygame.image.load(leafPath).convert_alpha()
                leafSurf = pygame.transform.scale(leafSurf, (int(32 * ZOOM_X), int(32 * ZOOM_Y)))
                pos = (self.rect.centerx + random.randint(-20, 20), self.rect.top + random.randint(-50, -10))
                velocity = (random.uniform(-35, 35), random.uniform(-80, -25))
                Particle(pos, leafSurf, [particlesGroup, allSpritesGroup], velocity, duration=3000, z=LAYERS['abovePlayer'])

class Crop(pygame.sprite.Sprite):
    def __init__(self, pos, cropName, groups):
        super().__init__(groups)
        self.cropName = cropName
        self.growthStages = self.loadGrowthStages(cropName)
        self.stage = 0
        self.image = self.growthStages[self.stage] if self.growthStages else pygame.Surface((32,32))
        self.rect = self.image.get_rect(topleft=pos)
        self.growthTime = GROW_SPEED.get(cropName, 1000)
        self.elapsedTime = 0
        self.fullyGrown = False

    def loadGrowthStages(self, cropName):
        stages = []
        folderPath = os.path.join("graphics", "overlay", cropName)
        if not os.path.exists(folderPath):
            return stages
        files = [f for f in os.listdir(folderPath) if f.endswith('.png')]
        files.sort(key=lambda x: int(os.path.splitext(x)[0]))
        for fileName in files:
            img = pygame.image.load(os.path.join(folderPath, fileName)).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * ZOOM_X), int(img.get_height() * ZOOM_Y)))
            stages.append(img)
        return stages

    def update(self, deltaTime):
        if self.fullyGrown or not self.growthStages:
            return
        self.elapsedTime += deltaTime
        if self.elapsedTime >= self.growthTime and self.stage < len(self.growthStages) - 1:
            self.stage += 1
            self.image = self.growthStages[self.stage]
            self.elapsedTime = 0
            if self.stage == len(self.growthStages) - 1:
                self.fullyGrown = True

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, untiledImage, tilledImage):
        super().__init__(groups)
        self.untiledImage = untiledImage
        self.tilledImage = tilledImage
        self.image = self.untiledImage
        self.rect = self.image.get_rect(topleft=pos)
        self.tilled = False
        self.z = LAYERS['soil']

    def till(self):
        self.image = self.tilledImage
        self.tilled = True

    def water(self):
        pass

class Item(Generic):
    def __init__(self, pos, surf, groups, itemName):
        super().__init__(pos, surf, groups)
        self.pickup = True
        self.itemName = itemName

class Wood(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, LAYERS['main'])
        self.pickup = True
        self.pickupKey = 'wood'
        self.itemName = 'wood'
        self.icon = pygame.transform.scale(surf, (32, 32))
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5, -self.rect.height * 0.5)
