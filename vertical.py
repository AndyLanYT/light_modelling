import pygame
import numpy as np
import time


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

BLOCK_COUNT = 275

BLOCK_SIDE = 4

RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
WHITE = 255, 255, 255
BLACK = 0, 0, 0


class Block:
    def __init__(self, idx, side=BLOCK_SIDE, weight=1):
        self.idx = idx

        self.side = side
        
        self.height = 0
        self.prev_height = 0

        self.weight = weight
        self.vel = 0

        self.neighbors = []

        self.active = True

    def set_neighbors(self, row):
        if self.idx == 0 or self.idx == BLOCK_COUNT - 1:
            self.weight = float('inf')
        # elif self.idx <= 2 * BLOCK_COUNT // 5:
            # self.weight = 10
        
        if self.idx != 0:   # LEFT
            self.neighbors.append(row[self.idx-1])
    
        if self.idx != BLOCK_COUNT-1:   # RIGHT
            self.neighbors.append(row[self.idx+1])
    
    @property
    def x(self):
        return 10 + self.idx * (self.side + 0)

    @property
    def y(self):
        return (SCREEN_HEIGHT - BLOCK_SIDE) // 2 - self.height
    
    @property
    def color(self):
        val = 170
        
        if self.weight == 10:
            val = 130
        elif self.weight > 10:
            val = 0
        
        return val, val, val
    
    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.side, self.side))

    def __repr__(self):
        return f'idx: {self.idx}, height: {self.height}, vel: {self.vel}'

class Row:
    def __init__(self, count):
        self.count = count

        self.row = []
        for idx in range(count):
            block = Block(idx)
            self.row.append(block)
        
        for block in self.row:
            block.set_neighbors(self.row)

    def renovate(self):
        self.row = []
        for idx in range(self.count):
            block = Block(idx)
            self.row.append(block)
        
        for block in self.row:
            block.set_neighbors(self.row)

    def update(self):
        for block in self.row:
            if block.active:
                heights = [neighbor.prev_height for neighbor in block.neighbors]
                block.vel += (np.average(heights) - block.height) / block.weight

                block.height += block.vel
        
        for block in self.row:
            block.prev_height = block.height

    def render(self, screen):
        for block in self.row:
            block.render(screen)
    
    def __getitem__(self, key):
        return self.row[key]

    def __contains__(self, val):
        return val in self.row


class Visualizer:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.row = Row(BLOCK_COUNT)

        self.started = True
        self.runner = True
        self.pressed_block = None
    
    def get_clicked_block(self, mouse_x, mouse_y):
        for block in self.row:
            if block.x <= mouse_x <= block.x + block.side and block.y <= mouse_y <= block.y + block.side:
                return block.idx
    
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runner = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.started = not self.started
                elif event.key == pygame.K_r:
                    self.row.renovate()

        mouse_x, mouse_y = pygame.mouse.get_pos()    

        if pygame.mouse.get_pressed()[0] and not self.pressed_block:
            idx = self.get_clicked_block(mouse_x, mouse_y)
            if idx is not None:
                self.pressed_block = self.row[idx]
                self.pressed_block.active = False
        elif pygame.mouse.get_pressed()[0]:
            self.pressed_block.height = SCREEN_HEIGHT // 2 - mouse_y
        elif self.pressed_block:
            self.pressed_block.active = True
            self.pressed_block = None
        elif pygame.mouse.get_pressed()[2]:
            idx = self.get_clicked_block(mouse_x, mouse_y)
            if idx is not None:
                self.pressed_block = self.row[idx]
                self.pressed_block.height += 100

    def update(self):
        self.row.update()

    def render(self):
        self.screen.fill(WHITE)
        self.row.render(self.screen)
        pygame.display.flip()
    
    def run(self):
        while self.runner:
            self.clock.tick(60)

            self.process_input()
            if self.started:
                self.update()
            self.render()
        
        pygame.quit()


Visualizer(SCREEN_WIDTH, SCREEN_HEIGHT).run()
