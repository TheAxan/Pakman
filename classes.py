import pygame
import pathing
import copy
import itertools
import settings
import screen as s
from maps import default_map as map



class Entity:
    entities: set[object] =  set()  # to loop through routines
    
    direction_conversion = {
            (0, -1): 'up',
            (-1, 0): 'left',
            (0, 1): 'down',
            (1, 0): 'right',
    }

    def __init__(self, x: int, y: int, speed: int, direction: str, name: str) -> None:
        Entity.entities.add(self)
        self.name = name

        # self.x is the array index
        self.x: int = x
        self.y: int = y

        self.offset: list[float] = [x, y]

        self.surface = pygame.Surface((s.gu, s.gu))
        self.graphic_rect = self.surface.get_rect()
        self.graphic_update()

        self.speed_scalar: float = speed  # cells/frame
        self.direction_update(
            {
                'up': (0, -1),
                'left': (-1, 0),
                'down': (0, 1),
                'right': (1, 0),
            }[direction]
        )


    def routine(self):
        self.full_cell_check()
        self.move()
        self.update_position()
        self.graphic_update()
    
    def graphic_update(self):
        self.graphic_rect.center = (self.offset[0] * s.cu + s.cu/2, self.offset[1] * s.cu + s.cu/2)
        s.screen.blit(self.surface, self.graphic_rect)
    
    def full_cell_check(self):
        if self.x == round(self.offset[0], 3) and self.y == round(self.offset[1], 3):
            self.full_cell_routine()
    
    def full_cell_routine(self):
        raise NotImplementedError

    def tunnel_warp(self):
        if self.y == 14:
            if self.x == -1:
                self.offset[0] = 28
            elif self.x == 28:
                self.offset[0] = -1
    
    def wall_ahead(self) -> bool:
        return (map.walls[self.y + self.direction_vector[1]]
                        [self.x + self.direction_vector[0]] == 1)

    def move(self):
        self.offset[0] += self.speed_vector[0]
        self.offset[1] += self.speed_vector[1]

    def update_position(self):
        self.x = round(self.offset[0])
        self.y = round(self.offset[1])

    def direction_update(self, new_direction):
        self.direction_vector: tuple[int] = new_direction
        self.direction: str = Entity.direction_conversion[self.direction_vector]
        self.speed_vector: tuple[float] = tuple(self.speed_scalar * i for i in self.direction_vector)
        self.sprite_update()

    def sprite_update(self):
        self.sprites = itertools.cycle(self.sprite_cycle())
        self.sprite_next()

    def sprite_cycle(self):
        raise NotImplementedError

    def sprite_next(self):
        if any(self.speed_vector):
            self.surface = next(self.sprites)

class Player(Entity):
    def __init__(self, x: int, y: int, speed: int, direction: str, name: str) -> None:
        super().__init__(x, y, speed, direction, name)
        self.input: tuple[int | float] | None = None
    
    def full_cell_routine(self):
        self.input_handling()
        self.tunnel_warp()
        self.wall_handling()
        self.ghost_collision()
        self.pellet_handling()
    

    def input_assignement(self, input):
        self.input = {
            pygame.K_UP: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_DOWN: (0, 1),
            pygame.K_RIGHT: (1, 0),
        }[input]
    
    def input_is_real(self):
        return self.input is not None and self.direction_vector != self.input
    
    def input_is_accessible(self): # cell to turn to isn't a wall
        return map.walls[self.y + self.input[1]][self.x + self.input[0]] != 1
        
    def input_is_valid(self) -> bool:
        return (self.input_is_real() and 
                self.input_is_accessible() and 
                self.x in range(0, 27))

    def input_handling(self):
        if self.input_is_valid():
            self.direction_update(self.input)
            self.input = None
    

    def wall_handling(self):
        if self.wall_ahead():
            self.speed_vector = (0, 0)
    
    def ghost_collision(self):
        for entity in Ennemy.ennemies:
            entity.player_collision()
    
    def sprite_cycle(self):
        return (
            pygame.image.load(f'image_files\{self.name}_{self.direction}_{sprite_number}.png')
            for sprite_number in (0, 1, 2, 1)
        )
    
    def pellet(self):
        return map.points[self.y][self.x]
            
    def pellet_handling(self):
        if self.pellet():
            if self.pellet == 2:
                self.power_pellet_handling()
            map.remove_point(self.x, self.y)
    
    def power_pellet_handling(self):
        raise NotImplementedError

        

