import pygame
from settings import *


class Menu:
    def __init__(self, simulation):
        self.simulation = simulation
        self.mid_w, self.mid_h = DISPLAY_W / 2, DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 100
        self.state = "Reactive"
        self.reactivex, self.reactivey = self.mid_w, self.mid_h + 30
        self.nocoopx, self.nocoopy = self.mid_w, self.mid_h + 50
        self.alloutx, self.allouty = self.mid_w, self.mid_h + 70
        self.cursor_rect.midtop = (self.reactivex + self.offset, self.reactivey)

    def draw_cursor(self):
        self.simulation.draw_text('*', 15, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.simulation.window.blit(self.simulation.display, (0, 0))
        pygame.display.update()
        self.simulation.reset_keys()

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.simulation.check_events()
            self.check_input()
            self.simulation.display.fill(BLACK)
            self.simulation.draw_text('Main Menu', 20, DISPLAY_W / 2, DISPLAY_H / 2 - 20)
            self.simulation.draw_text("Reactive", 20, self.reactivex, self.reactivey)
            self.simulation.draw_text("No coop", 20, self.nocoopx, self.nocoopy)
            self.simulation.draw_text("All out", 20, self.alloutx, self.allouty)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.simulation.DOWN_KEY:
            if self.state == 'Reactive':
                self.cursor_rect.midtop = (self.nocoopx + self.offset, self.nocoopy)
                self.state = 'No coop'
            elif self.state == 'No coop':
                self.cursor_rect.midtop = (self.alloutx + self.offset, self.allouty)
                self.state = 'All out'
            elif self.state == 'All out':
                self.cursor_rect.midtop = (self.reactivex + self.offset, self.reactivey)
                self.state = 'Reactive'
        elif self.simulation.UP_KEY:
            if self.state == 'Reactive':
                self.cursor_rect.midtop = (self.alloutx + self.offset, self.allouty)
                self.state = 'All out'
            elif self.state == 'No coop':
                self.cursor_rect.midtop = (self.reactivex + self.offset, self.reactivey)
                self.state = 'Reactive'
            elif self.state == 'All out':
                self.cursor_rect.midtop = (self.nocoopx + self.offset, self.nocoopy)
                self.state = 'No coop'

    def check_input(self):
        self.move_cursor()
        if self.simulation.START_KEY:
            if self.state == 'Reactive':
                self.simulation.playing = True
            elif self.state == 'No coop':
                pass
            elif self.state == 'All out':
                pass
            self.run_display = False











