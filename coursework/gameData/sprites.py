import pygame
import os
import random
from settings import *
from timer import Timer

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
    def __init__(self, pos, surf, velocity, duration=3000, z=LAYERS['abovePlayer']):
        super().__init__()        
        # Make sure the surface is properly scaled and has alpha
        self.originalImage = surf.copy()
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect(center=pos)
        
        # Use moderate speed - not too fast, not too slow
        self.velocity = pygame.math.Vector2(velocity[0] * 0.2, velocity[1] * 0.2)
        self.duration = duration
        self.startTime = pygame.time.get_ticks()
        self.z = z
        self.alive = True
        
    def update(self, deltaTime):
        if not self.alive:
            return
            
        # Move particle with moderate speed
        self.rect.x += self.velocity.x * deltaTime * 20
        self.rect.y += self.velocity.y * deltaTime * 20

        # Calculate fade effect
        elapsed = pygame.time.get_ticks() - self.startTime
        if elapsed < self.duration:
            # Smooth fade out from 255 to 0 alpha
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
        self.health = 5
        self.alive = True
        stumpPath = os.path.join("coursework","gameData","graphics","stump","0.png")
        self.stumpSurf = pygame.image.load(stumpPath).convert_alpha()
        self.invulTimer = Timer(200)
        self.playerAdded = playerAdded
        
    def chop(self, particlesGroup):
        if self.invulTimer.active:
            return

        self.health -= 1
        self.invulTimer.activate()
        self.spawnLeaves(particlesGroup)

        if self.health <= 0:
            self.alive = False
            self.image = self.stumpSurf
            if hasattr(self, 'hitboxSprite'):
                self.hitboxSprite.kill()

    def spawnLeaves(self, particlesGroup):
        leafFolder = os.path.join("coursework","gameData","graphics","leaves")
        leafFiles = [f"{i}.png" for i in range(5)]
                
        for _ in range(random.randint(5, 8)):
            leafPath = os.path.join(leafFolder, random.choice(leafFiles))
            
            if os.path.exists(leafPath):
                # Load and scale leaf image to be more visible
                leafSurf = pygame.image.load(leafPath).convert_alpha()
                leafSurf = pygame.transform.scale(leafSurf, (32, 32))  # Make leaves larger
                
                # Position particles around the tree
                pos = (self.rect.centerx + random.randint(-30, 30), 
                       self.rect.centery + random.randint(-50, 0))
                
                # Moderate velocity for visible movement
                velocity = (random.uniform(-35, 35), random.uniform(-80, -25))
                particle = Particle(pos, leafSurf, velocity, duration=3000)
                
                # Add to both particles group and allSprites group
                particlesGroup.add(particle)
                
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