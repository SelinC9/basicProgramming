import pygame
import os
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import *
from overlay import Overlay
from shop import Shop
from saveSystem import SaveSystem

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface() #main display surface

        self.untiledSoil = pygame.transform.smoothscale(
            pygame.image.load('graphics/soil/untiled.png').convert_alpha(), #load and scale soil images
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y)) # scale size
        )
        self.tilledSoilImage = pygame.transform.smoothscale(    
            pygame.image.load('graphics/soil/tilled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        ) # scale size

        # sprite groups
        self.allSprites = CameraGroup() #camera group for all sprites
        self.soilTiles = pygame.sprite.Group() #group for soil tiles 
        self.collisionSprites = pygame.sprite.Group() #group for collision
        self.crops = pygame.sprite.Group() #group for crops
        self.trees = pygame.sprite.Group() #group for trees
        self.particles = pygame.sprite.Group() #group for particles
        self.itemsGroup = pygame.sprite.Group() #group for items

        # wood surface (fallback if missing)
        try:
            woodPath = "graphics/items/wood.png"
            woodSurf = pygame.image.load(woodPath).convert_alpha() #load wood image
            self.woodSurf = pygame.transform.scale(woodSurf, (int(32 * ZOOM_X), int(32 * ZOOM_Y))) #scale wood image
        except Exception:
            surf = pygame.Surface((int(32 * ZOOM_X), int(32 * ZOOM_Y)), pygame.SRCALPHA) #create empty surface
            surf.fill((0, 0, 0, 0)) #make it transparent
            self.woodSurf = surf #use empty surface if loading fails

        # stone surface (fallback if missing) - SMALLER SIZE
        try:
            stonePath = "graphics/items/stone.png"
            stoneSurf = pygame.image.load(stonePath).convert_alpha() #load stone image
            self.stoneSurf = pygame.transform.scale(stoneSurf, (int(24 * ZOOM_X), int(24 * ZOOM_Y))) #scale stone image - smaller size
        except Exception:
            surf = pygame.Surface((int(24 * ZOOM_X), int(24 * ZOOM_Y)), pygame.SRCALPHA) #create empty surface
            surf.fill((0, 0, 0, 0)) #make it transparent
            self.stoneSurf = surf #use empty surface if loading fails

        # map
        self.tmxData = load_pygame('graphics/world/myfarm.tmx') #load tmx map
        mapWidth = self.tmxData.width * self.tmxData.tilewidth #in pixels
        mapHeight = self.tmxData.height * self.tmxData.tileheight #in pixels
        self.mapRect = pygame.Rect(0, 0, mapWidth, mapHeight) #rectangle for map size
        self.allSprites.mapRect = self.mapRect #set map rect for camera group

        self.shop = Shop(self) 
        self.playerAdded = False
        self.setup()

        self.saveSystem = SaveSystem(self) #initialize save system

        #Time system
        from transition import Time
        self.time = Time()

    def getTileInFront(self, player): #get tile coordinates in front of player
        tileX = player.rect.centerx // TILE_SIZE #get tile coordinates
        tileY = player.rect.centery // TILE_SIZE #get tile coordinates
        direction = player.status #player direction
        if "Idle" in direction: 
            direction = direction.replace("Idle", "") #remove idle
        for tool in ["Axe", "Water", "Hoe", "Pickaxe"]: #remove tool from direction
            if direction.endswith(tool): 
                direction = direction[:-len(tool)]
                break
        if direction == "up":
            tileY = tileY - 1
        if direction == "down":
            tileY = tileY + 1
        if direction == "left":
            tileX = tileX - 1
        if direction == "right":
            tileX = tileX + 1
        return int(tileX), int(tileY)

    def tillSoil(self, player):
        tileX, tileY = self.getTileInFront(player) #get tile in front of player
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY): #found tile
                if not tile.tilled: 
                    tile.till()
                return
        pos = (tileX * TILE_SIZE, tileY * TILE_SIZE) #position of new soil tile
        soilTile = SoilTile(pos, groups=[self.allSprites, self.soilTiles], untiledImage=self.untiledSoil, tilledImage=self.tilledSoilImage) #create new soil tile
        soilTile.till()

    def waterSoil(self, targetPos): #targetPos is pixel position
        for tile in self.soilTiles: #check all soil tiles
            if tile.rect.collidepoint(targetPos):
                tile.water()
                break

    def chopTree(self, tileX, tileY):
        # More precise targeting so only check the exact tile
        targetPos = (tileX * TILE_SIZE, tileY * TILE_SIZE)
        targetRect = pygame.Rect(targetPos, (TILE_SIZE, TILE_SIZE))
                
        closestTree = None
        minDistance = float('inf')
        
        for tree in self.trees:
            if tree.alive and not tree.isChopped and tree.rect.colliderect(targetRect):
                # Find the closest tree to the target center
                treeCenter = tree.rect.center
                targetCenter = targetRect.center
                distance = ((treeCenter[0] - targetCenter[0]) ** 2 + 
                        (treeCenter[1] - targetCenter[1]) ** 2) ** 0.5
                
                if distance < minDistance:
                    closestTree = tree
                    minDistance = distance
        
        if closestTree:
            # Call chop with the correct parameter names
            wasChopped = closestTree.chop(
                particlesGroup=self.particles,
                allSpritesGroup=self.allSprites, 
                player=self.player
            )
            
            if wasChopped and closestTree.isChopped: #only if actually chopped
                self.trees.remove(closestTree)
            return True
        
        return False

    def breakRock(self, tileX, tileY):
        # More precise targeting so only check the exact tile
        targetPos = (tileX * TILE_SIZE, tileY * TILE_SIZE)
        targetRect = pygame.Rect(targetPos, (TILE_SIZE, TILE_SIZE))
                
        closestRock = None
        minDistance = float('inf')
        
        # Check both the visible rock sprites and collision sprites
        for sprite in self.allSprites:
            if (hasattr(sprite, 'breakable') and sprite.breakable and 
                sprite.rect.colliderect(targetRect)):
                # Find the closest rock to the target center
                rockCenter = sprite.rect.center
                targetCenter = targetRect.center
                distance = ((rockCenter[0] - targetCenter[0]) ** 2 + 
                        (rockCenter[1] - targetCenter[1]) ** 2) ** 0.5
                
                if distance < minDistance:
                    closestRock = sprite
                    minDistance = distance
        
        if closestRock:
            # Spawn stone items
            numStones = random.randint(1, 2)
            for _ in range(numStones):
                offset_x = random.randint(-15, 15)
                offset_y = random.randint(-15, 15)
                stonePos = (closestRock.rect.centerx + offset_x, closestRock.rect.centery + offset_y)
                Stone(stonePos, self.stoneSurf, [self.allSprites, self.itemsGroup])
            
            # Remove the rock from all groups
            closestRock.kill()
            
            # Also remove any collision sprites at the same position
            for collision_sprite in self.collisionSprites:
                if (collision_sprite.rect.centerx == closestRock.rect.centerx and 
                    collision_sprite.rect.centery == closestRock.rect.centery):
                    collision_sprite.kill()
            
            return True
        
        return False

    def isPlantable(self, tilePos):
        for crop in self.crops:
            if (crop.rect.x // TILE_SIZE, crop.rect.y // TILE_SIZE) == tilePos: #already a crop here
                return False
        return True

    def plantCrop(self, cropName, player):
        tileX, tileY = self.getTileInFront(player) #get tile in front of player
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY): #found tile
                if tile.tilled and self.isPlantable((tileX, tileY)): #can plant here
                    cropPos = (tileX * TILE_SIZE, tileY * TILE_SIZE) #position of crop
                    Crop(cropPos, cropName, [self.allSprites, self.crops])
                    print(f"Planted {cropName} at ({tileX}, {tileY})")
                    return True
                else:
                    if not tile.tilled:
                        print(f"Cannot plant {cropName} - soil not tilled")
                    else:
                        print(f"Cannot plant {cropName} - already occupied")
                    return False
        print(f"No soil tile found at ({tileX}, {tileY})")
        return False
    
    def harvestCrop(self, tileX, tileY):
        targetPos = (tileX * TILE_SIZE, tileY * TILE_SIZE)
        targetRect = pygame.Rect(targetPos, (TILE_SIZE, TILE_SIZE))
        
        for crop in self.crops:
            if (crop.rect.colliderect(targetRect) and crop.fullyGrown):
                crop.harvest()
                success = self.player.inventory.addItem(crop.cropName, random.randint(1, 3))
                if success:
                    print(f"Harvested {crop.cropName}")
                    return True
        return False

    def setup(self):
        mapWidth = self.tmxData.width * self.tmxData.tilewidth #in pixels
        mapHeight = self.tmxData.height * self.tmxData.tileheight #in pixels
        groundSurf = pygame.image.load("graphics/world/myfarm.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(mapWidth * ZOOM_X), int(mapHeight * ZOOM_Y))) #scale to fit
        Generic((0, 0), groundSurf, [self.allSprites], z=LAYERS['ground']) #ground layer
 
        self.spawnObstacles()

        spawnPoint = None
        for obj in self.tmxData.objects:
            if getattr(obj, "objectType", None) == "playerSpawn": #find player spawn point
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y) #scale position
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y) #default spawn if none found

        from player import Player
        self.player = Player(spawnPoint, [self.allSprites], self.collisionSprites, self) #add player
        self.player.setMapBounds(self.mapRect) #set map boundaries
        self.overlay = Overlay(self.player)

    def spawnObstacles(self):
        for x, y, surf in self.tmxData.get_layer_by_name("fence").tiles(): #fence layer
            if surf:
                scaled_surf = pygame.transform.scale(surf, (int(surf.get_width() * ZOOM_X), int(surf.get_height() * ZOOM_Y))) #scale surface
                pos = (x * self.tmxData.tilewidth * ZOOM_X, y * self.tmxData.tileheight * ZOOM_Y) #position
                Generic(pos, scaled_surf, [self.allSprites, self.collisionSprites]) #add to groups
        
        # Get all tree objects
        treeObjects = []
        for obj in self.tmxData.get_layer_by_name("tree"):
            treeObjects.append(obj)
        
        #group pixels that are close together
        treeGroups = []
        usedObjects = set()
        
        # Sort objects by position to make clustering more efficient
        sortedObjects = sorted(treeObjects, key=lambda obj: (obj.y, obj.x))
        
        for i, obj in enumerate(sortedObjects):
            if i in usedObjects:
                continue
                
            # Start a new cluster with this object
            currentCluster = [obj]
            usedObjects.add(i)
            
            # Look for nearby objects (within 32 pixels)
            clusterChanged = True
            while clusterChanged:
                clusterChanged = False
                for j, otherObj in enumerate(sortedObjects):
                    if j in usedObjects:
                        continue
                    
                    # Check if this object is close to any object in the current cluster
                    for clusterObj in currentCluster:
                        distance = ((clusterObj.x - otherObj.x) ** 2 + 
                                (clusterObj.y - otherObj.y) ** 2) ** 0.5
                        
                        if distance < 32:  # 32 pixel radius
                            currentCluster.append(otherObj)
                            usedObjects.add(j)
                            clusterChanged = True
                            break
            
            # Only create trees from clusters that look like actual trees
            if 8 <= len(currentCluster) <= 16:
                treeGroups.append(currentCluster)
        
        # Create tree sprites for each valid cluster
        for cluster in treeGroups:
            self.createTreeFromGroup(cluster)
        
        # Create rocks with proper collision
        for obj in self.tmxData.get_layer_by_name("rock"):
            scaled_surf = pygame.transform.scale(obj.image, (int(obj.image.get_width() * ZOOM_X), int(obj.image.get_height() * ZOOM_Y)))
            # Create one sprite that handles both visibility and collision
            rock = Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), scaled_surf, [self.allSprites, self.collisionSprites])
            rock.breakable = True  # Mark rock as breakable
                
    def createTreeFromGroup(self, group):
        if not group:
            return
        
        # Calculate the bounding box that contains all objects
        minX = min(obj.x for obj in group)
        minY = min(obj.y for obj in group)
        maxX = max(obj.x + (obj.width if hasattr(obj, 'width') else 16) for obj in group)
        maxY = max(obj.y + (obj.height if hasattr(obj, 'height') else 16) for obj in group)
        
        # Add some padding to the bounding box
        padding = 10
        width = max(50, maxX - minX + padding)
        height = max(70, maxY - minY + padding)
        
        # Calculate center position for the tree
        centerX = minX + (maxX - minX) / 2
        centerY = minY + (maxY - minY) / 2
        
        # Create a surface for the combined tree
        treeSurface = pygame.Surface((width, height), pygame.SRCALPHA)
        treeSurface.fill((0, 0, 0, 0))
        
        # Draw all objects onto the tree surface, centered
        for obj in group:
            xOffset = obj.x - minX + padding // 2
            yOffset = obj.y - minY + padding // 2
            treeSurface.blit(obj.image, (xOffset, yOffset))
        
        # Scale the tree surface
        scaled_tree_surface = pygame.transform.scale(treeSurface, (int(width * ZOOM_X), int(height * ZOOM_Y)))
        
        # Create the tree sprite at the calculated center
        tree = Tree(
            pos=(centerX * ZOOM_X - (width * ZOOM_X) / 2, centerY * ZOOM_Y - (height * ZOOM_Y) / 2),
            surf=scaled_tree_surface,
            groups=[self.allSprites, self.trees],
            name='tree',
            playerAdded=self.playerAdded
        )
        
        # Create one collision hitbox for the entire tree
        trunkWidth = int(tree.rect.width)
        trunkHeight = int(tree.rect.height)
        
        # Calculate hitbox position - centered on the tree
        hitboxX = tree.rect.centerx - trunkWidth // 2
        hitboxY = tree.rect.centery - trunkHeight // 2
        
        # Create hitbox sprite (invisible collision only)
        hitboxSurf = pygame.Surface((trunkWidth, trunkHeight))
        hitboxSurf.fill((0, 0, 0))
        hitboxSurf.set_alpha(0)  # Completely invisible
        
        hitboxSprite = Generic(
            (hitboxX, hitboxY),
            hitboxSurf,
            [self.collisionSprites],
            z=LAYERS['main']
        )
        tree.hitboxSprite = hitboxSprite

    def run(self, deltaTime):
        self.allSprites.update(deltaTime)

        shouldAutoSave = self.time.update(deltaTime)
        if shouldAutoSave:
            print("Auto-saving game...")
            self.saveSystem.saveGame()

        self.time.update(deltaTime)  # Update time system
        self.crops.update(deltaTime)
        self.particles.update(deltaTime)
        self.trees.update(deltaTime)
        self.itemsGroup.update(deltaTime)

        keys = pygame.key.get_pressed() #get key states
        for sprite in [s for s in self.allSprites if getattr(s, 'pickup', False)]: #only items that can be picked up
            if self.player.rect.colliderect(sprite.rect) and keys[pygame.K_f]: #player touching item and pressing F
                added = self.player.inventory.addItem(sprite.pickupKey, 1, getattr(sprite, 'icon', None)) #add to inventory
                if added:
                    sprite.kill()

        if keys[pygame.K_F5]: #save game
            self.saveSystem.saveGame()
        if keys[pygame.K_F9]: #load game
            self.saveSystem.loadGame()

        self.allSprites.customisedDraw(self.player) #draw with camera
        self.overlay.display()
        self.time.draw()  # Draw time overlay
        self.player.inventory.draw(self.displaySurface)
        self.shop.draw()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.mapRect = pygame.Rect(0, 0, 0, 0) #to be set later
        self.offset = pygame.math.Vector2(0, 0) #camera offset
        self.displaySurface = pygame.display.get_surface() #main display surface

    def customisedDraw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2 #center camera on player
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2 #center camera on player
        self.offset.x = max(0, min(self.offset.x, self.mapRect.width - SCREEN_WIDTH)) #clamp to map boundaries
        self.offset.y = max(0, min(self.offset.y, self.mapRect.height - SCREEN_HEIGHT)) #clamp to map boundaries
        
        for sprite in sorted(self.sprites(), key=lambda spr: spr.z): #draw in order of z
            offsetPos = sprite.rect.topleft - self.offset #apply offset
            self.displaySurface.blit(sprite.image, offsetPos) #draw sprite