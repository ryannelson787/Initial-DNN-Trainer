from level_generator import Level, Segment
from NeuralNetwork.neural_net import NeuralNet
from car import Car
import pygame, random

def turn_order(e):
    return -e.total_dis

random.seed(82)

new_level = Level(100, 20000, 200, 210)

generation = 1
gens = list()
cars = list()
for i in range(50):
    car = Car(0, 0, new_level)
    car.setup_nn(5, 3, 6, 10)

    cars.append(car)

gens.append(cars)

max_cycle_time = 100 * 60
cycle_time = 0

cx = 0
cy = 0
zoom = 0.5
res = [1200, 700]

"""
Pygame Initialization
"""

pygame.init()

pygame.key.set_repeat(1)

clock = pygame.time.Clock()

game_display = pygame.display.set_mode(res)
draw_surface = pygame.Surface(res)

running = True
while running:

    cycle_time += 1
    if cycle_time >= max_cycle_time:
        generation += 1

        gens[-1].sort(key=turn_order)

        percent_taken = 0.5

        print("NEWGEN: " + str(generation))
        print(gens[-1][0].total_dis)

        if generation % 100 == 0:
            new_level = Level(100, 20000, 200, 300)

        new_cars = list()
        cars = gens[-1]
        for i in range(0, len(cars)):
            new_car = Car(0, 0, new_level)

            if i < len(cars) * percent_taken:
                new_car.take_nn(cars[i].nn.create_copy())
                new_car.color = cars[i].color
                
            else:
                take_index = i % int(len(cars) * percent_taken)
                new_car.take_nn(cars[take_index].nn.create_mutation(take_index))
                new_car.color = cars[take_index % int(percent_taken * len(cars))].color
                co0 = min(max(100, new_car.color[0] + random.randint(-20, 20)), 255)
                co1 = min(max(100, new_car.color[1] + random.randint(-20, 20)), 255)
                co2 = min(max(100, new_car.color[2] + random.randint(-20, 20)), 255)
                new_car.color = (co0, co1, co2)
            new_cars.append(new_car)

        gens.append(new_cars)

        cycle_time = 0

    input_left = 0
    input_right = 0
    input_up = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        input_up = 1
    if keys[pygame.K_LEFT]:
        input_left = 1
    if keys[pygame.K_RIGHT]:
        input_right = 1

    best_car = None
    is_live_car = False
    for car in gens[-1]:
        live_car = car.calculate_nn_decisions()
        car.update()

        if not is_live_car and live_car:
            is_live_car = True

        if not live_car:
            continue
        
        if best_car == None:
            best_car = car
        else:
            stats_best = turn_order(best_car)
            stats_car = turn_order(car)

            if stats_car < stats_best:
                best_car = car

    if not is_live_car:
        cycle_time = max_cycle_time - 1

    best_car = gens[-1][0]
    cx = best_car.x
    cy = best_car.y

    """
    UPDATE ABOVE
    RENDER BELOW
    """

    draw_surface.fill((50, 50, 50))

    for seg in new_level.path:
        seg.draw_seg(draw_surface, cx, cy, zoom, res)

    for car in gens[-1]:
        car.draw_car(draw_surface, cx, cy, zoom, res)

    game_display.blit(draw_surface, (0, 0))

    pygame.display.update()

    clock.tick(144)

pygame.quit()