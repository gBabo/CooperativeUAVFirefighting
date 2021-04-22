from tile import Population, Forest, Road, Water
from drone import *
from map2 import *
from weather import *
from sector import *
import time


class Simulation:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, True
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
        # use to draw and do update to tiles
        self.tile_group = pygame.sprite.Group()
        # use to draw and do update to drones
        self.drone_group = pygame.sprite.Group()
        # to put created tiles dont know/can do the same with the Group above
        self.tile_dict = {}
        # to put created tiles dont know/can do the same with the Group above
        self.drone_list = []
        self.wind = Wind(
            random.choice([Direction.North, Direction.South, Direction.East, Direction.West]),
            random.randint(1, 10))  # Static for testing
        self.wildfire_list: List[Wildfire] = []

        self.sector_list: List[Sector] = []

    def simulation_loop(self):
        while self.playing:
            self.check_events()
            for agent in self.drone_list:
                agent.agent_decision()
            for wild in self.wildfire_list:
                update_wildfire(wild)
                expand_wildfire(wild, self.tile_dict, self.wind)

            for sector in self.sector_list:
                if sector.calculate_fire_alert(self.wildfire_list):
                    print("FIRE! in sector "+str(sector.sectorID))
            
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

# update things

    def update(self):
        self.tile_group.update()
        self.drone_group.update()

    def update_tiles(self):
        for wildfire in self.wildfire_list:
            for fire in wildfire.tiles:
                if self.tile_dict[fire.point].on_fire:
                    continue
                self.tile_dict[fire.point].image.fill(ORANGE)
                self.tile_dict[fire.point].on_fire = True

# draw things

    def draw(self):
        self.update_tiles()
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

# inicitate and create things

    def initiate(self):
        self.create_tiles()
        self.crete_drones()
        self.create_sectors()
        self.create_wildfires()

    def create_tiles(self):
        for y in range(0, 32, 1):
            for x in range(0, 32, 1):
                if sim_map2[y][x][0] == "population":
                    tile = Population(self, x, y)
                elif sim_map2[y][x][0] == "road":
                    tile = Road(self, x, y)
                elif sim_map2[y][x][0] == "forest":
                    tile = Forest(self, x, y)
                else:  # Water
                    tile = Water(self, x, y)
                self.tile_group.add(tile)
                self.tile_dict[tile.point] = tile

    def crete_drones(self):
        drone = DroneReactive(self, 16, 16)
        self.drone_group.add(drone)
        self.drone_list.append(drone)

    def create_sectors(self):
        sector_id = 1
        sector_size = 8
        for y in range(0, 32//sector_size, 1):
            for x in range(0, 32//sector_size, 1):
                #id, probability per fire, size
                sector = Sector(sector_id, 4/64, sector_size)
                sector_id = sector_id + 1
                sector.create_sector(x*sector_size, y*sector_size, self.tile_dict)
                self.sector_list.append(sector)

    def create_wildfires(self):
        point = Point(16, 16)
        fire = self.tile_dict[Point(16, 16)]
        fire.on_fire = True
        fire.image.fill(ORANGE)
        fire.fire_intensity = random.randint(1, 10)
        wild = Wildfire(1, point, 1)
        wild.add_fire(fire)
        self.wildfire_list.append(wild)
