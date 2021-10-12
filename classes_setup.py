import pygame
import pathing
import sys
import copy
import screen_setup as s
import map_setup as m

class Entity:
    entities: list[object] = []  # to loop through routines
    
    def __init__(self, x: int, y: int, speed_divider: int, original_direction: str) -> None:
        Entity.entities.append(self)
        
        self.surface = pygame.Surface((s.u, s.u))
        self.surface.set_colorkey(s.black)

        # self.rect.x is the pixel x
        self.rect = self.surface.get_rect()
        self.rect.x = x * s.u
        self.rect.y = y * s.u

        # self.x is the array x
        self.x: int = x
        self.y: int = y
        
        self.speed: float = s.u / speed_divider
        self.movement: tuple[int | float] = {
            'left': (-self.speed, 0),
            'up': (0, -self.speed),
            'right': (self.speed, 0),
            'down': (0, self.speed),
        }[original_direction]

    def routine(self):
        self.full_cell_check()
        self.rect.move_ip(self.movement)
        self.update_position()
        s.screen.blit(self.surface, self.rect)
    
    def update_position(self):
        self.x = round(self.rect.x / s.u)
        self.y = round(self.rect.y / s.u)

    def tunnel_warp(self):
        if self.y == 14:
            if self.x == -1:
                self.rect.x = 28 * s.u
            elif self.x == 28:
                self.rect.x = -1 * s.u
    
    def wall_check(self):
        if (m.map_grid[self.y + int(self.movement[1] / self.speed)]  # cell ahead is a wall
                    [self.x + int(self.movement[0] / self.speed)]) == 1:
            self.wall_reaction()

    def wall_reaction():
        pass # defined in subclass

    def full_cell_check(self):
        if self.x == self.rect.x / s.u and self.y == self.rect.y / s.u:  # on a full cell
            self.full_cell_routine()

    def full_cell_routine(self):
        pass  # defined in subclass


class Player(Entity):
    def __init__(self, x: int, y: int, speed_divider: int, original_direction: str, color: tuple[int]) -> None:
        super().__init__(x, y, speed_divider, original_direction)
        
        self.input: tuple[int | float] | None = None
        pygame.draw.circle(self.surface, color, (s.u/2, s.u/2), s.u/2)
    
    def update_direction(self):
        if self.input is not None:
            if not (m.map_grid[self.y + int(self.input[1] / self.speed)]  # cell to turn to isn't a wall
                            [self.x + int(self.input[0] / self.speed)]) == 1:
                if self.x in range(0, 27):
                    self.movement = self.input
            self.input = None
    
    def wall_reaction(self):
        self.movement = (0, 0)
    
    def ghost_collision(self):
        for entity in Entity.entities[1:]:
            entity.player_collision()

    def full_cell_routine(self):
        self.update_direction()
        self.tunnel_warp()
        self.wall_check()
        self.ghost_collision()
    
    def input_handling(self, input):
        self.input = {
            pygame.K_LEFT: (-self.speed, 0),
            pygame.K_UP: (0, -self.speed),
            pygame.K_RIGHT: (self.speed, 0),
            pygame.K_DOWN: (0, self.speed),
        }[input]
    

class Ennemy(Entity):
    ghost_template = pygame.Surface((s.u, s.u))
    pygame.draw.circle(ghost_template, s.white, (s.u/2, s.u/2), s.u/2)
    pygame.draw.rect(ghost_template, s.black, (0, s.u/2, s.u, s.u/2))
    pygame.draw.polygon(ghost_template, s.white, (
        (0, s.u/2), (0, s.u), (s.u/4, s.u*3/4), (s.u/2, s.u), (s.u*3/4, s.u*3/4), (s.u, s.u), (s.u, s.u/2)))

    def __init__(self, x: int, y: int, speed_divider: int, original_direction: str, color: tuple[int], name: str) -> None:
        super().__init__(x, y, speed_divider, original_direction)
        
        self.surface.blit(Ennemy.ghost_template, (0, 0))
        self.surface.fill(color, special_flags=pygame.BLEND_MULT)
        self.name = name

    def full_cell_routine(self):
        self.player_collision()
        self.intersection_check()
        self.tunnel_warp()

    def intersection_check(self):
        if m.map_grid[self.y][self.x] == 2:
            self.next_move()
        else:
            self.wall_check()
    
    def wall_reaction(self):
        if self.movement[0] == 0:
            if m.map_grid[self.y][self.x + 1] == 1:
                self.movement = (-self.speed, 0)
            else:
                self.movement = (self.speed, 0)
        elif self.movement[1] == 0:
            if m.map_grid[self.y + 1][self.x] == 1:
                self.movement = (0, -self.speed)
            else:
                self.movement = (0, self.speed)
        
    def player_collision(self):
        if self.rect.colliderect(pak.rect):
            print(f'Game over, {self.name} got you')  # maybe TODO game over screen
            sys.exit()
            
    def no_backtrack(self, array: list[list[int]]):
        temp_array = copy.deepcopy(array)
        temp_array[self.y - int(self.movement[1] / self.speed)][self.x - int(self.movement[0] / self.speed)] = 1
        return temp_array
    
    def next_move(self):  # TODO A* pathing target parameters
        path = pathing.A_star((self.x, self.y), (pak.x, pak.y), self.no_backtrack(m.map_grid), (1, 3))
        self.movement = ((path[1][0] - path[0][0]) * self.speed, (path[1][1] - path[0][1]) * self.speed)


pak = Player(14, 23, 15, 'left', s.yellow)

blinky = Ennemy(17, 23, 18, 'left', s.red, 'Blinky')
inky = Ennemy(22, 14, 18, 'right', s.cyan, 'Inky')
pinky = Ennemy(16, 29, 18, 'right', s.pink, 'Pinky')
clyde = Ennemy(21, 13, 18, 'up', s.orange, 'Clyde')