import json
import os
import pygame
from settings import *

class SaveSystem:
    def __init__(self, level):
        self.level = level
        self.saveDirectory = "saves"
        self.currentSlot = 1
        self.ensureSaveDirectory()

    def ensureSaveDirectory(self):
        if not os.path.exists(self.saveDirectory):
            os.makedirs(self.saveDirectory)

    def getSaveFilePath(self, slot=None):
        if slot is None:
            slot = self.currentSlot
        return os.path.join(self.saveDirectory, f"save_slot_{slot}.json")

    def saveGame(self, slot=None):
        if slot:
            self.currentSlot = slot
            
        try:
            saveData = {
                'player': {
                    'position': {
                        'x': self.level.player.rect.centerx,
                        'y': self.level.player.rect.centery
                    },
                    'money': self.level.player.money,
                    'inventory': self.getInventoryData()
                },
                'farm': {
                    'soilTiles': self.getSoilData(),
                    'crops': self.getCropData(),
                    'trees': self.getTreeData(),
                    'items': self.getItemData()
                },
                'time': {
                    'currentTime': getattr(self.level.time, 'currentTime', 0),
                    'dayCount': getattr(self.level.time, 'dayCount', 1),
                    'season': getattr(self.level.time, 'season', 'spring')
                },
                'metadata': {
                    'slot': self.currentSlot,
                    'timestamp': pygame.time.get_ticks(),
                    'dayCount': getattr(self.level.time, 'dayCount', 1),
                    'season': getattr(self.level.time, 'season', 'spring')
                }
            }

            savePath = self.getSaveFilePath(self.currentSlot)
            with open(savePath, 'w') as f:
                json.dump(saveData, f, indent=2)
            
            print(f"Game saved successfully to slot {self.currentSlot}!")
            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def loadGame(self, slot=None):
        if slot:
            self.currentSlot = slot
            
        try:
            savePath = self.getSaveFilePath(self.currentSlot)
            if not os.path.exists(savePath):
                print(f"No save file found in slot {self.currentSlot}!")
                return False

            with open(savePath, 'r') as f:
                saveData = json.load(f)

            # Load player data
            self.loadPlayerData(saveData['player'])
            
            # Load farm data
            self.loadFarmData(saveData['farm'])
            
            # Load time data
            self.loadTimeData(saveData['time'])
            
            print(f"Game loaded successfully from slot {self.currentSlot}!")
            return True

        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def getSaveSlotsInfo(self):
        slotsInfo = []
        for slot in range(1, 4):  # 3 save slots
            savePath = self.getSaveFilePath(slot)
            slotInfo = {
                'slot': slot,
                'exists': os.path.exists(savePath),
                'filePath': savePath
            }
            
            if slotInfo['exists']:
                try:
                    with open(savePath, 'r') as f:
                        saveData = json.load(f)
                    slotInfo['dayCount'] = saveData['metadata']['dayCount']
                    slotInfo['season'] = saveData['metadata']['season']
                    slotInfo['timestamp'] = saveData['metadata']['timestamp']
                except:
                    slotInfo['exists'] = False
            
            slotsInfo.append(slotInfo)
        
        return slotsInfo

    def deleteSave(self, slot):
        savePath = self.getSaveFilePath(slot)
        if os.path.exists(savePath):
            os.remove(savePath)
            print(f"Save slot {slot} deleted!")
            return True
        return False

    def getInventoryData(self):
        inventoryData = []
        for item in self.level.player.inventory.items:
            itemData = {
                'name': item['name'],
                'quantity': item.get('quantity', 1)
            }
            inventoryData.append(itemData)
        return inventoryData

    def getSoilData(self):
        soilData = []
        for soil in self.level.soilTiles:
            soilData.append({
                'position': {
                    'x': soil.rect.x,
                    'y': soil.rect.y
                },
                'tilled': soil.tilled
            })
        return soilData

    def getCropData(self):
        cropData = []
        for crop in self.level.crops:
            cropData.append({
                'position': {
                    'x': crop.rect.x,
                    'y': crop.rect.y
                },
                'type': crop.cropName,
                'stage': crop.stage,
                'growthProgress': crop.elapsedTime,
                'fullyGrown': crop.fullyGrown
            })
        return cropData

    def getTreeData(self):
        treeData = []
        for tree in self.level.trees:
            treeData.append({
                'position': {
                    'x': tree.rect.x,
                    'y': tree.rect.y
                },
                'health': tree.health,
                'alive': tree.alive
            })
        return treeData

    def getItemData(self):
        itemData = []
        for item in self.level.itemsGroup:
            if hasattr(item, 'pickupKey'):
                itemData.append({
                    'position': {
                        'x': item.rect.x,
                        'y': item.rect.y
                    },
                    'type': item.pickupKey
                })
        return itemData

    def loadPlayerData(self, playerData):
        # Set player position
        pos = playerData['position']
        self.level.player.rect.center = (pos['x'], pos['y'])
        
        # Set player money
        self.level.player.money = playerData['money']
        
        # Clear and reload inventory
        self.level.player.inventory.items = []
        for itemData in playerData['inventory']:
            self.level.player.inventory.addItem(
                itemData['name'], 
                itemData.get('quantity', 1)
            )

    def loadFarmData(self, farmData):
        # Clear existing farm objects
        self.clearFarmObjects()
        
        # Load soil tiles
        for soilData in farmData['soilTiles']:
            pos = soilData['position']
            self.createSoilTile((pos['x'], pos['y']), soilData['tilled'])
        
        # Load crops
        for cropData in farmData['crops']:
            pos = cropData['position']
            self.createCrop((pos['x'], pos['y']), cropData)
        
        # Load items on ground
        for itemData in farmData['items']:
            pos = itemData['position']
            self.createGroundItem((pos['x'], pos['y']), itemData['type'])

    def loadTimeData(self, timeData):
        if hasattr(self.level, 'time'):
            self.level.time.currentTime = timeData['currentTime']
            self.level.time.dayCount = timeData['dayCount']
            self.level.time.season = timeData['season']

    def clearFarmObjects(self):
        for soil in self.level.soilTiles:
            soil.kill()
        for crop in self.level.crops:
            crop.kill()
        for item in self.level.itemsGroup:
            item.kill()

    def createSoilTile(self, pos, tilled):
        from sprites import SoilTile
        soil = SoilTile(
            pos, 
            groups=[self.level.allSprites, self.level.soilTiles],
            untiledImage=self.level.untiledSoil,
            tilledImage=self.level.tilledSoilImage
        )
        if tilled:
            soil.till()

    def createCrop(self, pos, cropData):
        from sprites import Crop
        crop = Crop(pos, cropData['type'], [self.level.allSprites, self.level.crops])
        crop.stage = cropData['stage']
        crop.elapsedTime = cropData['growthProgress']
        crop.fullyGrown = cropData['fullyGrown']
        
        # Update crop image to correct growth stage
        if crop.growthStages and crop.stage < len(crop.growthStages):
            crop.image = crop.growthStages[crop.stage]

    def createGroundItem(self, pos, itemType):
        if itemType == 'wood':
            from sprites import Wood
            Wood(pos, self.level.woodSurf, [self.level.allSprites, self.level.itemsGroup])
        elif itemType == 'stone':
            from sprites import Stone
            Stone(pos, self.level.stoneSurf, [self.level.allSprites, self.level.itemsGroup])