import pygame
import os
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite): #inherits from the sprite class
    def __init__(self, pos, group): #we need the position and the group of the sprite
        super().__init__(group) #pass in the group

        self.importAssets() #import the assets for the player
        #needs to be at the beginning so that the player can use the animations
        self.status = 'downIdle' #default status of the player
        self.frameIndex = 0 #default frame index of the player
        self.z = LAYERS['main']

        #General
        self.image = self.animations[self.status][self.frameIndex]
        self.rect = self.image.get_rect(center = pos) #we are getting the center from the parameter
        
        ####Movement attributes####
        self.direction = pygame.math.Vector2() #by default x = 0 and y = 0
        self.pos = pygame.math.Vector2(self.rect.center) #
        self.speed = 200 #speed of the player (I can change it later)

        #Timers
        self.timers = {
            'tool use': Timer(350,self.useTool), #350 milliseconds for the tool use
            'tool switch': Timer(200), #200 milliseconds for the tool switch
            'seed use': Timer(350,self.useSeed), #350 milliseconds for the tool use
            'seed switch': Timer(200) #200 milliseconds for the tool switch
        }
        
        #tools
        self.tools = ['hoe', 'axe', 'wateringCan'] #list of the tools the player can use  
        self.toolIndex = 0
        self.selectedTool = self.tools[self.toolIndex] #default tool of the player

        #seeds
        self.seeds = ['kale', 'parsnips', 'beans', 'potatoes', 'melon', 'corn', 'hotPeppers', 'tomato', 'cranberries', 'pumpkin', 'berries', 'onion', 'beets', 'artichoke']
        self.seedIndex = 0
        self.selectedSeed = self.seeds[self.seedIndex] #default seed of the player

        # Map boundaries (set externally by Level)
        self.boundary = None

    def setMapBounds(self, rect):
        self.boundary = rect.copy() #creates a copy of the rectangle

    def useTool(self):
        pass

    def useSeed(self):
        pass

    def importAssets(self):
        characterPath = "coursework\\gameData\\graphics\\character\\" #path to the character folder

        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'rightIdle': [], 'leftIdle': [], 'upIdle': [], 'downIdle': [],
                           'rightHoe': [], 'leftHoe': [], 'upHoe': [], 'downHoe': [],
                           'rightAxe': [], 'leftAxe': [], 'upAxe': [], 'downAxe': [],
                           'rightWater': [], 'leftWater': [], 'upWater': [], 'downWater': []}
        #imported from my sprites folder, all the keys correspond with the file names
        for animation in self.animations.keys():
            fullPath = characterPath + animation #correlates with the location of the folders
            print('Importing player animation from:', fullPath) #for testing purposes
            frames = importFolder(fullPath)  # returns a list of surfaces
            self.animations[animation] = frames
        
        for key, value in self.animations.items():
           print(f"{key}: {len(value)} frames, first frame: {value[0] if value else 'None'}") #for testing purposes

    def animate(self, deltaTime):
        self.frameIndex += 10 * deltaTime #changes the frame index based on the time passed
        if self.frameIndex >= len(self.animations[self.status]): #if the frame index is greater than the number of frames in the animation
            self.frameIndex = 0 #resets the frame index to 0
        self.image = self.animations[self.status][int(self.frameIndex)] #changes the image of the player based on the frame index and the status

    def input(self):
        keys = pygame.key.get_pressed() #returns a list with all of the keys pressed

        if not self.timers['tool use'].active: #so if the tool use timer is not active, the player can move
            #Reset movement direction
            self.direction.x = 0
            self.direction.y = 0

            if keys[pygame.K_UP]:
                self.direction.y = -1 #changes the y-coordinate by -1
                self.status = 'up' #changes the status of the player
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1 #changes the y-coordinate by 1
                self.status = 'down' 

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1 #changes the x-coordinate by -1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1 #changes the y-coordinate by 1
                self.status = 'left'
            

            #If no movement detected, switch to idle
            if self.direction.x == 0 and self.direction.y == 0:
                if 'left' in self.status:
                    self.status = 'leftIdle'
                elif 'right' in self.status:
                    self.status = 'rightIdle'
                elif 'up' in self.status:
                    self.status = 'upIdle'
                elif 'down' in self.status:
                    self.status = 'downIdle'

            #tool use
            if keys[pygame.K_SPACE]:
                #timer for the tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2() #so the player can't move while using the tool
                self.frameIndex = 0 #resets the frame index to 0

            #change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate() #activates the tool switch timer
                self.toolIndex += 1 #changes the tool index by 1
                #if tool index is greater than the number of tools, reset it to 0
                self.toolIndex = self.toolIndex if self.toolIndex < len(self.tools) else 0
                self.selectedTool = self.tools[self.toolIndex] #changes the selected tool based on the tool index (using modulo to loop through the list)

            #seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frameIndex = 0
                print('use seed')

            #change seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seedIndex += 1
                self.seedIndex = self.seedIndex if self.seedIndex < len(self.seeds) else 0
                self.selectedSeed = self.seeds[self.seedIndex]
                print(self.selectedSeed)

    def getStatus(self):
        if "up" in self.status:
           base = "up"
        elif "down" in self.status:
           base = "down"
        elif "left" in self.status:
           base = "left"
        else:
              base = "right"

        #if not moving and not using a tool
        if self.direction.magnitude() == 0 and not self.timers['tool use'].active:
            self.status = base + "Idle"

        #if using a tool
        elif self.timers['tool use'].active:
            toolSuffix = self.selectedTool.capitalize() #capitalizes the first letter of the tool Water, Axe, Hoe
            self.status = base + toolSuffix

    def move(self,deltaTime):
        #I need to normalize a vector (so I need to make sure the character moves in speed 1 in every direction)
        if self.direction.magnitude() > 0: #so if the player is moving
            self.direction = self.direction.normalize() #it converts the vector to length

        #move position based on direction
        self.pos.x += self.direction.x * self.speed * deltaTime
        self.pos.y += self.direction.y * self.speed * deltaTime

        #keep player within map boundaries
        if self.boundary:
            half_w = self.rect.width / 2
            half_h = self.rect.height / 2
            min_x = self.boundary.left + half_w
            max_x = self.boundary.right - half_w
            min_y = self.boundary.top + half_h
            max_y = self.boundary.bottom - half_h

        if self.pos.x < min_x: self.pos.x = min_x
        if self.pos.x > max_x: self.pos.x = max_x
        if self.pos.y < min_y: self.pos.y = min_y
        if self.pos.y > max_y: self.pos.y = max_y
        #sync rect with pos
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, deltaTime):
        self.input()
        self.move(deltaTime) #updates the position of the player
        
        #updates the timers
        for timer in self.timers.values():
            timer.update()

        self.getStatus() #updates the status of the player
        self.animate(deltaTime) #updates the animation of the player
