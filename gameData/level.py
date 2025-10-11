import pygame
import os
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import *
from overlay import Overlay

ZOOM_X = SCREEN_WIDTH / 1280
ZOOM_Y = SCREEN_HEIGHT / 720

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface()

        self.untiledSoil = pygame.transform.smoothscale(
            pygame.image.load('graphics/soil/untiled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )
        self.tilledSoilImage = pygame.transform.smoothscale(
            pygame.image.load('graphics/soil/tilled.png').convert_alpha(),
            (int(TILE_SIZE * ZOOM_X), int(TILE_SIZE * ZOOM_Y))
        )

        # sprite groups
        self.allSprites = CameraGroup(pygame.Rect(0, 0, 0, 0))
        self.soilTiles = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.crops = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.itemsGroup = pygame.sprite.Group()

        # wood surface (fallback if missing)
        try:
            woodPath = "graphics/items/wood.png"
            woodSurf = pygame.image.load(woodPath).convert_alpha()
            self.woodSurf = pygame.transform.scale(woodSurf, (int(32 * ZOOM_X), int(32 * ZOOM_Y)))
        except Exception:
            surf = pygame.Surface((int(32 * ZOOM_X), int(32 * ZOOM_Y)), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            self.woodSurf = surf

        # map
        self.tmxData = load_pygame('graphics/world/myfarm.tmx')
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        self.mapRect = pygame.Rect(0, 0, mapWidth, mapHeight)
        self.allSprites.mapRect = self.mapRect

        self.playerAdded = False
        self.setup()

    def getTileInFront(self, player):
        tileX = player.rect.centerx // TILE_SIZE
        tileY = player.rect.centery // TILE_SIZE
        direction = player.status
        if "Idle" in direction:
            direction = direction.replace("Idle", "")
        for tool in ["Axe", "Water", "Hoe"]:
            if direction.endswith(tool):
                direction = direction[:-len(tool)]
                break
        if direction == "up":
            tileY -= 1
        if direction == "down":
            tileY += 1
        if direction == "left":
            tileX -= 1
        if direction == "right":
            tileX += 1
        return int(tileX), int(tileY)

    def tillSoil(self, player):
        tileX, tileY = self.getTileInFront(player)
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if not tile.tilled:
                    tile.till()
                return
        pos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
        soilTile = SoilTile(pos,
                            groups=[self.allSprites, self.soilTiles],
                            untiledImage=self.untiledSoil,
                            tilledImage=self.tilledSoilImage)
        soilTile.till()

    def waterSoil(self, targetPos):
        for tile in self.soilTiles:
            if tile.rect.collidepoint(targetPos):
                tile.water()
                break

    def chopTree(self, tileX, tileY):
        # More precise targeting - only check the exact tile
        targetPos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
        targetRect = pygame.Rect(targetPos, (TILE_SIZE * ZOOM_X, TILE_SIZE * ZOOM_Y))
        
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
            wasChopped = closestTree.chop(self.particles, self.allSprites, self.player)
            if wasChopped and closestTree.isChopped:
                self.trees.remove(closestTree)
            return True
        return False
    
    def isPlantable(self, tilePos):
        for crop in self.crops:
            if (crop.rect.x // TILE_SIZE, crop.rect.y // TILE_SIZE) == tilePos:
                return False
        return True

    def plantCrop(self, cropName, player):
        tileX, tileY = self.getTileInFront(player)
        for tile in self.soilTiles:
            if (tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE) == (tileX, tileY):
                if tile.tilled and self.isPlantable((tileX, tileY)):
                    cropPos = (tileX * TILE_SIZE * ZOOM_X, tileY * TILE_SIZE * ZOOM_Y)
                    Crop(cropPos, cropName, [self.allSprites, self.crops])
                return

    def setup(self):
        mapWidth = self.tmxData.width * self.tmxData.tilewidth
        mapHeight = self.tmxData.height * self.tmxData.tileheight
        groundSurf = pygame.image.load("graphics/world/myfarm.png").convert_alpha()
        groundSurf = pygame.transform.smoothscale(groundSurf, (int(mapWidth * ZOOM_X), int(mapHeight * ZOOM_Y)))
        Generic((0, 0), groundSurf, [self.allSprites], z=LAYERS['ground'])

        self.spawnObstacles()

        spawnPoint = None
        for obj in self.tmxData.objects:
            if getattr(obj, "objectType", None) == "playerSpawn":
                spawnPoint = (obj.x * ZOOM_X, obj.y * ZOOM_Y)
                break
        if not spawnPoint:
            spawnPoint = (400 * ZOOM_X, 300 * ZOOM_Y)

        from player import Player
        self.player = Player(spawnPoint, [self.allSprites], self.collisionSprites, self)
        self.player.setMapBounds(self.mapRect)
        self.overlay = Overlay(self.player)

    def spawnObstacles(self):
        for x, y, surf in self.tmxData.get_layer_by_name("fence").tiles():
            if surf:
                pos = (x * self.tmxData.tilewidth * ZOOM_X, y * self.tmxData.tileheight * ZOOM_Y)
                Generic(pos, surf, [self.allSprites, self.collisionSprites])
        
        # Get all tree objects
        treeObjects = []
        for obj in self.tmxData.get_layer_by_name("tree"):
            treeObjects.append(obj)
        
        # Automatic clustering - group pixels that are close together
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
                    
                    # Check if this object is close to ANY object in the current cluster
                    for clusterObj in currentCluster:
                        distance = ((clusterObj.x - otherObj.x) ** 2 + 
                                (clusterObj.y - otherObj.y) ** 2) ** 0.5
                        
                        if distance < 32:  # 32 pixel radius
                            currentCluster.append(otherObj)
                            usedObjects.add(j)
                            clusterChanged = True
                            break
            
            # Only create trees from clusters that look like actual trees (8-16 pixels)
            if 8 <= len(currentCluster) <= 16:
                treeGroups.append(currentCluster)
        
        # Create tree sprites for each valid cluster
        for cluster in treeGroups:
            self.createTreeFromGroup(cluster)
        
        for obj in self.tmxData.get_layer_by_name("rock"):
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), obj.image, [self.allSprites])
            rockHitbox = pygame.Surface((int(16 * ZOOM_X), int(16 * ZOOM_Y)), pygame.SRCALPHA)
            Generic((obj.x * ZOOM_X, obj.y * ZOOM_Y), rockHitbox, [self.collisionSprites])
                
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
        
        # Create the tree sprite at the calculated center
        tree = Tree(
            pos=(centerX * ZOOM_X - width * ZOOM_X / 2, centerY * ZOOM_Y - height * ZOOM_Y / 2),
            surf=treeSurface,
            groups=[self.allSprites, self.trees],
            name='tree',
            playerAdded=self.playerAdded
        )
        
        # Create ONE collision hitbox for the entire tree
        trunkWidth = int(tree.rect.width)  # Full tree width
        trunkHeight = int(tree.rect.height)  # Full tree height
        
        # Calculate hitbox position - centered on the tree
        hitboxX = tree.rect.centerx - trunkWidth // 2
        hitboxY = tree.rect.centery - trunkHeight // 2
        
        # Create ONE hitbox sprite (invisible collision only)
        hitboxSurf = pygame.Surface((trunkWidth, trunkHeight))
        hitboxSurf.fill((0, 0, 0))
        hitboxSurf.set_alpha(0)  # Completely invisible
        
        hitboxSprite = Generic(
            (hitboxX, hitboxY),
            hitboxSurf,
            [self.collisionSprites],  # Only collision group, not visible
            z=LAYERS['main']
        )
        tree.hitboxSprite = hitboxSprite

    def run(self, deltaTime):
        self.allSprites.update(deltaTime)
        self.crops.update(deltaTime)
        self.particles.update(deltaTime)
        self.trees.update(deltaTime)
        self.itemsGroup.update(deltaTime)

        keys = pygame.key.get_pressed()
        for sprite in [s for s in self.allSprites if getattr(s, 'pickup', False)]:
            if self.player.rect.colliderect(sprite.rect) and keys[pygame.K_f]:
                added = self.player.inventory.addItem(sprite.pickupKey, 1, getattr(sprite, 'icon', None))
                if added:
                    sprite.kill()

        self.allSprites.customisedDraw(self.player)
        self.overlay.display()
        self.player.inventory.draw(self.displaySurface)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, mapRect):
        super().__init__()
        self.mapRect = mapRect
        self.offset = pygame.math.Vector2(0, 0)
        self.displaySurface = pygame.display.get_surface()

    def customisedDraw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        self.offset.x = max(0, min(self.offset.x, self.mapRect.width - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.mapRect.height - SCREEN_HEIGHT))
        
        for sprite in sorted(self.sprites(), key=lambda spr: spr.z):
            offsetPos = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPos)