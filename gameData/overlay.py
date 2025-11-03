import pygame
import os
from settings import *

class Overlay:
    def __init__(self,player):
        #general setup
        self.displaySurface = pygame.display.get_surface()
        self.player = player

        self.font = pygame.font.Font('assets/fonts/Pixellari.ttf',24) #font for time display

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

        #display time
        moneyBackground = pygame.Rect(15, SCREEN_HEIGHT - 100, 150, 30)
        pygame.draw.rect(self.displaySurface, (101, 67, 33, 200), moneyBackground)
        pygame.draw.rect(self.displaySurface, (160, 120, 70), moneyBackground, 2)

        moneyText = self.font.render(f"Money: {self.player.money}g", True, (210, 180, 140))
        self.displaySurface.blit(moneyText, (25, SCREEN_HEIGHT - 95))

        #draw time in the corner
        if hasattr(self.player.level, 'time'):
            timeText = self.font.render(
                f"{self.player.level.time.getTimeString()}", 
                True, (255, 255, 255))
            
            dayText = self.font.render(
                f"{self.player.level.time.getDayString()}", 
                True, (255, 255, 255))
            
            #position in top right corner without background
            timeRect = timeText.get_rect(topright=(SCREEN_WIDTH - 20, 20))
            self.displaySurface.blit(timeText, timeRect)
            
            dayRect = dayText.get_rect(topright=(SCREEN_WIDTH - 20, 50))
            self.displaySurface.blit(dayText, dayRect)