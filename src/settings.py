# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# dimensions of the window
DISPLAY_W = 1024
DISPLAY_H = 768

# dimensions of the grid
GRID_W = 512
GRID_H = 512
# dimenstion of the margins of the grid
GRID_MARGIN_X = 250
GRID_MARGIN_Y = 150

# dimension of the tile margin
TILE_MARGIN_X = 259
TILE_MARGIN_Y = 159

# dimension of the tile
TILESIZE = 16

# constants of the drone
DRONESIZE = 12
WATERCAPACITY = 100
BATTERY = 100
WATERRELEASED = 20
MOVEBATTERYCOST = 0

# limits
MIN_WIND = 1
MAX_WIND = 10
MIN_FIRE = 0
MAX_FIRE = 10
MIN_INTEGRITY = 0
DECAY = 1

# probability to tile type

# end conditions
#                     pop + extra
MAX_PRIORITY_BURNED = 36*10 + 10