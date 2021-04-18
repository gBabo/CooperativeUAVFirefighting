from tile import *
from drone import *
from map2 import *
import time


class Simulation:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, True
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
        self.font_name = pygame.font.get_default_font()
        # use to draw and do update to tiles
        self.tile_group = pygame.sprite.Group()
        # use to draw and do update to drones
        self.drone_group = pygame.sprite.Group()
        # to put created tiles dont know/can do the same with the Group above
        self.tile_list = []
        # to put created tiles dont know/can do the same with the Group above
        self.drone_list = []

    def simulation_loop(self):
        while self.playing:
            self.check_events()
            for agent in self.drone_list:
                agent.agent_decision()
            self.update()
            self.draw()
            self.reset_keys()
            time.sleep(1)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def update(self):
        self.tile_group.update()
        self.drone_group.update()

    def draw(self):
        self.draw_tiles()
        self.draw_grid()
        self.draw_drones()
        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, GRID_W + 1, TILESIZE):
            pygame.draw.line(self.screen, WHITE, (x + GRID_MARGIN_X, GRID_MARGIN_Y),
                             (x + GRID_MARGIN_X, GRID_H + GRID_MARGIN_Y))
        for y in range(0, GRID_H + 1, TILESIZE):
            pygame.draw.line(self.screen, WHITE, (GRID_MARGIN_X, y + GRID_MARGIN_Y),
                             (GRID_W + GRID_MARGIN_X, y + GRID_MARGIN_Y))

    def draw_tiles(self):
        self.tile_group.draw(self.screen)

    def draw_drones(self):
        self.drone_group.draw(self.screen)

    def initiate(self):
        self.create_tiles()
        self.crete_drones()

    '''
    def create_tiles(self):
        for attr_list in sim_map:
            if attr_list[0] == "population":
                temp = Tile(self, attr_list[0], int(attr_list[1]) + TILE_MARGIN_X, int(attr_list[2]) + TILE_MARGIN_Y,
                            RED)
                self.tile_group.add(temp)
                self.tile_list.append(temp)
            if attr_list[0] == "road":
                temp = Tile(self, attr_list[0], int(attr_list[1]) + TILE_MARGIN_X, int(attr_list[2]) + TILE_MARGIN_Y,
                            BLACK)
                self.tile_group.add(temp)
                self.tile_list.append(temp)
            if attr_list[0] == "forest":
                temp = Tile(self, attr_list[0], int(attr_list[1]) + TILE_MARGIN_X, int(attr_list[2]) + TILE_MARGIN_Y,
                            GREEN)
                self.tile_group.add(temp)
                self.tile_list.append(temp)
            if attr_list[0] == "body of water":
                temp = Tile(self, attr_list[0], int(attr_list[1]) + TILE_MARGIN_X, int(attr_list[2]) + TILE_MARGIN_Y,
                            BLUE)
                self.tile_group.add(temp)
                self.tile_list.append(temp)'''

    def create_tiles(self):
        for y in range(0, 32, 1):
            for x in range(0, 32, 1):
                if sim_map2[y][x][0] == "population":
                    temp = Tile(self, sim_map2[x][y][0], x, y, RED)
                    self.tile_group.add(temp)
                    self.tile_list.append(temp)
                if sim_map2[y][x][0] == "road":
                    temp = Tile(self, sim_map2[x][y][0], x, y, BLACK)
                    self.tile_group.add(temp)
                    self.tile_list.append(temp)
                if sim_map2[y][x][0] == "forest":
                    temp = Tile(self, sim_map2[x][y][0], x, y, GREEN)
                    self.tile_group.add(temp)
                    self.tile_list.append(temp)
                if sim_map2[y][x][0] == "body of water":
                    temp = Tile(self, sim_map2[x][y][0],  x, y, BLUE)
                    self.tile_group.add(temp)
                    self.tile_list.append(temp)

    def crete_drones(self):
        drone = Drone(self, 16, 16)
        self.drone_group.add(drone)
        self.drone_list.append(drone)
