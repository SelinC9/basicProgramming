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
        
        self.velocity = pygame.math.Vector2(velocity[0] * 0.2 * ZOOM_X, velocity[1] * 0.2 * ZOOM_Y)
        self.duration = duration
        self.startTime = pygame.time.get_ticks()
        self.z = z
        self.alive = True
        
    def update(self, deltaTime):
        if not self.alive:
            return
            
        self.rect.x += self.velocity.x * deltaTime * 20
        self.rect.y += self.velocity.y * deltaTime * 20

        elapsed = pygame.time.get_ticks() - self.startTime
        if elapsed < self.duration:
            alpha = 255 - (elapsed * 255 // self.duration)
            self.image = self.originalImage.copy()
            self.image.set_alpha(max(0, alpha))
        else:
            self.alive = False
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
        self.isChopped = False  # track if tree is already chopped
        self.stumpSurf = pygame.image.load(os.path.join("coursework","gameData","graphics","stump","0.png")).convert_alpha()
        self.stumpSurf = pygame.transform.scale(self.stumpSurf, (int(self.stumpSurf.get_width() * ZOOM_X), 
                                                                 int(self.stumpSurf.get_height() * ZOOM_Y)))
        self.invulTimer = Timer(200)
        self.playerAdded = playerAdded
        self.hitboxSprite = None

    def chop(self, particlesGroup, allSpritesGroup, player=None):
        if self.invulTimer.active or not self.alive or self.isChopped:
            return False

        self.health -= 1
        print(f"Tree health: {self.health}")
        self.invulTimer.activate()
        self.spawnLeaves(particlesGroup, allSpritesGroup)

        if self.health <= 0 and not self.isChopped:
            self.alive = False
            self.isChopped = True

            # Remove hitbox so player can walk over
            if self.hitboxSprite:
                self.hitboxSprite.kill()
                self.hitboxSprite = None
            self.hitbox = pygame.Rect(0, 0, 0, 0)

            # Change image to stump
            self.image = self.stumpSurf

            # Give wood to player once
            if player:
                amount = random.randint(2, 3)
                player.inventory.addItem('wood', amount)
                print(f"Picked up wood: {amount}")

        return True
    
    def spawnLeaves(self, particlesGroup, allSpritesGroup):
        leafFolder = os.path.join("coursework","gameData","graphics","leaves")
        if not os.path.exists(leafFolder):
            return
            
        leafFiles = [f"{i}.png" for i in range(5)]
                
        for _ in range(random.randint(5, 8)):
            leafPath = os.path.join(leafFolder, random.choice(leafFiles))
            
            if os.path.exists(leafPath):
                leafSurf = pygame.image.load(leafPath).convert_alpha()
                leafSurf = pygame.transform.scale(leafSurf, (int(32 * ZOOM_X), int(32 * ZOOM_Y)))
                
                pos = (self.rect.centerx + random.randint(-30, 30) * ZOOM_X, 
                       self.rect.centery + random.randint(-50, 0) * ZOOM_Y)
                
                velocity = (random.uniform(-35, 35), random.uniform(-80, -25))
                
                Particle(pos, leafSurf, [particlesGroup, allSpritesGroup], 
                        velocity, duration=3000, z=LAYERS['abovePlayer'])

    def update(self, deltaTime):
        self.invulTimer.update()

class Crop(pygame.sprite.Sprite):
    def __init__(self, pos, cropName, groups):
        super().__init__(groups)
        self.cropName = cropName
        self.growthStages = self.loadGrowthStages(cropName)
        self.stage = 0
        self.image = self.growthStages[self.stage]
        self.rect = self.image.get_rect(topleft=pos)
        self.growthTime = GROW_SPEED[cropName]
        self.elapsedTime = 0
        self.fullyGrown = False

    def loadGrowthStages(self, cropName):
        stages = []
        folderPath = f"coursework/gameData/graphics/overlay/{cropName}"
        
        if not os.path.exists(folderPath):
            return stages

        files = [f for f in os.listdir(folderPath) if f.endswith('.png')]
        files.sort(key=lambda x: int(os.path.splitext(x)[0]))

        for fileName in files:
            img = pygame.image.load(os.path.join(folderPath, fileName)).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * ZOOM_X), 
                                            int(img.get_height() * ZOOM_Y)))
            stages.append(img)

        return stages
    
    def update(self, deltaTime):
        if self.fullyGrown:
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
