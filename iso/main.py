import record
import pygame
import pygame.gfxdraw
import time

class Color(record.Record):
    color: tuple

class State(record.Record):
    tile_colors: tuple
    background: Color
    tile_size: tuple

def pygame_init(screen_size):
    pygame.init()
    return pygame.display.set_mode(screen_size)

def state_init():
    red = Color((255, 0, 0))
    green = Color((0, 255, 0))
    blue = Color((0, 0, 255))
    grey = Color((100, 100, 100))
    return State((red, green, blue), grey, (100, 60))

def update_screen(state, screen):
    screen.fill(state.background)
    horizontal_center = screen.get_size()[0]//2
    tile_width, tile_height = state.tile_size
    colors = state.tile_colors
    for i in range(4):
        row_horizontal_shift = i*(tile_width//2)
        row_vertical_shift = i*(tile_height//2)
        i = -i
        for j in range(4):
            color = colors[int((1*i+j) % len(colors))]
            j /= 2
            i += 0.5
            tile_center = [i*(tile_width)+horizontal_center+row_horizontal_shift,
                           j*(tile_height)+row_vertical_shift]
            tile_points = [[tile_center[0], tile_center[1]+tile_height//2],
                           [tile_center[0]+tile_width//2, tile_center[1]],
                           [tile_center[0], tile_center[1]-tile_height//2],
                           [tile_center[0]-tile_width//2, tile_center[1]],]
            pygame.gfxdraw.filled_polygon(screen, tile_points, color)
    pygame.display.flip()

def main():
    screen = pygame_init((500, 500))
    state = state_init()
    while True:
        update_screen(state, screen)
        time.sleep(1)
    pygame.quit()

if __name__ == '__main__':
    main()