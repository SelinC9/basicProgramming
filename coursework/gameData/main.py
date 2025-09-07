import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT #imports the height and the width
from level import Level #imports the level class

class mainGame:
    def __init__(self):
        pygame.init() #initialise in order to use pygame functions
        self.windowScreen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Witherford") #caption of the game
        self.level = Level()
        self.backgroundImage = pygame.image.load("coursework\\gameData\\graphics\\background\\0.png").convert_alpha() #loads the background image
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (SCREEN_WIDTH, SCREEN_HEIGHT)) #scales the background image to fit the screen

        self.font = pygame.font.Font("coursework\\gameData\\assets\\fonts\\Pixellari.ttf", 80) #loads the font from the assets folder
        self.smallFont = pygame.font.Font("coursework\\gameData\\assets\\fonts\\Pixellari.ttf", 40) #loads the small font from the assets folder

    def menu(self):
        while True:
            self.windowScreen.blit(self.backgroundImage, (0,0)) #fills the screen with the background image

            #drawing the title
            titleText = self.font.render("Witherford", True, (255, 255, 255)) #renders the title text
            titleRect = titleText.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)) #it won't be used but just in case
            self.windowScreen.blit(titleText, (SCREEN_WIDTH // 2 - titleText.get_width() // 2, SCREEN_HEIGHT // 2 - titleText.get_height() // 2 - 50)) #blits the title text to the screen
            mousePos = pygame.mouse.get_pos()

            #drawing the new game button
            newStartText = self.smallFont.render("New Game", True, (255, 255, 255)) #renders the start text
            newStartRect = newStartText.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)) #gets the rectangle of the start text (can change it later)
            if newStartRect.collidepoint(mousePos): #checks if the mouse is over the new game button
                pygame.draw.rect(self.windowScreen, (150, 200, 255), newStartRect.inflate(20, 10)) #draws a rectangle around the text
            else:
                pygame.draw.rect(self.windowScreen, (100, 149, 245), newStartRect.inflate(20, 10)) #draws a rectangle around the text
            self.windowScreen.blit(newStartText, newStartRect)

            #drawing the load game button
            loadStartText = self.smallFont.render("Load Game", True, (255, 255, 255)) #renders the start text
            loadStartRect = loadStartText.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)) #gets the rectangle of the start text (can change it later)
            if loadStartRect.collidepoint(mousePos): #checks if the mouse is over the button
                pygame.draw.rect(self.windowScreen, (150, 200, 255), loadStartRect.inflate(20, 10)) #draws a rectangle around the text
            else:
                pygame.draw.rect(self.windowScreen, (100, 149, 245), loadStartRect.inflate(20, 10)) #draws a rectangle around the text
            self.windowScreen.blit(loadStartText, loadStartRect)

            #drawing the exit button
            exitText = self.smallFont.render("Press Escape to Exit", True, (255, 255, 255)) #renders the exit text
            exitRect = exitText.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)) #gets the rectangle of the exit text
            if exitRect.collidepoint(mousePos): #checks if the mouse is over the exit button
                pygame.draw.rect(self.windowScreen, (255, 100, 100), exitRect.inflate(20, 10)) #draws a rectangle around the text
            else:
                pygame.draw.rect(self.windowScreen, (200, 60, 60), exitRect.inflate(20, 10))
            self.windowScreen.blit(exitText, exitRect)

            #check if the game is closed or anything is pressed (event handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return #if the enter key is pressed, return to the main game loop
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos() #gets the position of the mouse
                    if newStartRect.collidepoint(mousePos): #checks if the mouse is over the start
                        return "new"
                    elif loadStartRect.collidepoint(mousePos): #checks if the mouse is over the load
                        return "load"
                    elif exitRect.collidepoint(mousePos): #checks if the mouse is over the exit
                        pygame.quit()
                        sys.exit()

            pygame.display.update() #updates the display
            self.clock.tick(60) #limits the frame rate to 60 FPS

    def run(self):
        self.menu() #show the menu before starting the game
        running = True
        #GAME LOOP
        while running:
            #CHECKS IF THE GAME IS CLOSED
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                    
            deltaTime = self.clock.tick(100) / 1000.0 #frame rate is 100 FPS, deltaTime is the time between frames in seconds
            self.level.run(deltaTime)
            #deltaTime is the time between frames
            pygame.display.update() #updates the display

#checks if we are in the main file and create an object from the class
if __name__ == "__main__":
    game = mainGame()
    game.run()