import pygame
# from menu import *
from settings import *
from tile import *


class Simulation:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, True
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
        self.font_name = pygame.font.get_default_font()
        # self.main_menu = Menu(self)
        self.tile_group = pygame.sprite.Group()
        self.tile_list = []

    def simulation_loop(self):
        while self.playing:
            self.check_events()
            self.update()
            self.draw()
            self.reset_keys()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                # self.main_menu.run_display = False
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

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def update(self):
        self.tile_group.update()

    def draw(self):
        self.draw_tiles()
        self.draw_grid()
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

    def initiate(self):
        self.create_tiles()

    """def create_tiles(self):
        for y in range(0, GRID_H + 1, TILESIZE):
            for x in range(0, GRID_W + 1, TILESIZE):
                self.tile_group.add(
                    Tile(self, "forest", x + TILE_MARGIN_X, y + TILE_MARGIN_Y, RED))"""

    def create_tiles(self):
        file = open("map.txt", "r")
        line = file.readline()
        while line:
            map_list = line.split(", ")
            print(map_list)
            if map_list[0] == "population":
                self.tile_group.add(
                    Tile(self, map_list[0], int(map_list[1]) + TILE_MARGIN_X, int(map_list[2]) + TILE_MARGIN_Y, RED))
                line = file.readline()
            if map_list[0] == "road":
                self.tile_group.add(
                    Tile(self, map_list[0], int(map_list[1]) + TILE_MARGIN_X, int(map_list[2]) + TILE_MARGIN_Y, BLACK))
                line = file.readline()
            if map_list[0] == "forest":
                self.tile_group.add(
                    Tile(self, map_list[0], int(map_list[1]) + TILE_MARGIN_X, int(map_list[2]) + TILE_MARGIN_Y, GREEN))
                line = file.readline()
            if map_list[0] == "body of water":
                self.tile_group.add(
                    Tile(self, map_list[0], int(map_list[1]) + TILE_MARGIN_X, int(map_list[2]) + TILE_MARGIN_Y, BLUE))
                line = file.readline()
        file.close()

