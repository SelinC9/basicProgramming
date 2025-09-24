import pygame
import os
from settings import *

class Overlay:
    def __init__(self,player):
        #general setup
        self.displaySurface = pygame.display.get_surface()
        self.player = player

        #paths
        overlayPath = 'coursework\\gameData\\graphics\\overlay\\'
        iconSize = (64,64) #changeable icon size

        #tools
        self.toolsSurf = {}
        for tool in player.tools:
            path = f'{overlayPath}{tool}.png' #path to the tool image
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha() #load the image and convert it to a surface
                self.toolsSurf[tool] = pygame.transform.scale(image, iconSize) #scale the image to the icon size
            else:
                self.toolsSurf[tool] = pygame.Surface(iconSize, pygame.SRCALPHA)  #placeholder surface if image not found

        #seeds
        self.seedsSurf = {}
        for seed in player.seeds:
            path = f'{overlayPath}{seed}.png' #path to the seed image
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                self.seedsSurf[seed] = pygame.transform.scale(image, iconSize) #scale the image to the icon size
            else:
                self.seedsSurf[seed] = pygame.Surface(iconSize, pygame.SRCALPHA) #placeholder surface if image not found

    def display(self):
        #tools
        toolSurf = self.toolsSurf[self.player.selectedTool] #get the surface of the selected tool
        toolRect = toolSurf.get_rect(midbottom = OVERLAY_POSITIONS['tool']) #get the rectangle of the tool surface
        self.displaySurface.blit(toolSurf,toolRect) #blit the tool surface to the display surface

        #seeds
        seedSurf = self.seedsSurf[self.player.selectedSeed] #get the surface of the selected seed
        seedRect = seedSurf.get_rect(midbottom = OVERLAY_POSITIONS['seed']) #get the rectangle of the seed surface
        self.displaySurface.blit(seedSurf,seedRect) #blit the seed surface to the display surface