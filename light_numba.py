import pygame
import numpy as np
import time
import math
from numba import jit, njit, prange


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

ROWS = 250
COLS = 250

BLOCK_SIDE = min(SCREEN_WIDTH // COLS, SCREEN_HEIGHT // ROWS)

SCREEN_WIDTH = COLS * BLOCK_SIDE
SCREEN_HEIGHT = ROWS * BLOCK_SIDE

RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
WHITE = 255, 255, 255
BLACK = 0, 0, 0
DARK_GREY = 128, 128, 128


def color(height, weight):
    val = min(255, max(0, height))
    if weight == 10:
        val = 200
    elif weight > 1000:
        val = 169
     
    return val, val, val

@jit
def gpu_update(heights, prev_heights, vels, weights):
    for row in range(ROWS):
        for col in range(COLS):
            neighbors_heights = []
            if row != 0:   # UP
                neighbors_heights.append(prev_heights[row-1][col])
            if col != 0:   # LEFT
                neighbors_heights.append(prev_heights[row][col-1])
            if row != ROWS-1:   # DOWN
                neighbors_heights.append(prev_heights[row+1][col])
            if col != COLS-1:   # RIGHT
                neighbors_heights.append(prev_heights[row][col+1])
            
            vels[row][col] += (np.average(neighbors_heights) - heights[row][col]) / weights[row][col]
            heights[row][col] += vels[row][col]
    
    for row in range(ROWS):
        for col in range(COLS):
            prev_heights[row][col] = heights[row][col]


class Grid:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols

        self.width = width
        self.height = height
        
        self.xs = np.array([col * BLOCK_SIDE for col in range(COLS)])
        self.ys = np.array([row * BLOCK_SIDE for row in range(ROWS)])

        self.heights = np.array([[0.0 for col in range(COLS)] for row in range(ROWS)])
        self.prev_heights = np.array([[0.0 for col in range(COLS)] for row in range(ROWS)])
        self.vels = np.array([[0.0 for col in range(COLS)] for row in range(ROWS)])
        self.weights = np.array([[1.0 for col in range(COLS)] for row in range(ROWS)])

    def renovate(self):
        self.heights = np.array([[0.0 for _ in range(COLS)] for _ in range(ROWS)])
        self.prev_heights = np.array([[0.0 for _ in range(COLS)] for _ in range(ROWS)])
        self.vels = np.array([[0.0 for _ in range(COLS)] for _ in range(ROWS)])
        self.weights = np.array([[1.0 for col in range(COLS)] for _ in range(ROWS)])

        for row in range(ROWS):
            self.weights[row][150] = float('inf')
    
    def get_vals(self):
        return self.heights, self.prev_heights, self.vels, self.weights

    def render(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                pygame.draw.rect(screen, color(self.heights[row][col], self.weights[row][col]), (self.xs[col], self.ys[row], BLOCK_SIDE, BLOCK_SIDE))
    
    def __getitem__(self, key):
        return self.grid[key]

    def __contains__(self, val):
        return val in self.grid


class Visualizer:
    def __init__(self, width, height, rows, cols):
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.grid = Grid(rows, cols, width, height)

        self.started = True
        self.runner = True
    
    def get_clicked_pos(self, mouse_x, mouse_y):
        return mouse_y // BLOCK_SIDE, mouse_x // BLOCK_SIDE

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runner = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.started = not self.started
                
                elif event.key == pygame.K_c:
                    self.update()
                
                elif event.key == pygame.K_r:
                    self.grid.renovate()

        mouse_pos = pygame.mouse.get_pos()        
        row, col = self.get_clicked_pos(*mouse_pos)
        
        if pygame.mouse.get_pressed()[0]:
            self.grid.heights[row][col] = 10000
            self.grid.weights[row][col] = 10
        
        elif pygame.mouse.get_pressed()[2]:
            # if self.grid.weights[row][col] == 1:
                # self.grid.weights[row][col] = 10
            if self.grid.weights[row][col] > 100:
                self.grid.weights[row][col] = 1

    def update(self):
        gpu_update(*self.grid.get_vals())

    def render(self):
        self.grid.render(self.screen)
        pygame.display.flip()

        pygame.display.set_caption(f'FPS: {self.clock.get_fps()}')
    
    def run(self):
        while self.runner:
            self.clock.tick(25)
            
            self.process_input()
            if self.started:
                self.update()
            self.render()
        
        pygame.quit()


Visualizer(SCREEN_WIDTH, SCREEN_HEIGHT, ROWS, COLS).run()
