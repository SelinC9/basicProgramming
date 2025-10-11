import pygame
import os
import random
from settings import *
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']): #default layer is 'main' layer
        super().__init__(groups) #initialize parent class with groups
        self.image = surf #set image
        self.rect = self.image.get_rect(topleft=pos)    #set rect at position
        self.z = z #layer for rendering order
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75) #smaller hitbox
        self.pickup = False #default no pickup
        self.pickupKey = None #default no pickup key
        self.icon = None #default no icon
        self.alive = True    #alive status

    def destroy(self): #method to destroy the object
        self.alive = False #set alive to false
        self.kill() #remove from all groups

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, velocity, duration=2000, z=LAYERS['abovePlayer']): #duration in milliseconds
        super().__init__(groups) #initialize parent class with groups
        self.originalImage = surf.copy() #store original image
        self.image = self.originalImage.copy() #current image
        self.rect = self.image.get_rect(center=pos) #center at position
        self.velocity = pygame.math.Vector2(velocity[0], velocity[1]) #velocity vector
        self.duration = duration #duration in milliseconds
        self.startTime = pygame.time.get_ticks() #start time in milliseconds
        self.z = z #layer for rendering order
        self.alive = True

    def update(self, deltaTime):
        if not self.alive:
            return
            
        # Convert deltaTime to seconds
        dtSeconds = deltaTime / 1000.0
        
        # Add gravity effect
        self.velocity.y += 100 * dtSeconds
        
        # Add some air resistance
        self.velocity.x *= 0.99
        self.velocity.y *= 0.99
        
        # Update position
        self.rect.x += self.velocity.x * dtSeconds
        self.rect.y += self.velocity.y * dtSeconds
        
        # Handle fade out
        elapsed = pygame.time.get_ticks() - self.startTime
        if elapsed < self.duration:
            progress = elapsed / self.duration
            alpha = max(0, int(255 * (1 - progress)))
            
            # Scale down over time
            scale_factor = 1.0 - (progress * 0.5)
            new_width = max(5, int(self.originalImage.get_width() * scale_factor))
            new_height = max(5, int(self.originalImage.get_height() * scale_factor))
            
            self.image = pygame.transform.scale(self.originalImage, (new_width, new_height))
            self.image.set_alpha(alpha)
            
            # Update rect to maintain center
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
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
        
        # Health system
        self.maxHealth = 5
        self.health = self.maxHealth #start with full health
        self.alive = True   #tree is alive
        self.isChopped = False #not chopped initially
        self.logsSpawned = False #logs not spawned yet
        self.playerAdded = playerAdded #whether player planted the tree
        self.hitboxSprite = None #reference to hitbox sprite if any
        self.invulDuration = 500 #invulnerability duration in milliseconds
        self.invulStart = 0 #time when invulnerability started
        self.stumpCreated = False #whether stump is created
        
        # Stump surface
        self.stumpSurf = self.loadStumpSurface()
        
        # Load leaf images
        self.leafImages = self.loadLeafImages()
        
    def loadStumpSurface(self):
        stumpPath = os.path.join("graphics", "stump", "0.png")
        if os.path.exists(stumpPath): 
            try:
                stump = pygame.image.load(stumpPath).convert_alpha() #load image
                stump = pygame.transform.scale(
                    stump,
                    (int(stump.get_width() * ZOOM_X), int(stump.get_height() * ZOOM_Y)) #scale image
                )
                return stump
            except Exception:
                pass
        
        # Fallback stump surface
        fallback = pygame.Surface((int(32 * ZOOM_X), int(16 * ZOOM_Y)), pygame.SRCALPHA) #create surface
        fallback.fill((101, 67, 33)) #brown
        return fallback

    def loadLeafImages(self):
        leaf_images = []
        leaf_folder = "graphics/leaves"
        
        if not os.path.exists(leaf_folder):
            return self.createFallbackLeaves()
        
        try:
            files = os.listdir(leaf_folder)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            if not image_files:
                return self.createFallbackLeaves()
            
            for filename in image_files:
                leaf_path = os.path.join(leaf_folder, filename)
                
                try:
                    leaf_surf = pygame.image.load(leaf_path).convert_alpha()
                    # Scale to reasonable size
                    base_width = leaf_surf.get_width()
                    base_height = leaf_surf.get_height()
                    scaled_width = max(20, int(base_width * ZOOM_X * 0.7))
                    scaled_height = max(20, int(base_height * ZOOM_Y * 0.7))
                    
                    scaled_leaf = pygame.transform.scale(leaf_surf, (scaled_width, scaled_height))
                    leaf_images.append(scaled_leaf)
                    
                except Exception:
                    continue
                    
        except Exception:
            return self.createFallbackLeaves()
        
        return leaf_images

    def createFallbackLeaves(self):
        fallback_leaves = []
        leaf_colors = [(34, 139, 34), (50, 205, 50), (107, 142, 35)]
        
        for color in leaf_colors:
            for size in [15, 20, 25]:
                leaf_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surf, color, (0, 0, size, size))
                fallback_leaves.append(leaf_surf)
                
        return fallback_leaves

    def chop(self, particlesGroup=None, allSpritesGroup=None, player=None):
        now = pygame.time.get_ticks() #current time
        # Check invulnerability
        if now - self.invulStart < self.invulDuration: 
            return False
        if not self.alive or self.isChopped:
            return False
        
        # Reduce health
        self.health -= 1
        self.invulStart = now
        
        # spawn leaves when chopped
        if particlesGroup is not None and allSpritesGroup is not None:
            self.spawnLeaves(particlesGroup, allSpritesGroup)

        # Check if tree should be chopped down
        if self.health <= 0:
            self.alive = False
            self.isChopped = True
            
            # Remove collision
            if self.hitboxSprite:
                self.hitboxSprite.kill()
                self.hitboxSprite = None
            
            # Spawn logs
            if not self.logsSpawned and player and allSpritesGroup:
                self.logsSpawned = True
                numLogs = random.randint(2, 3)
                for _ in range(numLogs): #spawn 2-3 logs
                    offset_x = random.randint(-20, 20) #random offset
                    offset_y = random.randint(-10, 10) #random offset
                    logPos = (self.rect.centerx + offset_x, self.rect.centery + offset_y) #position with offset
                    groups = [allSpritesGroup]
                    if hasattr(player.level, 'itemsGroup'): #add to items group if exists
                        groups.append(player.level.itemsGroup)
                    Wood(logPos, player.level.woodSurf, groups)
            
            # Create stump
            if not self.stumpCreated and allSpritesGroup:
                self.stumpCreated = True
                stumpPos = (self.rect.centerx - self.stumpSurf.get_width() // 2, 
                        self.rect.bottom - self.stumpSurf.get_height())
                Stump(stumpPos, self.stumpSurf, [allSpritesGroup], z=LAYERS['main'])
            
            self.kill()
            return True
            
        return True

    def spawnLeaves(self, particlesGroup, allSpritesGroup): # Spawn leaf particles
        if not self.leafImages:
            return
            
        numLeaves = random.randint(10, 15)
        
        for i in range(numLeaves):
            # Choose a random leaf image
            leaf_surf = random.choice(self.leafImages)
            
            # Spawn position around tree center
            posX = self.rect.centerx + random.randint(-self.rect.width//3, self.rect.width//3)
            posY = self.rect.centery + random.randint(-self.rect.height//3, self.rect.height//3)
            pos = (posX, posY)
            
            # Random velocity
            velocityX = random.uniform(-100, 100)
            velocityY = random.uniform(-80, 40)
            
            # Random duration
            duration = random.randint(1500, 2500)
            
            # Create particle
            Particle(pos, leaf_surf, [particlesGroup, allSpritesGroup], 
                    (velocityX, velocityY), duration=duration, z=LAYERS['abovePlayer'])

class Stump(Generic):
    def __init__(self, pos, surf, groups, z=LAYERS['main'], duration=None): #duration=None means permanent
        super().__init__(pos, surf, groups, z) #call parent constructor
        self.duration = duration #duration in milliseconds
        self.start = pygame.time.get_ticks() if duration else None

    def update(self, deltaTime): #check if duration has passed
        if self.duration is None: 
            return
        if pygame.time.get_ticks() - self.start >= self.duration: #time to remove
            self.kill()

class Crop(pygame.sprite.Sprite):
    def __init__(self, pos, cropName, groups):
        super().__init__(groups)
        self.cropName = cropName
        self.growthStages = self.loadGrowthStages(cropName)
        self.stage = 0
        self.image = self.growthStages[self.stage] if self.growthStages else pygame.Surface((32,32)) #fallback
        self.rect = self.image.get_rect(topleft=pos) #position
        self.growthTime = GROW_SPEED.get(cropName, 1000) #default 1000s
        self.elapsedTime = 0 #time since last growth
        self.fullyGrown = False #flag

    def loadGrowthStages(self, cropName):
        stages = []
        folderPath = os.path.join("graphics", "overlay", cropName) #path to crop folder
        if not os.path.exists(folderPath): 
            return stages
        files = [f for f in os.listdir(folderPath) if f.endswith('.png')] #only pngs
        files.sort(key=lambda x: int(os.path.splitext(x)[0])) #sort numerically
        for fileName in files: #load each image
            img = pygame.image.load(os.path.join(folderPath, fileName)).convert_alpha() #load
            img = pygame.transform.scale(img, (int(img.get_width() * ZOOM_X), int(img.get_height() * ZOOM_Y))) #scale
            stages.append(img) 
        return stages

    def update(self, deltaTime):
        if self.fullyGrown or not self.growthStages: 
            return
        self.elapsedTime = self.elapsedTime + deltaTime #increment elapsed time
        if self.elapsedTime >= self.growthTime and self.stage < len(self.growthStages) - 1:
            self.stage = self.stage + 1
            self.image = self.growthStages[self.stage] #update image
            self.elapsedTime = 0
            if self.stage == len(self.growthStages) - 1: 
                self.fullyGrown = True

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, untiledImage, tilledImage):
        super().__init__(groups)
        self.untiledImage = untiledImage #surface for untilled
        self.tilledImage = tilledImage  #surface for tilled
        self.image = self.untiledImage #start as untilled
        self.rect = self.image.get_rect(topleft=pos) #position of tile
        self.tilled = False
        self.z = LAYERS['soil']

    def till(self):
        self.image = self.tilledImage
        self.tilled = True

    def water(self):
        pass

class Wood(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, LAYERS['main']) #call parent constructor
        self.pickup = True
        self.pickupKey = 'wood' #key for inventory
        self.itemName = 'wood' #name for inventory
        self.icon = pygame.transform.scale(surf, (32, 32)) #icon for inventory
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5, -self.rect.height * 0.5) #smaller hitbox