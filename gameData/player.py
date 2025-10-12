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
        self.speed = 180

        # Collision
        self.hitbox = pygame.Rect(0,0,20,24)
        self.hitbox.center = self.rect.center # Align hitbox with player rect
        self.collisionSprites = collisionSprites # Sprites to check collision against

        #sleep system
        self.canSleep = False
        self.sleepTimer = Timer(5000, self.sleep) # 5 seconds to sleep

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
        self.tools = ['hoe','axe','wateringCan', 'pickaxe'] # Available tools
        self.toolIndex = 0
        self.selectedTool = self.tools[self.toolIndex] # Start with first tool

        self.seeds = ['kale','parsnips','beans','potatoes','melon','corn','hotPeppers','tomato','cranberries','pumpkin','berries','onion','beets','artichoke'] # Available seeds
        self.seedIndex = 0
        self.selectedSeed = self.seeds[self.seedIndex] # Start with first seed

        self.inventory.addItem('kale', 5)
        self.inventory.addItem('tomato', 3)
        self.inventory.addItem('corn', 3)

        # Map boundaries
        self.boundary = None
        self.targetPos = pygame.math.Vector2(self.rect.center)

    def setMapBounds(self, rect):
        self.boundary = rect.copy() # Set movement boundaries

    def useTool(self):
        tileX, tileY = self.level.getTileInFront(self) # Get tile in front of player
        if self.selectedTool == 'hoe':
            if not self.level.harvestCrop(tileX, tileY): # Try to harvest first
                self.level.tillSoil(self) # Till soil at target position
        elif self.selectedTool == 'wateringCan':
            target = (tileX*TILE_SIZE + TILE_SIZE//2, tileY*TILE_SIZE + TILE_SIZE//2)
            self.level.waterSoil(target) # Water soil at target position
        elif self.selectedTool == 'axe':
            self.level.chopTree(tileX, tileY) # Chop tree at target position
        elif self.selectedTool == 'pickaxe':
            self.level.breakRock(tileX, tileY) # Mine rock at target position

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
            'upPickaxe','downPickaxe','leftPickaxe','rightPickaxe',
            'upWater','downWater','leftWater','rightWater'
        ]}
        for key in self.animations.keys(): 
            fullPath = os.path.join(characterPath,key) # Full path to animation folder
            if os.path.exists(fullPath): # Check if folder exists
                loaded_frames = importFolder(fullPath) # Load all frames in folder
                if loaded_frames: # Only use if we got actual frames
                    self.animations[key] = loaded_frames
                else:
                    # Create a simple fallback frame
                    fallback = pygame.Surface((32, 32))
                    fallback.fill((255, 0, 255))
                    self.animations[key] = [fallback]
                    print(f"Created fallback for {key} - no frames loaded")
            else:
                # Create a simple fallback frame for missing folders
                fallback = pygame.Surface((32, 32))
                fallback.fill((255, 0, 255))
                self.animations[key] = [fallback]
                print(f"Created fallback for {key} - folder missing")

    def pickupItem(self):
        # Find the nearest pickupable item
        nearest_item = None
        min_distance = float('inf')
        
        if hasattr(self.level, 'itemsGroup'):
            for item in self.level.itemsGroup:
                if hasattr(item, 'pickup') and item.pickup:
                    distance = pygame.math.Vector2(item.rect.center).distance_to(
                        pygame.math.Vector2(self.rect.center))
                    
                    if distance < 50 and distance < min_distance:  # Within pickup range
                        nearest_item = item
                        min_distance = distance
        
        if nearest_item:
            # Add to inventory instead of just destroying
            success = self.inventory.addItem(
                nearest_item.pickupKey, 
                1,
                getattr(nearest_item, 'icon', None)
            )
            
            if success:
                print(f"Picked up {nearest_item.pickupKey}")
                nearest_item.kill()
            else:
                print("Inventory full - couldn't pick up item")

    def animate(self, deltaTime):
        # Store current position and rect before any animation changes
        current_center = self.rect.center
        
        # Get the current animation frames for the status
        current_animation = self.animations.get(self.status, [])
        
        if current_animation and len(current_animation) > 0:
            # 8 frames per second for smooth walking animation
            animation_speed = 8.0  # frames per second
            
            # Update frame index based on time
            self.frameIndex += animation_speed * deltaTime
            
            # Loop animation if we exceed frame count
            if self.frameIndex >= len(current_animation):
                self.frameIndex = 0
            
            # Get the current frame
            current_frame = current_animation[int(self.frameIndex)]
            
            # Update the image while preserving the rect properties
            old_rect = self.rect.copy()
            self.image = current_frame
            self.rect = self.image.get_rect(center=current_center)
            
        else:
            # Fallback: use downIdle if current animation is completely empty
            fallback_animation = self.animations.get('downIdle', [])
            if fallback_animation and len(fallback_animation) > 0:
                self.image = fallback_animation[0]
                self.rect = self.image.get_rect(center=current_center)
            else:
                # Ultimate fallback
                self.image = pygame.Surface((32, 32))
                self.image.fill((255, 0, 255))
                self.rect = self.image.get_rect(center=current_center)
        
        # Ensure hitbox stays aligned with the player
        self.hitbox.center = self.rect.center
        
    def input(self):
        keys = pygame.key.get_pressed()
        
        #debugging - MOVED TO TOP SO IT ALWAYS WORKS
        if keys[pygame.K_1]:  # Press 1 to set to morning (6 AM)
            if hasattr(self.level, 'time'):
                self.level.time.currentTime = 6 * TIME_RATE
                print(f"DEBUG: Set time to 6 AM - currentTime: {self.level.time.currentTime}")
            else:
                print("DEBUG: No time system found!")
        if keys[pygame.K_2]:  # Press 2 to set to noon (12 PM)
            if hasattr(self.level, 'time'):
                self.level.time.currentTime = 12 * TIME_RATE
                print(f"DEBUG: Set time to 12 PM - currentTime: {self.level.time.currentTime}")
        if keys[pygame.K_3]:  # Press 3 to set to evening (6 PM)
            if hasattr(self.level, 'time'):
                self.level.time.currentTime = 18 * TIME_RATE
                print(f"DEBUG: Set time to 6 PM - currentTime: {self.level.time.currentTime}")
        if keys[pygame.K_4]:  # Press 4 to set to night (10 PM)
            if hasattr(self.level, 'time'):
                self.level.time.currentTime = 22 * TIME_RATE
                print(f"DEBUG: Set time to 10 PM - currentTime: {self.level.time.currentTime}")
        if keys[pygame.K_5]:  # Press 5 to advance time by 1 hour
            if hasattr(self.level, 'time'):
                self.level.time.currentTime += 60
                print(f"DEBUG: Advanced time by 1 hour - currentTime: {self.level.time.currentTime}")
        if keys[pygame.K_6]:  # Press 6 to advance time by 6 hours
            if hasattr(self.level, 'time'):
                self.level.time.currentTime += 360
                print(f"DEBUG: Advanced time by 6 hours - currentTime: {self.level.time.currentTime}")

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

            #Sleep interaction(when near bed)
            if keys[pygame.K_z] and self.canSleep and not self.sleepTimer.active:
                self.sleepTimer.activate()
                print("Going to sleep...")

            # Tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frameIndex = 0

            # Switch tool
            if keys[pygame.K_t] and not self.timers['tool switch'].active:
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

            # F key pickup
            if keys[pygame.K_f] and not self.timers['tool use'].active:
                self.pickupItem()

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

    def sleep(self):
        #move to the next day
        if hasattr(self.level, 'time'):
            self.level.time.currentTime = 6 * TIME_RATE  # Wake up at 6 AM
            self.level.time.dayCount += 1
            print(f"Good morning! Day {self.level.time.dayCount}")

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
        self.sleepTimer.update() # Update sleep timer