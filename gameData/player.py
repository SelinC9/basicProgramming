import pygame
import os
from settings import *
from support import *
from timer import Timer
from inventory import Inventory

PLAYER_TOOL_OFFSET = {
    'up': pygame.math.Vector2(0, -32),
    'down': pygame.math.Vector2(0, 32),
    'left': pygame.math.Vector2(-32, 0),
    'right': pygame.math.Vector2(32, 0)
}

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collisionSprites, level):
        super().__init__(groups)
        self.level = level

        # Load assets
        self.importAssets()
        self.status = 'downIdle'
        self.frameIndex = 0

        # Use a fallback surface if animation empty
        if self.animations.get(self.status) and len(self.animations[self.status]) > 0: # Check if animation list is not empty
            self.image = self.animations[self.status][self.frameIndex] # Set initial image
        else:
            self.image = pygame.Surface((32, 32)) #
            self.image.fill((255,0,255))

        self.rect = self.image.get_rect(center=pos) # Center the rect on the given position
        self.z = LAYERS['main']

        # Movement
        self.direction = pygame.math.Vector2() # Initialize direction vector
        self.pos = pygame.math.Vector2(self.rect.center) # Use float for precise movement
        self.speed = 200

        # Collision
        self.hitbox = pygame.Rect(0,0,20,24)
        self.hitbox.center = self.rect.center # Align hitbox with player rect
        self.collisionSprites = collisionSprites # Sprites to check collision against

        # Timers
        self.timers = {
            'tool use': Timer(350, self.useTool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.useSeed),
            'seed switch': Timer(200)
        }

        # Inventory
        self.inventory = Inventory(size=10, level=self.level) # Inventory UI
        self.itemInventory = {name:0 for name in [
            'kale','parsnips','beans','potatoes','melon','corn','hotPeppers',
            'tomato','cranberries','pumpkin','berries','onion','beets','artichoke',
            'wood','stone'
        ]}  # Initialize item inventory with zero counts
        self.inventoryCapacity = 20 # Max different item types

        # Tools & seeds
        self.tools = ['hoe','axe','wateringCan']
        self.toolIndex = 0
        self.selectedTool = self.tools[self.toolIndex] # Start with first tool

        self.seeds = ['kale','parsnips','beans','potatoes','melon','corn','hotPeppers','tomato','cranberries','pumpkin','berries','onion','beets','artichoke'] # Available seeds
        self.seedIndex = 0
        self.selectedSeed = self.seeds[self.seedIndex] # Start with first seed

        # Map boundaries
        self.boundary = None
        self.targetPos = pygame.math.Vector2(self.rect.center)

    def setMapBounds(self, rect):
        self.boundary = rect.copy() # Set movement boundaries

    def useTool(self):
        tileX, tileY = self.level.getTileInFront(self) # Get tile in front of player
        if self.selectedTool == 'hoe':
            self.level.tillSoil(self) # Till soil at target position
        elif self.selectedTool == 'wateringCan':
            target = (tileX*TILE_SIZE + TILE_SIZE//2, tileY*TILE_SIZE + TILE_SIZE//2)
            self.level.waterSoil(target) # Water soil at target position
        elif self.selectedTool == 'axe':
            self.level.chopTree(tileX, tileY) # Chop tree at target position

    def useSeed(self):
        self.level.plantCrop(self.selectedSeed, self) # Plant selected seed at target position

    def addItem(self, item, amount=1): 
        if self.inventoryFull(): return False # Inventory full
        self.itemInventory[item] += amount # Add item to inventory
        return True

    def inventoryFull(self):
        return sum(self.itemInventory.values()) >= self.inventoryCapacity # Check if inventory is full

    def importAssets(self):
        characterPath = "graphics/character/"
        self.animations = {name:[] for name in [
            'up','down','left','right',
            'upIdle','downIdle','leftIdle','rightIdle',
            'upHoe','downHoe','leftHoe','rightHoe',
            'upAxe','downAxe','leftAxe','rightAxe',
            'upWater','downWater','leftWater','rightWater'
        ]}
        for key in self.animations.keys(): 
            fullPath = os.path.join(characterPath,key) # Full path to animation folder
            self.animations[key] = importFolder(fullPath) # Load all frames in folder

    def animate(self, deltaTime):
        if self.animations.get(self.status): # Check if animation list exists
            self.frameIndex += 10 * deltaTime # Animation speed
            if self.frameIndex >= len(self.animations[self.status]): 
                self.frameIndex = 0
            self.image = self.animations[self.status][int(self.frameIndex)] # Update image

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['tool use'].active:
            self.direction.x = 0
            self.direction.y = 0

            # Movement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'

            if self.direction.magnitude() == 0:
                if 'left' in self.status:
                    self.status = 'leftIdle'
                elif 'right' in self.status:
                    self.status = 'rightIdle'
                elif 'up' in self.status:
                    self.status = 'upIdle'
                else:
                    self.status = 'downIdle'

            # Tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frameIndex = 0

            # Switch tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.toolIndex = (self.toolIndex + 1) % len(self.tools)
                self.selectedTool = self.tools[self.toolIndex]

            # Seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frameIndex = 0

            # Switch seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seedIndex = (self.seedIndex + 1) % len(self.seeds)
                self.selectedSeed = self.seeds[self.seedIndex]

    def getStatus(self):
        base = 'down'
        if 'up' in self.status:
            base = 'up'
        elif 'down' in self.status:
            base = 'down'
        elif 'left' in self.status:
            base = 'left'
        elif 'right' in self.status:
            base = 'right'

        if self.direction.magnitude() == 0 and not self.timers['tool use'].active: 
            self.status = base + 'Idle' # Idle if not moving
        elif self.timers['tool use'].active: 
            self.status = base + self.selectedTool.capitalize() # Tool use animation

    def updateTimers(self):
        for timer in self.timers.values():
            timer.update() # Update all timers

    def collision(self, direction):
        for sprite in self.collisionSprites.sprites():
            if not hasattr(sprite, 'hitbox'):
                sprite.hitbox = sprite.rect.copy() # Ensure sprite has a hitbox
            
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal': 
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx # Update rect position
                    self.pos.x = self.hitbox.centerx # Update precise position
                    
                if direction == 'vertical':
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery # Update rect position
                    self.pos.y = self.hitbox.centery # Update precise position

    def move(self, deltaTime):
        if self.direction.magnitude() > 0: 
            self.direction = self.direction.normalize() # Normalize to get direction only

        self.pos.x += self.direction.x * self.speed * deltaTime # Update position with speed and deltaTime
        self.hitbox.centerx = round(self.pos.x) # Update hitbox position
        self.collision('horizontal') # Check horizontal collisions

        self.pos.y += self.direction.y * self.speed * deltaTime # Update position with speed and deltaTime
        self.hitbox.centery = round(self.pos.y) # Update hitbox position
        self.collision('vertical')

        if self.boundary:
            halfW, halfH = self.rect.width / 2, self.rect.height / 2 # Half dimensions
            self.pos.x = max(self.boundary.left + halfW, min(self.pos.x, self.boundary.right - halfW)) # Clamp to boundaries
            self.pos.y = max(self.boundary.top + halfH, min(self.pos.y, self.boundary.bottom - halfH)) # Clamp to boundaries
            self.rect.center = (round(self.pos.x), round(self.pos.y)) # Update rect position
            self.hitbox.center = self.rect.center # Keep hitbox aligned

    def getTargetPos(self): # Calculate target position based on direction
        baseDir = 'down' # Default direction
        if 'up' in self.status:
            baseDir = 'up'
        elif 'down' in self.status:
            baseDir = 'down'
        elif 'left' in self.status:
            baseDir = 'left' 
        elif 'right' in self.status:
            baseDir = 'right' # Determine base direction
        self.targetPos = pygame.math.Vector2(self.rect.center) + PLAYER_TOOL_OFFSET[baseDir] # Calculate target position

    def update(self, deltaTime): # Called every frame
        self.input() # Handle input
        self.move(deltaTime) # Move player
        self.getStatus() # Update status
        self.updateTimers() # Update timers
        self.getTargetPos() # Update target position
        self.animate(deltaTime) # Animate player