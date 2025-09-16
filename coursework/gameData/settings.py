from pygame.math import Vector2

#screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32

#original game resolution
ORIGINAL_WIDTH = 800
ORIGINAL_HEIGHT = 600

#zoom in scale
ZOOM_X = SCREEN_WIDTH / ORIGINAL_WIDTH
ZOOM_Y = SCREEN_HEIGHT / ORIGINAL_HEIGHT

#player
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 128

#overlay positions
OVERLAY_POSITIONS = {
    'tool': (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 15),
    'seed': (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 5)}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-50, 40),
    'right': Vector2(50, 40),
    'up': Vector2(0, -10),
    'down': Vector2(0, 50)
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}

GROW_SPEED = {
	'artichoke': 8,
    'beans': 10,
    'beets': 6,
    'berries': 13,
    'corn': 14,
    'cranberries': 7,
    'hotPeppers': 5,
    'kale': 6,
    'melon': 12,
    'onion': 7,
    'parsnips': 4,
    'potatoes': 6,
    'pumpkin': 13,
	'tomato': 11
}

SALE_PRICES = {
	'artichoke': 160,
    'beans': 40,
    'beets': 100,
    'berries': 60,
    'corn': 50,
    'cranberries': 75,
    'hotPeppers': 40,
    'kale': 110,
    'melon': 250,
    'onion': 80,
    'parsnips': 35,
    'potatoes': 80,
    'pumpkin': 320,
	'tomato': 60
}

PURCHASE_PRICES = {
	'artichoke': 30,
    'beans': 60,
    'beets': 20,
    'berries': 80,
    'corn': 150,
    'cranberries': 240,
    'hotPeppers': 40,
    'kale': 70,
    'melon': 100,
    'onion': 50,
    'parsnips': 20,
    'potatoes': 50,
    'pumpkin': 100,
	'tomato': 60
}

