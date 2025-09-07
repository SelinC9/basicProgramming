import pygame
from settings import *

class Generic(pygame.sprite.Sprite): #generic sprite class
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups) #initialise the sprite class
        self.image = surf #surface of the sprite
        self.rect = self.image.get_rect(topleft = pos) #rectangle of the sprite
        self.z = z