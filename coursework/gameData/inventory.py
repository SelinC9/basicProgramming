import pygame
from settings import *

class Inventory:
    def __init__(self, size=10):
        self.size = size  # max number of items
        self.items = []  # list of items
        self.selectedIndex = 0  # current selected slot
        self.visible = False  # whether the inventory UI is shown

        # load slot images
        self.slotImage = pygame.image.load("coursework\\gameData\\assets\\inventory\\slot.png").convert_alpha()
        self.slotImage = pygame.transform.scale(self.slotImage, (40, 40))  # adjust size
        self.selectedImage = pygame.image.load("coursework\\gameData\\assets\\inventory\\selected.png").convert_alpha()
        self.selectedImage = pygame.transform.scale(self.selectedImage, (44, 44))

        # font for item quantity
        self.font = pygame.font.Font("coursework\\gameData\\assets\\fonts\\Pixellari.ttf", 18)

        # safely load item images now that pygame is initialized
        for key, item in ITEMS.items():
            if 'imagePath' in item:
                try:
                    loaded_img = pygame.image.load(item['imagePath']).convert_alpha()
                    item['image'] = pygame.transform.scale(loaded_img, (32, 32))
                except Exception as e:
                    item['image'] = pygame.Surface((32, 32))
                    item['image'].fill((255, 0, 0))

    def addItem(self, itemKey, quantity=1):
        if itemKey not in ITEMS:
            return False

        # copy the item dictionary to avoid mutating the original
        itemData = ITEMS[itemKey].copy()

        # store quantity for stackable items or materials
        itemData['quantity'] = quantity

        # stackable check
        for i in self.items:
            if i['name'] == itemData['name'] and 'quantity' in i:
                i['quantity'] += quantity
                return True

        if len(self.items) < self.size:
            self.items.append(itemData)
            return True

        return False  # inventory full

    def removeItem(self, index, quantity=1):
        if index < len(self.items):
            item = self.items[index]
            if 'quantity' in item:
                item['quantity'] -= quantity
                if item['quantity'] <= 0:
                    self.items.pop(index)
            else:
                self.items.pop(index)

    def selectNext(self):
        self.selectedIndex = (self.selectedIndex + 1) % self.size

    def selectPrev(self):
        self.selectedIndex = (self.selectedIndex - 1) % self.size

    def useSelectedItem(self):
        if self.selectedIndex < len(self.items):
            item = self.items[self.selectedIndex]
            print(f"Using {item['name']} ({item['type']})")

            if item['type'] == "seed":
                # get player position from the level
                playerPos = self.level.player.get_tile_pos()  # assuming you have this method
                # plant crop at that position
                self.level.plant_crop(item['name'], playerPos)
                # remove one seed from inventory
                self.removeItem(self.selectedIndex, 1)
                print(f"Planted {item['name']} at {playerPos}")

            elif item['type'] == "tool":
                print(f"Swinging {item['name']}")
                # you can add tool effects here later

            elif item['type'] == "material":
                print(f"Used {item['name']}")


    def toggle(self):
        self.visible = not self.visible # toggle visibility

    def draw(self, surface):
        if not self.visible:
            return

        startX = 20
        startY = SCREEN_HEIGHT - 60
        slotWidth = 40
        slotHeight = 40
        slotSpacing = 10  # space between slots
        totalWidth = self.size * (slotWidth + slotSpacing) - slotSpacing

        panelPadding = 10
        panelRect = pygame.Rect(startX - panelPadding, startY - panelPadding, totalWidth + 2*panelPadding, slotHeight + 2*panelPadding)

        # draw shadow first
        shadowOffset = 5
        shadowRect = panelRect.copy()
        shadowRect.topleft = (panelRect.x + shadowOffset, panelRect.y + shadowOffset)
        sShadow = pygame.Surface((shadowRect.width, shadowRect.height), pygame.SRCALPHA)
        sShadow.fill((0, 0, 0, 100))  # black shadow with transparency
        surface.blit(sShadow, shadowRect.topleft)

        # draw light brown panel
        s = pygame.Surface((panelRect.width, panelRect.height), pygame.SRCALPHA)
        s.fill((210, 180, 140, 200))  # light brown with transparency
        surface.blit(s, panelRect.topleft)

        pygame.draw.rect(surface, (160, 120, 70), panelRect, 2)  # darker brown border

        for i in range(self.size):
            slotRect = pygame.Rect(startX + i*(slotWidth + slotSpacing), startY, slotWidth, slotHeight)

            # draw slot shadow
            slotShadow = pygame.Surface((slotWidth, slotHeight), pygame.SRCALPHA)
            slotShadow.fill((0, 0, 0, 60))  # subtle shadow
            surface.blit(slotShadow, (slotRect.x + 2, slotRect.y + 2))  # offset slightly

            # draw selected slot
            if i == self.selectedIndex:
                surface.blit(self.selectedImage, (slotRect.x - 2, slotRect.y - 2))
            else:
                surface.blit(self.slotImage, slotRect.topleft)

            # draw item image
            if i < len(self.items):
                surface.blit(self.items[i]['image'], (slotRect.x + 4, slotRect.y + 4))

                # draw quantity if exists
                if 'quantity' in self.items[i] and self.items[i]['quantity'] > 1:
                    qtyText = self.font.render(str(self.items[i]['quantity']), True, (255, 255, 255))
                    surface.blit(qtyText, (slotRect.right - qtyText.get_width(), slotRect.bottom - qtyText.get_height()))
