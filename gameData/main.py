import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from level import Level
from inventory import Inventory

class MainGame:
    def __init__(self):
        pygame.init()  # Initialize Pygame

        self.windowScreen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Witherford")  # Game title

        self.level = Level()

        # Load and scale background image
        self.backgroundImage = pygame.image.load("graphics/background/0.png").convert_alpha()
        self.backgroundImage = pygame.transform.scale(
            self.backgroundImage, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Load fonts
        self.font = pygame.font.Font("assets/fonts/Pixellari.ttf", 120)
        self.smallFont = pygame.font.Font("assets/fonts/Pixellari.ttf", 40)

    def menu(self):
        while True:
            self.windowScreen.blit(self.backgroundImage, (0, 0))

            # Title
            titleText = self.font.render("Witherford", True, (255, 255, 255))
            self.windowScreen.blit(
                titleText,
                (SCREEN_WIDTH // 2 - titleText.get_width() // 2,
                 SCREEN_HEIGHT // 2 - titleText.get_height() // 2 - 50),
            )

            mousePos = pygame.mouse.get_pos()

            # Buttons
            choice = self.drawButton("New Game", SCREEN_HEIGHT // 2 + 50, mousePos,
                                     highlightColor=(150, 200, 255), defaultColor=(100, 149, 245))
            if choice == "clicked":
                return "new"

            choice = self.drawButton("Load Game", SCREEN_HEIGHT // 2 + 100, mousePos,
                                     highlightColor=(150, 200, 255), defaultColor=(100, 149, 245))
            if choice == "clicked":
                return "load"

            choice = self.drawButton("Press Escape to Exit", SCREEN_HEIGHT // 2 + 150, mousePos,
                                     highlightColor=(255, 100, 100), defaultColor=(200, 60, 60))
            if choice == "clicked":
                pygame.quit()
                sys.exit()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.checkButtonClick("New Game", SCREEN_HEIGHT // 2 + 50, mousePos):
                        return "new"
                    elif self.checkButtonClick("Load Game", SCREEN_HEIGHT // 2 + 100, mousePos):
                        return "load"
                    elif self.checkButtonClick("Press Escape to Exit", SCREEN_HEIGHT // 2 + 150, mousePos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            self.clock.tick(60)

    def drawButton(self, text, yPos, mousePos, highlightColor, defaultColor):
        buttonText = self.smallFont.render(text, True, (255, 255, 255))
        buttonRect = buttonText.get_rect(center=(SCREEN_WIDTH // 2, yPos))

        if buttonRect.collidepoint(mousePos):
            pygame.draw.rect(self.windowScreen, highlightColor, buttonRect.inflate(20, 10))
            return "hover"
        else:
            pygame.draw.rect(self.windowScreen, defaultColor, buttonRect.inflate(20, 10))

        self.windowScreen.blit(buttonText, buttonRect)
        return "idle"

    def checkButtonClick(self, text, yPos, mousePos):
        buttonText = self.smallFont.render(text, True, (255, 255, 255))
        buttonRect = buttonText.get_rect(center=(SCREEN_WIDTH // 2, yPos))
        return buttonRect.collidepoint(mousePos)

    def run(self):
        self.menu()  # Show menu first
        running = True
        inventory = Inventory()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        inventory.toggle()
                    elif event.key == pygame.K_e:
                        inventory.selectNext()
                    elif event.key == pygame.K_q:
                        inventory.selectPrev()

            deltaTime = self.clock.tick(100) / 1000.0  # Frame delta in seconds
            self.level.run(deltaTime)

            # Handle tree chopping
            for tree in self.level.trees:
                if self.level.player.selectedTool == 'axe' and getattr(self.level.player, 'timers', None):
                    if self.level.player.timers['tool use'].active and self.level.player.rect.colliderect(tree.rect):
                        tree.chop(self.level.particles, self.level.allSprites, self.level.player)

            inventory.draw(self.windowScreen)
            pygame.display.update()


if __name__ == "__main__":
    game = MainGame()
    game.run()