class Ennemy(Entity):

    chase_mode: bool = False
    ennemies: set[object] = set()
    game_over: bool = False
    
    def __init__(self, x: int, y: int, speed: int, direction: str, 
                 name: str, color: tuple[int], scatter_target, chase_target) -> None:
        
        self.color = color
        super().__init__(x, y, speed, direction, name)

        self.scatter_target = {
            'up-left': (0, 0),
            'up-right': (len(map.walls[0]) - 1, 0),
            'down-left': (0, len(map.walls) -1 ),
            'down-right': (len(map.walls[0]) -1, len(map.walls) -1),
        }.get(scatter_target, 'up-left')
        
        self.chase_target = {
            'blinky_target': self.blinky_target,
            'pinky_target': self.pinky_target,
            'inky_target': self.inky_target,
            'clyde_target': self.clyde_target,
        }.get(chase_target, 'blinky_targe')

        Ennemy.ennemies.add(self)


    def full_cell_routine(self):
        self.player_collision()
        self.intersection_check()
        self.tunnel_warp()

    def player_collision(self):
        if self.x == pak.x and self.y == pak.y:
            print(f'Game over, {self.name.capitalize()} got you')  # maybe TODO game over screen
            Ennemy.game_over = True
    
    def intersection_check(self):
        if map.walls[self.y][self.x] == 2:
            self.next_move_triangulation()
        else:
            self.wall_handling()
    

    def next_move_A_star(self):  # maybe TODO A* tunnel consideration
        x, y = pathing.A_star((self.x, self.y), self.target_selection(), self.no_backtrack(map.walls), (1, 3))[1]
        self.direction_update((x - self.x, y - self.y))

    def next_move_triangulation(self):
        x, y = pathing.triangulation((self.x, self.y), self.target_selection(), self.no_backtrack(map.walls), (1, 3))
        self.direction_update((x - self.x, y - self.y))

    def target_selection(self):
        if Ennemy.chase_mode:
            return self.chase_target()
        else:
            return self.scatter_target

    def blinky_target(self):
        return (pak.x, pak.y)

    def pinky_target(self):
        return (pak.x + 4 * pak.direction_vector[0], pak.y + 4 * pak.direction_vector[1])

    def inky_target(self):  # a blinky ennemy is required
        return (
            (pak.x + 2 * pak.direction_vector[0] - blinky.x) * 2 + blinky.x, 
            (pak.y + 2 * pak.direction_vector[1] - blinky.y) * 2 + blinky.y
        )
    
    def clyde_target(self):
        if ((pak.x - self.x) ** 2 + (pak.y - self.y) ** 2) ** 0.5 <= 8:
            return self.scatter_target
        else:
            return self.blinky_target()
    
    def target_display(self):
        circle_surface = pygame.Surface((s.cu, s.cu))
        circle_surface.set_colorkey(settings.black)
        pygame.draw.circle(circle_surface, self.surface.get_at(self.surface.get_rect().center), 
                           (s.cu/2, s.cu/2), s.cu/3)
        if self.chase_target == inky.inky_target:
            s.screen.blit(circle_surface,
                          tuple(i * s.cu for i in (pak.x + 2 * pak.direction_vector[0], 
                                                   pak.y + 2 * pak.direction_vector[1])))
        s.screen.blit(circle_surface, tuple(i * s.cu for i in self.target_selection()))


    def no_backtrack(self, array: list[list[int]]):
        temp_array = copy.deepcopy(array)
        temp_array[self.y - self.direction_vector[1]][self.x - self.direction_vector[0]] = 1
        return temp_array
        
    def wall_handling(self):
        if self.wall_ahead():
            if self.direction_vector[0] == 0:
                if map.walls[self.y][self.x + 1] == 1:
                    self.direction_update((-1, 0))
                else:
                    self.direction_update((1, 0))
            elif self.direction_vector[1] == 0:
                if map.walls[self.y + 1][self.x] == 1:
                    self.direction_update((0, -1))
                else:
                    self.direction_update((0, 1))

    def turn_around(self):
        self.direction_update(tuple(-x for x in self.direction_vector))
    
    
    def sprite_cycle(self):
        return (
            self.sprite_assembly(sprite_number)
            for sprite_number in (0, 1)
        )
    
    def sprite_assembly(self, sprite_number):
        sprite = pygame.image.load(f'image_files\ghost_body_{sprite_number}.png')
        sprite.fill(self.color, special_flags=pygame.BLEND_MULT)
        sprite.blit(
            pygame.image.load(f'image_files\ghost_eyes_{self.direction}.png'),
            (0, 0)
        )
        return sprite
            

pak = Player(14, 17, 1/6, 'left', 'pac')

blinky = Ennemy(17, 23, 1/8, 'left', 'blinky', settings.red, 'up-right', 'blinky_target')
inky = Ennemy(22, 14, 1/8, 'right', 'inky', settings.cyan, 'down-right', 'inky_target')
pinky = Ennemy(16, 29, 1/8, 'right', 'pinky', settings.pink, 'up-left', 'pinky_target')
clyde = Ennemy(21, 13, 1/8, 'up', 'clyde', settings.orange, 'down-left', 'clyde_target')
