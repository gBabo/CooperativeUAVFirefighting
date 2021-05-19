from drone import *
from map2 import *
from hybrid import DroneHybrid
from weather import *
from sector import *
from button import *
from util import print_path_point
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
        # none actualized tile map for hybrid drone
        self.hybrid_drone_map = {}
        # to put created tiles dont know/can do the same with the Group above
        self.drone_list = []
        self.wind = Wind(
            random.choice([Direction.North, Direction.South, Direction.East, Direction.West]),
            random.randint(1, 10))  # Static for testing
        self.wind_display = Button(WHITE, 40, 120, 180, 30, "Wind direction: " + str(self.wind.direction))
        self.wildfire_list: List[Wildfire] = []

        self.sector_list: List[Sector] = []
        self.population_list: List[Tile] = []

        self.hybrid_drone_sectors_on_fire: List[Sector] = []
        self.hybrid_drone_points_on_fire: List[Point] = []

        self.fire_image = pygame.Surface((TILESIZE/2, TILESIZE/2))

        # button and variable that indicates if sim is in step or continuous mode
        self.step_button = None
        self.step = False

        # button, step counter and variable that make sim do one step in step mode
        self.step_next_button = None
        self.step_counter = 0
        self.step_pause = False

        # button and var that says to create reactive drones
        self.reactive_drone_button = None
        self.create_reactive_drone = False

        # button and var that indicates to create hybrid drones
        self.hybrid_drone_button = None
        self.create_hybrid_drone = False

        # button and var that indicates to create hybrid coop drones
        self.naive_drone_button = None
        self.create_naive_drone = False

        # button for debug mode
        self.debug_button = None
        self.debug_mode = False

        self.drone_not_chosen = True

    def simulation_loop(self):
        self.initial_draw()
        while self.drone_not_chosen and self.playing and self.running:
            self.check_events()
        self.init_and_draw_drones()
        time.sleep(1)
        while self.playing:
            self.step_counter += 1
            while self.step and self.step_pause and self.playing and self.running:
                self.check_events()
            self.step_pause = True
            if self.check_end_conditions():
                print("------------Simulation END------------")
                self.calculate_metrics()

                while self.playing and self.running:
                    self.check_events()
                break
            self.check_events()
            for agent in self.drone_list:
                agent.agent_decision()
            for wild in self.wildfire_list:
                update_wildfire(wild)
                expand_wildfire(wild, self.tile_dict, self.wind)
                if not wild.stop_time and not len(wild.tiles):
                    wild.stop_time = self.step_counter

            for sector in self.sector_list:
                if sector.calculate_fire_alert(self.wildfire_list):
                    print("FIRE! in sector " + str(sector.sectorID))
                    self.hybrid_drone_sectors_on_fire.append(sector)

            self.update()
            self.draw()
            self.reset_keys()
            time.sleep(1)

    def check_events(self):
        for event in pygame.event.get():
            mouse_position = pygame.mouse.get_pos()
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.naive_drone_button.is_over(mouse_position):
                    self.create_naive_drone = True
                    self.create_reactive_drone = False
                    self.create_hybrid_drone = False
                    self.drone_not_chosen = False
                    if not self.wildfire_list:
                        self.create_wildfires()
                if self.reactive_drone_button.is_over(mouse_position):
                    self.create_reactive_drone = True
                    self.create_hybrid_drone = False
                    self.create_naive_drone = False
                    self.drone_not_chosen = False
                    if not self.wildfire_list:
                        self.create_wildfires()
                if self.hybrid_drone_button.is_over(mouse_position):
                    self.create_hybrid_drone = True
                    self.create_reactive_drone = False
                    self.create_naive_drone = False
                    self.drone_not_chosen = False
                    if not self.wildfire_list:
                        self.create_wildfires()
                if self.step_button.is_over(mouse_position):
                    self.step = not self.step
                    self.step_pause = not self.step_pause
                    self.step_button.text = 'step:' + str(self.step)
                    self.step_button.draw(self.screen)
                    pygame.display.flip()
                if self.step_next_button.is_over(mouse_position):
                    self.step_pause = False
                if self.debug_button.is_over(mouse_position):
                    self.debug_mode = not self.debug_mode
                    print(self.debug_button.text + f": {self.debug_mode}")

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    # Create things

    def create_tiles(self):
        for y in range(0, 32, 1):
            for x in range(0, 32, 1):
                if sim_map2[y][x][0] == "population":
                    tile = Population(self, x, y)
                    self.population_list.append(tile)
                elif sim_map2[y][x][0] == "road":
                    tile = Road(self, x, y)
                elif sim_map2[y][x][0] == "forest":
                    tile = Forest(self, x, y)
                else:  # Water
                    tile = Water(self, x, y)
                self.tile_group.add(tile)
                self.tile_dict[tile.point] = tile
                self.hybrid_drone_map[tile.point] = tile

    def create_naive_drones(self):
        drone = DroneNaive(self, 16, 16)
        self.drone_group.add(drone)
        self.drone_list.append(drone)
        if not self.debug_mode:
            drone = DroneNaive(self, 17, 16)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneNaive(self, 18, 16)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneNaive(self, 16, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneNaive(self, 17, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneNaive(self, 18, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)

    def create_reactive_drones(self):
        drone = DroneReactive(self, 16, 16)
        self.drone_group.add(drone)
        self.drone_list.append(drone)
        if not self.debug_mode:
            drone = DroneReactive(self, 15, 16)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 17, 16)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 15, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 16, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 17, 17)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 15, 18)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneReactive(self, 16, 18)
            self.drone_group.add(drone)
            self.drone_list.append(drone)

    def create_hybrid_drones(self):
        drone = DroneHybrid(self, 16, 16, self.hybrid_drone_map)
        self.drone_group.add(drone)
        self.drone_list.append(drone)
        if not self.debug_mode:
            """drone = DroneHybrid(self, 15, 16, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneHybrid(self, 17, 16, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneHybrid(self, 15, 17, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            drone = DroneHybrid(self, 16, 17, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)"""
            drone = DroneHybrid(self, 17, 17, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)
            """drone = DroneHybrid(self, 15, 18, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)"""
            drone = DroneHybrid(self, 16, 18, self.hybrid_drone_map)
            self.drone_group.add(drone)
            self.drone_list.append(drone)

    def create_sectors(self):
        sector_id = 1
        sector_size = 8
        for y in range(0, 32 // sector_size, 1):
            for x in range(0, 32 // sector_size, 1):
                # id, probability per fire, size
                sector = Sector(sector_id, 16 / 64, sector_size)
                sector_id = sector_id + 1
                sector.create_sector(x * sector_size, y * sector_size)
                self.sector_list.append(sector)

    def create_wildfires(self):
        if self.debug_mode:
            point = Point(23, 18)
            fire = self.tile_dict[point]
            fire.fire_intensity = 10
            wild = Wildfire(1, point, 1)
            fire.on_fire = True
            wild.add_fire(fire)
            self.wildfire_list.append(wild)
        else:
            rng = random.randint(1, 3)
            print(f"Wildfire count: {rng}")
            for i in range(1, rng + 1):
                lst = [x for x in self.tile_dict.values() if x.__class__ == Forest and x.fire_intensity == 0]
                point = random.choice(lst).point
                fire = self.tile_dict[point]
                fire.fire_intensity = 1
                wild = Wildfire(i, point, 1)
                fire.on_fire = True
                wild.add_fire(fire)
                self.wildfire_list.append(wild)

    def create_buttons(self):
        self.step_button = Button(WHITE, 40, 40, 180, 30, 'step:' + str(self.step))
        self.step_next_button = Button(WHITE, 40, 80, 180, 30, 'next step')
        self.debug_button = Button(WHITE, 40, 160, 180, 30, 'Debug Mode')

        self.naive_drone_button = Button(WHITE, 250, 40, 160, 30, 'Start with naive drones')
        self.reactive_drone_button = Button(WHITE, 425, 40, 160, 30, 'Start with reactive drones')
        self.hybrid_drone_button = Button(WHITE, 600, 40, 160, 30, 'Start with hybrid drones')

    # draw things

    def draw(self):
        self.update_tiles()
        self.draw_tiles()
        self.draw_grid()
        self.draw_drones()
        self.draw_buttons()
        pygame.display.flip()

    def initial_draw(self):
        self.update_tiles()
        self.draw_tiles()
        self.draw_grid()
        self.draw_buttons()
        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, GRID_W + 1, TILESIZE):
            if x % 128 == 0:
                pygame.draw.line(self.screen, PURPLE, (x + GRID_MARGIN_X, GRID_MARGIN_Y),
                                 (x + GRID_MARGIN_X, GRID_H + GRID_MARGIN_Y))
            else:
                pygame.draw.line(self.screen, WHITE, (x + GRID_MARGIN_X, GRID_MARGIN_Y),
                                 (x + GRID_MARGIN_X, GRID_H + GRID_MARGIN_Y))
        for y in range(0, GRID_H + 1, TILESIZE):
            if y % 128 == 0:
                pygame.draw.line(self.screen, PURPLE, (GRID_MARGIN_X, y + GRID_MARGIN_Y),
                                 (GRID_W + GRID_MARGIN_X, y + GRID_MARGIN_Y))
            else:
                pygame.draw.line(self.screen, WHITE, (GRID_MARGIN_X, y + GRID_MARGIN_Y),
                                 (GRID_W + GRID_MARGIN_X, y + GRID_MARGIN_Y))

    def draw_tiles(self):
        self.tile_group.draw(self.screen)

    def draw_drones(self):
        self.drone_group.draw(self.screen)

    def draw_buttons(self):
        self.step_button.draw(self.screen)
        self.step_next_button.draw(self.screen)
        self.debug_button.draw(self.screen)
        self.reactive_drone_button.draw(self.screen)
        self.hybrid_drone_button.draw(self.screen)
        self.naive_drone_button.draw(self.screen)
        self.wind_display.draw(self.screen)

    # update things

    def update(self):
        self.tile_group.update()
        self.drone_group.update()

    def update_tiles(self):
        for tile in self.tile_dict.values():
            if tile.__class__ == Population:
                color = RED
            elif tile.__class__ == Forest:
                color = GREEN
            elif tile.__class__ == Road:
                color = LIGHTGREY
            else:
                color = BLUE
            tile.image.fill(color)

            if tile.on_fire or tile.integrity == 0:
                color = (ORANGE, BLACK)[tile.integrity == 0]
                self.fire_image.fill(color)
                tile.image.blit(self.fire_image, [TILESIZE/4, TILESIZE/4])

    def expand_priority(self):
        q = []

        for tile in self.tile_dict.values():
            if tile.priority == 10:
                q.append(tile)

        while len(q) != 0:
            tile = q.pop()
            priority = tile.priority - 1
            for n in get_neighbours(tile, self.tile_dict):
                if n.priority >= priority or n in q:
                    continue
                n.priority = priority
                q.append(n)

        """for tile in self.tile_dict.values():
            print(tile)"""

    # initiate and create things

    def initiate(self):
        self.create_buttons()
        self.create_tiles()
        self.expand_priority()
        self.create_sectors()

    def init_and_draw_drones(self):
        if self.create_reactive_drone:
            self.create_reactive_drones()

        if self.create_hybrid_drone:
            self.create_hybrid_drones()

        if self.create_naive_drone:
            self.create_naive_drones()

        self.draw_drones()
        pygame.display.flip()

    # End things

    def check_end_conditions(self):
        # All Drones Dead
        if len(self.drone_list) == 0:
            print("All Drones Died")
            return True

        # All Fires Dead and Calculate Total Priority Burned
        priority_value_burned = 0
        end = True
        for wildfire in self.wildfire_list:
            priority_value_burned += wildfire.tile_on_fire_priority()
            priority_value_burned += wildfire.tile_burned_priority()
            if len(wildfire.tiles) != 0:
                end = False

        if end:
            print("All Fires Out")
            return True

        # All Population tiles dead
        end = True
        for population_tile in self.population_list:
            if population_tile.integrity != 0:
                end = False

        if end:
            print("All Population Dead")
            return True

        # Too Much Priority Burned
        if priority_value_burned > MAX_PRIORITY_BURNED:
            print("Too Much Priority Dead")
            end = True
        else:
            end = False

        return end

    def calculate_metrics(self):
        print("Total Steps:", self.step_counter)
        print("Number of Fires:", len(self.wildfire_list))
        total_distance = total_priority_burned = n_tiles = 0
        for wildfire in self.wildfire_list:
            print("-----------------------", wildfire)
            # priority
            priority_burned = wildfire.tile_on_fire_priority() + wildfire.tile_burned_priority()
            total_priority_burned += priority_burned
            print("Priority On Fire and Burned:", priority_burned)
            # spread
            distance = wildfire.max_fire_spread_distance()
            total_distance += distance
            n_tiles += len(wildfire.points)
            print("Max Fire Spread Distance:", distance)
            # fire time to extinguish
            if wildfire.stop_time:
                print("Time to extinguish:", wildfire.stop_time - wildfire.start_time)
            else:
                print("Time to extinguish: Was not extinguished.")

        print("--------------------------------------\nTotal Priority On Fire and Burned:", total_priority_burned)
        print("Average Tile Priority On Fire and Burned:", total_priority_burned / n_tiles)
        print("Average Max Fire Spread Distance:", total_distance / len(self.wildfire_list))