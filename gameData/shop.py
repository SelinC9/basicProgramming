import pygame
from settings import *

class Shop:
    def __init__(self, level):
        self.level = level
        self.displaySurface = pygame.display.get_surface()
        self.visible = False
        self.selectedIndex = 0
        self.mode = 'buy'  # 'buy' or 'sell'
        self.items_per_page = 6
        self.current_page = 0
        
        # Input delay to prevent rapid movement
        self.input_delay = 200
        self.last_input_time = 0
        
        # Items available for purchase
        self.buyItems = [
            {'name': 'wood', 'price': 10, 'description': 'Wood (10g)'},
            {'name': 'stone', 'price': 15, 'description': 'Stone (15g)'},
            {'name': 'kale', 'price': 20, 'description': 'Kale Seeds (20g)'},
            {'name': 'parsnips', 'price': 15, 'description': 'Parsnip Seeds (15g)'},
            {'name': 'beans', 'price': 25, 'description': 'Bean Seeds (25g)'},
            {'name': 'potatoes', 'price': 18, 'description': 'Potato Seeds (18g)'},
            {'name': 'berries', 'price': 30, 'description': 'Berry Seeds (30g)'},
            {'name': 'corn', 'price': 35, 'description': 'Corn Seeds (35g)'},
            {'name': 'hotPeppers', 'price': 28, 'description': 'Hot Pepper Seeds (28g)'},
            {'name': 'melon', 'price': 40, 'description': 'Melon Seeds (40g)'},
            {'name': 'tomato', 'price': 32, 'description': 'Tomato Seeds (32g)'},
            {'name': 'artichoke', 'price': 38, 'description': 'Artichoke Seeds (38g)'},
            {'name': 'beets', 'price': 22, 'description': 'Beet Seeds (22g)'},
            {'name': 'cranberries', 'price': 35, 'description': 'Cranberry Seeds (35g)'},
            {'name': 'pumpkin', 'price': 45, 'description': 'Pumpkin Seeds (45g)'},
            {'name': 'onion', 'price': 20, 'description': 'Onion Seeds (20g)'},
        ]
        
        # Selling prices
        self.sellPrices = {
            'wood': 5, 'stone': 7, 'kale': 10, 'parsnips': 7, 'beans': 12,
            'potatoes': 9, 'berries': 15, 'corn': 17, 'hotPeppers': 14,
            'melon': 20, 'tomato': 16, 'artichoke': 19, 'beets': 11,
            'cranberries': 17, 'pumpkin': 22, 'onion': 10,
        }
        
        # Map crop names to display names for selling (add "Seeds" to crop names)
        self.displayNames = {
            'wood': 'Wood',
            'stone': 'Stone',
            'kale': 'Kale Seeds',
            'parsnips': 'Parsnip Seeds',
            'beans': 'Bean Seeds',
            'potatoes': 'Potato Seeds',
            'berries': 'Berry Seeds',
            'corn': 'Corn Seeds',
            'hotPeppers': 'Hot Pepper Seeds',
            'melon': 'Melon Seeds',
            'tomato': 'Tomato Seeds',
            'artichoke': 'Artichoke Seeds',
            'beets': 'Beet Seeds',
            'cranberries': 'Cranberry Seeds',
            'pumpkin': 'Pumpkin Seeds',
            'onion': 'Onion Seeds',
        }
        
        # Font - CORRECT PATH to assets/fonts
        try:
            print("Loading ThaleahFat font from assets/fonts...")
            self.font = pygame.font.Font("assets/fonts/ThaleahFat.ttf", 32)
            self.smallFont = pygame.font.Font("assets/fonts/ThaleahFat.ttf", 24)
            print("Successfully loaded ThaleahFat font")
        except Exception as e:
            print(f"Error loading ThaleahFat font: {e}")
            try:
                print("Trying Pixellari font from assets/fonts...")
                self.font = pygame.font.Font("assets/fonts/Pixellari.ttf", 32)
                self.smallFont = pygame.font.Font("assets/fonts/Pixellari.ttf", 24)
                print("Successfully loaded Pixellari font")
            except Exception as e2:
                print(f"Error loading Pixellari font: {e2}")
                print("Using system font as fallback")
                self.font = pygame.font.SysFont(None, 32)
                self.smallFont = pygame.font.SysFont(None, 24)

    def can_process_input(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_input_time >= self.input_delay

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.selectedIndex = 0
            self.current_page = 0
            self.last_input_time = pygame.time.get_ticks()

    def selectNext(self):
        if not self.can_process_input():
            return
            
        if self.mode == 'buy':
            total_items = len(self.buyItems)
        else:
            total_items = len(self.level.player.inventory.items)
        
        self.selectedIndex += 1
        if self.selectedIndex >= total_items:
            self.selectedIndex = 0
            self.current_page = 0
        elif self.selectedIndex >= (self.current_page + 1) * self.items_per_page:
            self.current_page += 1
        
        self.last_input_time = pygame.time.get_ticks()

    def selectPrev(self):
        if not self.can_process_input():
            return
            
        if self.mode == 'buy':
            total_items = len(self.buyItems)
        else:
            total_items = len(self.level.player.inventory.items)
        
        self.selectedIndex -= 1
        if self.selectedIndex < 0:
            self.selectedIndex = total_items - 1
            self.current_page = (total_items - 1) // self.items_per_page
        elif self.selectedIndex < self.current_page * self.items_per_page:
            self.current_page -= 1
        
        self.last_input_time = pygame.time.get_ticks()

    def switchMode(self):
        if not self.can_process_input():
            return
            
        self.mode = 'sell' if self.mode == 'buy' else 'buy'
        self.selectedIndex = 0
        self.current_page = 0
        self.last_input_time = pygame.time.get_ticks()

    def toggle(self):
        currentTime = pygame.time.get_ticks()

        if hasattr(self, 'lastToggleTime'):
            if currentTime - self.lastToggleTime < 300:  # 300 ms delay
                return
            
        self.visible = not self.visible
        if self.visible:
            self.selectedIndex = 0
            self.current_page = 0
            self.lastInputTime = currentTime
        
        self.lastToggleTime = currentTime

    def canAfford(self, price):
        return self.level.player.money >= price

    def buyItem(self):
        if not self.can_process_input():
            return False
            
        if self.mode != 'buy' or self.selectedIndex >= len(self.buyItems):
            return False
        
        item = self.buyItems[self.selectedIndex]
        
        if not self.canAfford(item['price']):
            print(f"Cannot afford {item['name']}!")
            return False
        
        self.level.player.money -= item['price']
        success = self.level.player.inventory.addItem(item['name'], 1)
        
        if success:
            print(f"Bought {item['name']} for {item['price']}g")
            self.last_input_time = pygame.time.get_ticks()
            return True
        else:
            self.level.player.money += item['price']
            print("Inventory full!")
            return False

    def sellItem(self):
        if not self.can_process_input():
            return False
            
        if self.mode != 'sell' or not self.level.player.inventory.items:
            return False
        
        if self.selectedIndex >= len(self.level.player.inventory.items):
            return False
        
        item = self.level.player.inventory.items[self.selectedIndex]
        item_name = item['name']
        sell_price = self.sellPrices.get(item_name, 1)
        
        self.level.player.money += sell_price
        self.level.player.inventory.removeItem(self.selectedIndex, 1)
        
        # Use display name for the print message
        display_name = self.displayNames.get(item_name, item_name)
        print(f"Sold {display_name} for {sell_price}g")
        self.last_input_time = pygame.time.get_ticks()
        return True

    def getCurrentPageItems(self):
        if self.mode == 'buy':
            items = self.buyItems
        else:
            items = self.level.player.inventory.items
        
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        return items[start_index:end_index]

    def getItemGlobalIndex(self, page_index):
        return self.current_page * self.items_per_page + page_index

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.displaySurface.blit(overlay, (0, 0))

        window_width = 650
        window_height = 550
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.displaySurface, (210, 180, 140), window_rect)
        pygame.draw.rect(self.displaySurface, (160, 120, 70), window_rect, 4)
        
        title = self.font.render("SHOP", True, (50, 50, 50))
        self.displaySurface.blit(title, (window_x + 20, window_y + 20))
        
        money_text = self.font.render(f"Money: {self.level.player.money}g", True, (50, 50, 50))
        self.displaySurface.blit(money_text, (window_x + window_width - money_text.get_width() - 20, window_y + 20))
        
        buy_color = (255, 255, 0) if self.mode == 'buy' else (200, 200, 200)
        sell_color = (255, 255, 0) if self.mode == 'sell' else (200, 200, 200)
        
        buy_text = self.smallFont.render("[BUY]", True, buy_color)
        sell_text = self.smallFont.render("[SELL]", True, sell_color)
        self.displaySurface.blit(buy_text, (window_x + 20, window_y + 70))
        self.displaySurface.blit(sell_text, (window_x + 120, window_y + 70))
        
        if self.mode == 'buy':
            total_items = len(self.buyItems)
        else:
            total_items = len(self.level.player.inventory.items)
        
        max_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        if max_pages > 1:
            page_text = self.smallFont.render(f"Page {self.current_page + 1}/{max_pages}", True, (50, 50, 50))
            self.displaySurface.blit(page_text, (window_x + window_width - page_text.get_width() - 20, window_y + 70))
        
        item_y = window_y + 120
        current_page_items = self.getCurrentPageItems()
        
        if self.mode == 'buy':
            for i, item in enumerate(current_page_items):
                global_index = self.getItemGlobalIndex(i)
                color = (255, 255, 255) if global_index != self.selectedIndex else (255, 255, 0)
                bg_color = (180, 150, 120) if global_index != self.selectedIndex else (200, 170, 100)
                
                item_rect = pygame.Rect(window_x + 20, item_y, window_width - 40, 45)
                pygame.draw.rect(self.displaySurface, bg_color, item_rect)
                pygame.draw.rect(self.displaySurface, (160, 120, 70), item_rect, 2)
                
                item_text = self.smallFont.render(item['description'], True, color)
                self.displaySurface.blit(item_text, (window_x + 30, item_y + 10))
                
                if self.canAfford(item['price']):
                    afford_text = self.smallFont.render("✓ Can Buy", True, (0, 255, 0))
                else:
                    afford_text = self.smallFont.render("✗ Too Expensive", True, (255, 0, 0))
                self.displaySurface.blit(afford_text, (window_x + window_width - afford_text.get_width() - 30, item_y + 10))
                
                item_y += 55
                
        else:
            if not current_page_items:
                no_items = self.smallFont.render("No items to sell!", True, (200, 200, 200))
                self.displaySurface.blit(no_items, (window_x + 30, item_y + 10))
            else:
                for i, item in enumerate(current_page_items):
                    global_index = self.getItemGlobalIndex(i)
                    color = (255, 255, 255) if global_index != self.selectedIndex else (255, 255, 0)
                    bg_color = (180, 150, 120) if global_index != self.selectedIndex else (200, 170, 100)
                    
                    item_rect = pygame.Rect(window_x + 20, item_y, window_width - 40, 45)
                    pygame.draw.rect(self.displaySurface, bg_color, item_rect)
                    pygame.draw.rect(self.displaySurface, (160, 120, 70), item_rect, 2)
                    
                    # Item name and quantity - USE DISPLAY NAME
                    quantity = item.get('quantity', 1)
                    sell_price = self.sellPrices.get(item['name'], 1)
                    display_name = self.displayNames.get(item['name'], item['name'])
                    item_text = self.smallFont.render(f"{display_name} x{quantity} - {sell_price}g each", True, color)
                    self.displaySurface.blit(item_text, (window_x + 30, item_y + 10))
                    
                    item_y += 55

        instructions = self.smallFont.render(
            "W/S: Select|SPACE: Buy/Sell|TAB: Switch Mode|ESC: Close", 
            True, (50, 50, 50)
        )
        self.displaySurface.blit(instructions, (window_x + 20, window_y + window_height - 40))