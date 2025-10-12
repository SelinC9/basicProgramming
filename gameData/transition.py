import pygame
from settings import *

class Time:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        # Time tracking
        self.currentTime = 6 * TIME_RATE  # Start at 6:00 AM
        self.dayCount = 1
        self.season = 'spring'
        
        # Overlay surface for day/night effects
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Seasons
        self.seasons = ['spring', 'summer', 'autumn', 'winter']
        self.seasonIndex = 0
        
    @property
    def hour(self):
        return int(self.currentTime // TIME_RATE)  # Convert to integer
    
    @property  
    def minute(self):
        return int(self.currentTime % TIME_RATE)  # Convert to integer
    
    def update(self, dt):
        # Update game time
        self.currentTime += dt / 1000 * TIME_RATE
        
        # Check for new day
        if self.currentTime >= DAY_LENGTH:
            self.currentTime = 0
            self.dayCount += 1
            
            # Change season every 28 days
            if self.dayCount % 28 == 0:
                self.seasonIndex = (self.seasonIndex + 1) % len(self.seasons)
                self.season = self.seasons[self.seasonIndex]
    
    def getTimeColor(self):
        hour = self.hour
        
        # Night (8 PM - 4 AM)
        if hour >= 20 or hour < 4:
            return NIGHT_COLOUR
        # Dawn (4 AM - 6 AM)  
        elif hour < 6:
            progress = (hour - 4) / 2
            alpha = int(100 * (1 - progress))
            return (255, 150, 50, alpha)
        # Dusk (6 PM - 8 PM)
        elif hour >= 18:
            progress = (hour - 18) / 2
            alpha = int(120 * progress)
            return (150, 75, 100, alpha)
        # Day (6 AM - 6 PM)
        else:
            return (0, 0, 0, 0)
    
    def draw(self):
        color = self.getTimeColor()
        if color[3] > 0:
            self.overlay.fill(color)
            self.display_surface.blit(self.overlay, (0, 0))
    
    def getTimeString(self):
        return f"{self.hour:02d}:{self.minute:02d}"
    
    def getDayString(self):
        return f"Day {self.dayCount} - {self.season.capitalize()}"