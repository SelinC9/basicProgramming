import pygame
import os
import random
from settings import *
from timer import Timer

class Generic(pygame.sprite.Sprite): #generic sprite class
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups) #initialise the sprite class
        self.image = surf #surface of the sprite
        self.rect = self.image.get_rect(topleft = pos) #rectangle of the sprite
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75) #creates a hitbox for the sprite

class Wildflower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups) #initialise the generic class
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9) #creates a hitbox for the wildflower

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration = 1500, velocity=None):
        super().__init__(pos, surf, groups, z) # initialise generic properly
        self.originalImage = surf.copy()  # Keep a copy to reset alpha
        self.startTime = pygame.time.get_ticks() #gets the current time in milliseconds
        self.duration = duration #duration of the particle in milliseconds

        if velocity is None:
            self.velocity = pygame.math.Vector2(random.uniform(-50,50), random.uniform(50,120))
        else:
            self.velocity = pygame.math.Vector2(velocity)

    def update(self, deltaTime):
        # Move particle
        self.rect.x += self.velocity.x * deltaTime
        self.rect.y += self.velocity.y * deltaTime

        # Fade out smoothly
        elapsed = pygame.time.get_ticks() - self.startTime
        alpha = max(0, 255 - (255 * elapsed / self.duration))
        self.image = self.originalImage.copy()
        self.image.set_alpha(alpha)

        # Kill after duration
        if elapsed > self.duration:
            self.kill()

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, name, playerAdded):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        self.z = LAYERS['main']

        # tree attributes
        self.name = name
        self.health = 5
        self.alive = True
        stumpPath = os.path.join("coursework","gameData","graphics","stump","0.png")
        self.stumpSurf = pygame.image.load(stumpPath).convert_alpha()
        self.invulTimer = Timer(200)
        
        self.playerAdded = playerAdded

    def chop(self, particlesGroup):
        if not self.alive:
            return

        # spawn leaves when chopping
        self.spawnLeaves(particlesGroup)

        if self.invulTimer.active:  # prevent rapid chopping
            return

        self.health -= 1
        self.invulTimer.activate()  # start invulnerability timer

        if self.health <= 0:
            self.alive = False
            self.image = self.stumpSurf  # swap tree sprite with stump
            if hasattr(self, 'hitboxSprite'):
                self.hitboxSprite.kill()  # remove the hitbox if it exists

    def spawnLeaves(self, particlesGroup):
        leafFolder = os.path.join("coursework","gameData","graphics","leaves")
        leafFiles = [f"{i}.png" for i in range(5)]
        for _ in range(random.randint(5,8)):
            leafPath = os.path.join(leafFolder, random.choice(leafFiles))
            if os.path.exists(leafPath):
                leafSurf = pygame.image.load(leafPath).convert_alpha()
                pos = (self.rect.centerx + random.randint(-10,10), self.rect.top + random.randint(-10,10))  # spawn slightly around top
                velocity = (random.uniform(-50,50), random.uniform(50,120))
                Particle(pos, leafSurf, particlesGroup, z=self.z, duration=1500, velocity=velocity)
