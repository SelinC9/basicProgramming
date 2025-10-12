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
                        wood_path = "graphics/items/wood.png"
                        wood_img = pygame.image.load(wood_path).convert_alpha()
                        icon = pygame.transform.scale(wood_img, (32, 32))
                    except:
                        icon = pygame.Surface((32, 32))
                        icon.fill((139, 69, 19))  # Brown fallback
                # For stone items, try to load the actual stone image
                elif itemKey == 'stone':
                    try:
                        stone_path = "graphics/items/stone.png"
                        stone_img = pygame.image.load(stone_path).convert_alpha()
                        icon = pygame.transform.scale(stone_img, (32, 32))
                    except:
                        icon = pygame.Surface((32, 32))
                        icon.fill((128, 128, 128))  # Gray fallback
                # For seeds, try to load seed images with proper naming
                elif itemKey in ['kale','parsnips','beans','potatoes','melon','corn','hotPeppers',
                            'tomato','cranberries','pumpkin','berries','onion','beets','artichoke']:
                    try:
                        # Map crop names to seed file names
                        seed_name_map = {
                            'kale': 'kaleSeeds', 'parsnips': 'parsnipSeeds', 'beans': 'beanSeeds',
                            'potatoes': 'potatoSeeds', 'melon': 'melonSeeds', 'corn': 'cornSeeds',
                            'hotPeppers': 'hotPepperSeeds', 'tomato': 'tomatoSeeds', 'cranberries': 'cranberrySeeds',
                            'pumpkin': 'pumpkinSeeds', 'berries': 'berrySeeds', 'onion': 'onionSeeds',
                            'beets': 'beetSeeds', 'artichoke': 'artichokeSeeds'
                        }
                        
                        seed_filename = seed_name_map.get(itemKey, f"{itemKey}Seeds")
                        seed_path = f"graphics/seeds/{seed_filename}.png"
                        
                        if os.path.exists(seed_path):
                            seed_img = pygame.image.load(seed_path).convert_alpha()
                            icon = pygame.transform.scale(seed_img, (32, 32))
                        else:
                            # Fallback: try graphics/items folder
                            item_path = f"graphics/items/{seed_filename}.png"
                            if os.path.exists(item_path):
                                item_img = pygame.image.load(item_path).convert_alpha()
                                icon = pygame.transform.scale(item_img, (32, 32))
                            else:
                                # Ultimate fallback: create colored seed icon
                                icon = pygame.Surface((32, 32), pygame.SRCALPHA)
                                seed_colors = {
                                    'kale': (0, 128, 0), 'parsnips': (255, 255, 200), 'beans': (0, 200, 0),
                                    'potatoes': (255, 248, 220), 'melon': (0, 180, 0), 'corn': (255, 255, 100),
                                    'hotPeppers': (255, 50, 50), 'tomato': (255, 0, 0), 'cranberries': (200, 0, 50),
                                    'pumpkin': (255, 165, 0), 'berries': (100, 0, 200), 'onion': (255, 255, 240),
                                    'beets': (150, 0, 50), 'artichoke': (0, 100, 0)
                                }
                                color = seed_colors.get(itemKey, (200, 200, 200))
                                pygame.draw.ellipse(icon, color, (8, 8, 16, 16))
                                pygame.draw.ellipse(icon, (255, 255, 255), (10, 10, 12, 12), 1)
                                
                    except Exception as e:
                        print(f"Error loading image for {itemKey}: {e}")
                        # Final fallback
                        icon = pygame.Surface((32, 32))
                        icon.fill((200, 200, 200))
            
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

        print(f"Using {item['name']}")

        # Handle seed planting
        if item['name'] in ['kale','parsnips','beans','potatoes','melon','corn','hotPeppers',
                        'tomato','cranberries','pumpkin','berries','onion','beets','artichoke']:
            if self.level and hasattr(self.level, 'plantCrop'):
                success = self.level.plantCrop(item['name'], self.level.player)
                if success:
                    self.removeItem(self.selectedIndex, 1)
                    print(f"Planted {item['name']} seed")
                else:
                    print("Could not plant seed - no tilled soil in front")
            else:
                print("No level reference or plantCrop method")

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