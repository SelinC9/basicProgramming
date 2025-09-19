import pygame
from settings import LAYERS

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil'] #sets the layer of the soil tile
        self.tilled = False #initially the soil is not tilled
        self.watered = False #initially the soil is not watered

    def till(self):
        if not self.tilled:
            self.tilled = True
            # Change the image to a tilled soil image
            self.image = pygame.image.load("coursework\\gameData\\graphics\\soil\\tilled_soil.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32)) #scale the image to fit the tile size