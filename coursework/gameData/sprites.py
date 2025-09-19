import pygame
from settings import *

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

class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups) #initialise the generic class
        
