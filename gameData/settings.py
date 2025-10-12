from pygame.math import Vector2

# SCREEN
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32

# RESOLUTION
BASE_WIDTH = 1280
BASE_HEIGHT = 720

# ZOOM SCALE
ZOOM_X = SCREEN_WIDTH / BASE_WIDTH  
ZOOM_Y = SCREEN_HEIGHT / BASE_HEIGHT 

# PLAYER
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 128

# OVERLAY POSITIONS
OVERLAY_POSITIONS = {
    'tool': (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 15),
    'seed': (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 5)
}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-50, 40),
    'right': Vector2(50, 40),
    'up': Vector2(0, -10),
    'down': Vector2(0, 50)
}

# LAYERS
LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'crops': 3,
    'main': 4,
    'abovePlayer': 5
}

#Time System
TIME_RATE = 60  # 1 real second equals 60 in-game seconds
DAY_LENGTH = 24 * TIME_RATE  # Total in-game seconds in a day

#DAY NIGHT COLOURS
NIGHT_COLOUR = (25, 25, 50, 180) # Dark blue with transparency
DAWN_COLOR = (255, 150, 50, 100)  # Orange with transparency
DUSK_COLOR = (150, 75, 100, 120)  # Purple with transparency

# ITEMS DICTIONARY
ITEMS = {
    # Crops / Seeds
    "artichoke": {
        "name": "Artichoke",
        "imagePath": "coursework/gameData/graphics/items/artichoke.png",
        "type": "seed"
    },
    "beans": {
        "name": "Beans",
        "imagePath": "coursework/gameData/graphics/items/beans.png",
        "type": "seed"
    },
    "beets": {
        "name": "Beets",
        "imagePath": "coursework/gameData/graphics/items/beets.png",
        "type": "seed"
    },
    "berries": {
        "name": "Berries",
        "imagePath": "coursework/gameData/graphics/items/berries.png",
        "type": "seed"
    },
    "corn": {
        "name": "Corn",
        "imagePath": "coursework/gameData/graphics/items/corn.png",
        "type": "seed"
    },
    "cranberries": {
        "name": "Cranberries",
        "imagePath": "coursework/gameData/graphics/items/cranberries.png",
        "type": "seed"
    },
    "hotpeppers": {
        "name": "Hot Peppers",
        "imagePath": "coursework/gameData/graphics/items/hotpeppers.png",
        "type": "seed"
    },
    "kale": {
        "name": "Kale",
        "imagePath": "coursework/gameData/graphics/items/kale.png",
        "type": "seed"
    },
    "melon": {
        "name": "Melon",
        "imagePath": "coursework/gameData/graphics/items/melon.png",
        "type": "seed"
    },
    "onion": {
        "name": "Onion",
        "imagePath": "coursework/gameData/graphics/items/onion.png",
        "type": "seed"
    },
    "parsnips": {
        "name": "Parsnips",
        "imagePath": "coursework/gameData/graphics/items/parsnips.png",
        "type": "seed"
    },
    "potatoes": {
        "name": "Potatoes",
        "imagePath": "coursework/gameData/graphics/items/potatoes.png",
        "type": "seed"
    },
    "pumpkin": {
        "name": "Pumpkin",
        "imagePath": "coursework/gameData/graphics/items/pumpkin.png",
        "type": "seed"
    },
    "tomato": {
        "name": "Tomato",
        "imagePath": "coursework/gameData/graphics/items/tomato.png",
        "type": "seed"
    },

    # Tools / Materials
    "wood": {
        "name": "Wood",
        "imagePath": "coursework/gameData/graphics/items/wood.png",
        "type": "material"
    },
    "stone": {
        "name": "Stone",
        "imagePath": "coursework/gameData/graphics/items/stone.png",
        "type": "material"
    },
    "wateringCan": {
        "name": "Watering Can",
        "imagePath": "coursework/gameData/graphics/items/wateringCan.png",
        "type": "tool"
    },
    "axe": {
        "name": "Axe",
        "imagePath": "coursework/gameData/graphics/items/axe.png",
        "type": "tool",
        "power": 5
    }
}

# GROW SPEEDS
GROW_SPEED = {
    'beans': 11 * DAY_LENGTH,      # 11 days
    'kale': 7 * DAY_LENGTH,        # 7 days
    'parsnips': 5 * DAY_LENGTH,    # 5 days
    'potatoes': 7 * DAY_LENGTH,    # 7 days
    'berries': 9 * DAY_LENGTH,     # 9 days
    'corn': 15 * DAY_LENGTH,       # 15 days
    'hotPeppers': 6 * DAY_LENGTH,  # 6 days
    'melon': 13 * DAY_LENGTH,      # 13 days
    'tomato': 12 * DAY_LENGTH,     # 12 days
    'artichoke': 9 * DAY_LENGTH,   # 9 days
    'beets': 7 * DAY_LENGTH,       # 7 days
    'cranberries': 8 * DAY_LENGTH, # 8 days
    'pumpkin': 14 * DAY_LENGTH,    # 14 days
    'onion': 7 * DAY_LENGTH,       # 7 days
}

# SALE PRICES
SALE_PRICES = {
    'artichoke': 160,
    'beans': 40,
    'beets': 100,
    'berries': 60,
    'corn': 50,
    'cranberries': 75,
    'hotpeppers': 40,
    'kale': 110,
    'melon': 250,
    'onion': 80,
    'parsnips': 35,
    'potatoes': 80,
    'pumpkin': 320,
    'tomato': 60
}

# PURCHASE PRICES
PURCHASE_PRICES = {
    'artichoke': 30,
    'beans': 60,
    'beets': 20,
    'berries': 80,
    'corn': 150,
    'cranberries': 240,
    'hotpeppers': 40,
    'kale': 70,
    'melon': 100,
    'onion': 50,
    'parsnips': 20,
    'potatoes': 50,
    'pumpkin': 100,
    'tomato': 60
}
