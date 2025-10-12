import pygame
import os
from settings import *

class Inventory:
    def __init__(self, size=10, level=None):
        self.size = size
        self.items = []
        self.selectedIndex = 0
        self.visible = False
        self.level = level

        # Inventory slot graphics
        try:
            self.slotImage = pygame.image.load("assets/inventory/slot.png").convert_alpha()
            self.slotImage = pygame.transform.scale(self.slotImage, (40, 40))
        except Exception:
            self.slotImage = pygame.Surface((40, 40))
            self.slotImage.fill((100, 100, 100))

        try:
            self.selectedImage = pygame.image.load("assets/inventory/selected.png").convert_alpha()
            self.selectedImage = pygame.transform.scale(self.selectedImage, (44, 44))
        except Exception:
            self.selectedImage = pygame.Surface((44, 44))
            self.selectedImage.fill((200, 200, 0))

        # Font
        try:
            self.font = pygame.font.Font("graphics/fonts/Pixellari.ttf", 18)
        except Exception:
            self.font = pygame.font.SysFont(None, 18)

        # Load item images safely
        for key, item in ITEMS.items():
            if 'imagePath' in item:
                try:
                    loadedImg = pygame.image.load(item['imagePath']).convert_alpha()
                    item['image'] = pygame.transform.scale(loadedImg, (32, 32))
                except Exception:
                    item['image'] = pygame.Surface((32, 32))
                    item['image'].fill((255, 0, 0))

    # Add item to inventory
    def addItem(self, itemKey, quantity=1, icon=None):
        for i, item in enumerate(self.items):
            if item['name'] == itemKey:
                self.items[i]['quantity'] += quantity
                print(f"Added {quantity} {itemKey}. Total: {self.items[i]['quantity']}")
                return True
        
        # Add new item if there's space
        if len(self.items) < self.size:
            if icon is None:
                # For wood items, try to load the actual wood image
                if itemKey == 'wood':
                    try:
                        woodPath = "graphics/items/wood.png"
                        woodImg = pygame.image.load(woodPath).convert_alpha()
                        icon = pygame.transform.scale(woodImg, (32, 32))
                    except:
                        icon = pygame.Surface((32, 32))
                        icon.fill((139, 69, 19))  # Brown fallback
                # For stone items, try to load the actual stone image
                elif itemKey == 'stone':
                    try:
                        stonePath = "graphics/items/stone.png"
                        stoneSurf = pygame.image.load(stonePath).convert_alpha() #load stone image
                        # Scale to a reasonable size for world items - much smaller
                        base_width, base_height = stoneSurf.get_size()
                        target_width = max(16, int(base_width * ZOOM_X * 0.5))  # 50% smaller
                        target_height = max(16, int(base_height * ZOOM_Y * 0.5))
                        self.stoneSurf = pygame.transform.smoothscale(stoneSurf, (target_width, target_height)) #smooth scaling
                    except Exception:
                        # Create a better fallback stone
                        surf = pygame.Surface((int(20 * ZOOM_X), int(20 * ZOOM_Y)), pygame.SRCALPHA)
                        # Draw a simple stone shape
                        pygame.draw.ellipse(surf, (120, 120, 120), (2, 2, int(16 * ZOOM_X), int(16 * ZOOM_Y)))
                        pygame.draw.ellipse(surf, (100, 100, 100), (4, 4, int(12 * ZOOM_X), int(12 * ZOOM_Y)))
                        self.stoneSurf = surf
                
            item_data = {
                'name': itemKey,
                'quantity': quantity,
                'image': icon
            }
            self.items.append(item_data)
            print(f"Added {itemKey} to inventory. Total: {quantity}")
            return True
        
        print(f"Inventory full! Could not add {itemKey}")
        return False

    # Remove item
    def removeItem(self, index, quantity=1):
        if index < len(self.items):
            item = self.items[index]
            if 'quantity' in item:
                item['quantity'] -= quantity
                if item['quantity'] <= 0:
                    self.items.pop(index)
            else:
                self.items.pop(index)

    # Cycle through slots
    def selectNext(self):
        self.selectedIndex = (self.selectedIndex + 1) % self.size

    def selectPrev(self):
        self.selectedIndex = (self.selectedIndex - 1) % self.size

    # Use the selected item
    def useSelectedItem(self):
        if self.selectedIndex >= len(self.items):
            return
        item = self.items[self.selectedIndex]

        print(f"Using {item['name']} ({item.get('type', 'unknown')})")

        if item.get('type') == "seed" and self.level:
            self.level.plantSeed(self.level.player.targetPos, item['name'])
            self.removeItem(self.selectedIndex, 1)

        elif item.get('type') == "tool":
            print(f"Swinging {item['name']}")

        elif item.get('type') == "material":
            print(f"Used {item['name']}")

    # Toggle visibility
    def toggle(self):
        self.visible = not self.visible

    # Draw inventory UI
    def draw(self, surface):
        if not self.visible:
            return

        startX = 20
        startY = SCREEN_HEIGHT - 60
        slotWidth = 40
        slotHeight = 40
        slotSpacing = 10
        totalWidth = self.size * (slotWidth + slotSpacing) - slotSpacing

        panelPadding = 10
        panelRect = pygame.Rect(startX - panelPadding, startY - panelPadding,
                                totalWidth + 2*panelPadding, slotHeight + 2*panelPadding)

        # Shadow
        shadowOffset = 5
        shadowRect = panelRect.copy()
        shadowRect.topleft = (panelRect.x + shadowOffset, panelRect.y + shadowOffset)
        sShadow = pygame.Surface((shadowRect.width, shadowRect.height), pygame.SRCALPHA)
        sShadow.fill((0, 0, 0, 100))
        surface.blit(sShadow, shadowRect.topleft)

        # Panel background
        s = pygame.Surface((panelRect.width, panelRect.height), pygame.SRCALPHA)
        s.fill((210, 180, 140, 200))
        surface.blit(s, panelRect.topleft)
        pygame.draw.rect(surface, (160, 120, 70), panelRect, 2)

        # Slots
        for i in range(self.size):
            slotRect = pygame.Rect(startX + i*(slotWidth + slotSpacing), startY, slotWidth, slotHeight)

            if i == self.selectedIndex:
                surface.blit(self.selectedImage, (slotRect.x - 2, slotRect.y - 2))
            else:
                surface.blit(self.slotImage, slotRect.topleft)

            if i < len(self.items):
                surface.blit(self.items[i]['image'], (slotRect.x + 4, slotRect.y + 4))

                if 'quantity' in self.items[i] and self.items[i]['quantity'] > 1:
                    qtyText = self.font.render(str(self.items[i]['quantity']), True, (255, 255, 255))
                    surface.blit(qtyText, (slotRect.right - qtyText.get_width(),
                                           slotRect.bottom - qtyText.get_height()))