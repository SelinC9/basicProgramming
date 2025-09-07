import pygame
class Timer:
    def __init__(self,duration,func = None): #func is a function that will be called when the timer ends
        self.duration = duration
        self.func = func
        self.startTime = 0
        self.active = False

    def activate(self):
        self.active = True
        self.startTime = pygame.time.get_ticks() #gets the current time in milliseconds


    def deactivate(self):
        self.active = False
        self.startTime = 0

    def update(self):
        currentTime = pygame.time.get_ticks() #it will always get the current time
        if currentTime - self.startTime >= self.duration: #if the current time - the start time is greater than or equal to the duration
            self.deactivate() #deactivates the timer
            if self.func: #so if this function exists
                self.func() #calls the function