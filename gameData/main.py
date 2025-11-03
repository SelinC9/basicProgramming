import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, ZOOM_X, ZOOM_Y, TIME_RATE
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
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load fonts
        self.font = pygame.font.Font("assets/fonts/Pixellari.ttf", 120)
        self.smallFont = pygame.font.Font("assets/fonts/Pixellari.ttf", 40)

    def menu(self):
        while True:
            self.windowScreen.blit(self.backgroundImage, (0, 0))

            # Title
            titleText = self.font.render("Witherford", True, (255, 255, 255)) #renders the title text
            self.windowScreen.blit(titleText, (SCREEN_WIDTH // 2 - titleText.get_width() // 2, SCREEN_HEIGHT // 4 - titleText.get_height() // 2))
            mousePos = pygame.mouse.get_pos()
            
            # Buttons
            choice = self.drawButton("New Game", SCREEN_HEIGHT // 2 - 60, mousePos, highlightColor=(150, 200, 255), defaultColor=(100, 149, 245))
            if choice == "clicked":
                return self.newGameMenu()

            choice = self.drawButton("Load Game", SCREEN_HEIGHT // 2, mousePos, highlightColor=(150, 200, 255), defaultColor=(100, 149, 245))
            if choice == "clicked":
                return self.loadGameMenu()

            choice = self.drawButton("Press Escape to Exit", SCREEN_HEIGHT // 2 + 60, mousePos, highlightColor=(255, 100, 100), defaultColor=(200, 60, 60))
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
                    if self.checkButtonClick("New Game", SCREEN_HEIGHT // 2 - 60, mousePos):
                        return self.newGameMenu()
                    elif self.checkButtonClick("Load Game", SCREEN_HEIGHT // 2, mousePos):
                        return self.loadGameMenu()
                    elif self.checkButtonClick("Press Escape to Exit", SCREEN_HEIGHT // 2 + 60, mousePos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            self.clock.tick(60)

    def newGameMenu(self):
        while True:
            self.windowScreen.blit(self.backgroundImage, (0, 0))

            # Title
            titleText = self.font.render("New Game", True, (255, 255, 255))
            self.windowScreen.blit(titleText,
                (SCREEN_WIDTH // 2 - titleText.get_width() // 2,
                 SCREEN_HEIGHT // 6),
            )

            mousePos = pygame.mouse.get_pos()
            slotsInfo = self.level.saveSystem.getSaveSlotsInfo()

            # Draw save slots
            slotButtons = []
            for i, slotInfo in enumerate(slotsInfo):
                yPos = SCREEN_HEIGHT // 3 + i * 80
                
                if slotInfo['exists']:
                    slotText = f"Slot {slotInfo['slot']}: Day {slotInfo.get('dayCount', 1)} - {slotInfo.get('season', 'Spring')}"
                    buttonColor = (200, 200, 100)  # Yellow for existing save
                else:
                    slotText = f"Slot {slotInfo['slot']}: Empty"
                    buttonColor = (100, 149, 245)  # Blue for empty slot

                choice = self.drawButton(slotText, yPos, mousePos, highlightColor=(150, 200, 255), defaultColor=buttonColor)
                
                if choice == "clicked":
                    # Start new game in this slot (overwrite if exists)
                    self.level.saveSystem.currentSlot = slotInfo['slot']
                    return "new"

                slotButtons.append((slotText, yPos))

            # Back button
            choice = self.drawButton("Back", SCREEN_HEIGHT - 100, mousePos, highlightColor=(255, 150, 150), defaultColor=(200, 100, 100))
            if choice == "clicked":
                return "back"

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for slotText, yPos in slotButtons:
                        if self.checkButtonClick(slotText, yPos, mousePos):
                            slotNum = int(slotText.split(":")[0].split(" ")[1])
                            self.level.saveSystem.currentSlot = slotNum
                            return "new"
                    
                    if self.checkButtonClick("Back", SCREEN_HEIGHT - 100, mousePos):
                        return "back"

            pygame.display.update()
            self.clock.tick(60)

    def loadGameMenu(self):
        while True:
            self.windowScreen.blit(self.backgroundImage, (0, 0))

            # Title
            titleText = self.font.render("Load Game", True, (255, 255, 255))
            self.windowScreen.blit(
                titleText,
                (SCREEN_WIDTH // 2 - titleText.get_width() // 2,
                 SCREEN_HEIGHT // 6),
            )

            mousePos = pygame.mouse.get_pos()
            slotsInfo = self.level.saveSystem.getSaveSlotsInfo()

            # Draw save slots (only existing ones)
            slotButtons = []
            validSlots = [slot for slot in slotsInfo if slot['exists']]
            
            if not validSlots:
                # No save files message
                noSavesText = self.smallFont.render("No save files found!", True, (255, 255, 255))
                self.windowScreen.blit(noSavesText, (SCREEN_WIDTH // 2 - noSavesText.get_width() // 2, SCREEN_HEIGHT // 2))

            for i, slotInfo in enumerate(validSlots):
                yPos = SCREEN_HEIGHT // 3 + i * 80
                slotText = f"Slot {slotInfo['slot']}: Day {slotInfo.get('dayCount', 1)} - {slotInfo.get('season', 'Spring')}"

                choice = self.drawButton(slotText, yPos, mousePos, highlightColor=(150, 200, 255), defaultColor=(100, 200, 100))
                
                if choice == "clicked":
                    # Load game from this slot
                    if self.level.saveSystem.loadGame(slotInfo['slot']):
                        return "load"
                    else:
                        print(f"Failed to load slot {slotInfo['slot']}")

                slotButtons.append((slotText, yPos))

            # Back button
            choice = self.drawButton("Back", SCREEN_HEIGHT - 100, mousePos, highlightColor=(255, 150, 150), defaultColor=(200, 100, 100))
            if choice == "clicked":
                return "back"

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for slotText, yPos in slotButtons:
                        if self.checkButtonClick(slotText, yPos, mousePos):
                            slotNum = int(slotText.split(":")[0].split(" ")[1])
                            if self.level.saveSystem.loadGame(slotNum):
                                return "load"
                    
                    if self.checkButtonClick("Back", SCREEN_HEIGHT - 100, mousePos):
                        return "back"

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
        menuChoice = self.menu()  # Show menu first and get choice
        running = True
        
        # If new game was chosen, reset the game state
        if menuChoice == "new":
            # Reset player to default position and state
            self.level.player.rect.center = (400 * ZOOM_X, 300 * ZOOM_Y)
            self.level.player.money = 100
            self.level.player.inventory.items = []
            self.level.time.currentTime = 6 * TIME_RATE  # 6:00 AM
            self.level.time.dayCount = 1
            self.level.time.season = 'spring'
            # Clear farm objects for fresh start
            self.level.saveSystem.clearFarmObjects()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Save/Load controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        self.level.saveSystem.saveGame()
                    elif event.key == pygame.K_F9:
                        self.level.saveSystem.loadGame()
                        
                # Inventory controls  
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.level.player.inventory.toggle()
                    elif event.key == pygame.K_e:
                        self.level.player.inventory.selectNext()
                    elif event.key == pygame.K_q:
                        self.level.player.inventory.selectPrev()
                    elif event.key == pygame.K_b:  # Shop control
                        self.level.shop.toggle()
                    
                    # Shop navigation (only if shop is visible)
                    if self.level.shop.visible:
                        if event.key == pygame.K_w:
                            self.level.shop.selectPrev()
                        elif event.key == pygame.K_s:
                            self.level.shop.selectNext()
                        elif event.key == pygame.K_TAB:
                            self.level.shop.switchMode()
                        elif event.key == pygame.K_SPACE:
                            if self.level.shop.mode == 'buy':
                                self.level.shop.buyItem()
                            else:
                                self.level.shop.sellItem()
                        elif event.key == pygame.K_ESCAPE:
                            self.level.shop.visible = False

            deltaTime = self.clock.tick(100) / 1000.0  # Frame delta in seconds
            self.level.run(deltaTime)

            # Handle tree chopping
            for tree in self.level.trees:
                if self.level.player.selectedTool == 'axe' and getattr(self.level.player, 'timers', None):
                    if self.level.player.timers['tool use'].active and self.level.player.rect.colliderect(tree.rect):
                        tree.chop(self.level.particles, self.level.allSprites, self.level.player)

            self.level.player.inventory.draw(self.windowScreen)
            pygame.display.update()


if __name__ == "__main__":
    game = MainGame()
    game.run()