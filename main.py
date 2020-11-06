from random import randint, random
import numpy as np
import sys
import pygame
import math

sys.setrecursionlimit(100000)
pygame.init()

height = 750
width = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('FlappyAI')
back = pygame.image.load('background.png').convert_alpha()
back1 = pygame.image.load('back.jpg').convert()
clock = pygame.time.Clock()
gravity = 0
score = 0
num = 10
gen = 0
weights1 = []
weights2 = []
parents = []
parents1 = []
fitness = []


class Bird(pygame.sprite.Sprite):
    def __init__(self, bird_width, bird_height, y_change, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('bird.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (bird_width, bird_height))
        self.bird_width = bird_width
        self.bird_height = bird_height
        self.y_change = y_change
        self.x = x
        self.y = y
        self.term_velocity = 15
        self.rect1 = self.image.get_rect()
        self.center = self.rect1.center
        self.rot_sprite = None
        self.velocity = 1
        self.in1 = 0
        self.in3 = 0
        self.in4 = 0
        self.in6 = 0
        self.in7 = 0
        self.inputs = [[0, 0, 0, 0]]
        self.fitness_score = 0
        self.ang = 0
        self.weights1 = np.random.uniform(low=-1.0, high=1.0, size=(4, 6))
        self.weights2 = np.random.uniform(low=-1.0, high=1.0, size=(6, 1))
        self.dead = False

    def render(self):
        screen.blit(self.rot_sprite, (self.x, self.y))

    def check_collision(self, sprite):
        if self.rect1.colliderect(sprite) and not self.dead:
            self.dead = True

    def rect(self):
        self.rect1 = self.image.get_rect(x=self.x, y=self.y, width=self.bird_width, height=self.bird_height)

    def rot_center(self, angle):
        self.rot_sprite = pygame.transform.rotate(self.image, angle)
        self.rot_sprite.get_rect().center = self.center
        return self.rot_sprite

    def jump(self):
        self.velocity = -7
        self.rot_center(self.ang)

    def drop(self):
        self.velocity += self.y_change * gravity
        self.y += self.velocity
        self.rot_center(self.ang)
        if self.velocity > self.term_velocity:
            self.velocity = 15

    def get_data(self):
        self.fitness_score += 1
        self.inputs[0][0] = pipe.x_pos
        self.inputs[0][1] = self.velocity
        self.inputs[0][2] = math.sqrt(self.x**2+(self.y-pipe.my_list[score])**2)
        self.inputs[0][3] = math.sqrt(self.x**2+(pipe.my_list[score]-(150/2)-self.y)**2)
        self.inputs = np.asarray(self.inputs)

    def ff(self):
        l1 = np.tanh(np.dot(self.inputs, self.weights1))
        l2 = np.tanh(np.dot(l1, self.weights2))
        if l2[0] > 0.5 and not self.dead:
            global gravity
            gravity = 0
            self.jump()


def text_objects(text, font):
    text_surface = font.render(text, True, (255, 255, 255))
    return text_surface


def score_display(x_pos, y_pos):
    large_text = pygame.font.Font('font.TTF', 50)
    text_surf = text_objects(str(score), large_text)
    screen.blit(text_surf, (x_pos, y_pos))


def gen_display(x_pos, y_pos):
    large_text = pygame.font.Font('font.TTF', 50)
    text_surf = text_objects('Gen: %s' % str(gen), large_text)
    screen.blit(text_surf, (x_pos, y_pos))


def alive_display(x_pos, y_pos, alive):
    large_text = pygame.font.Font('font.TTF', 50)
    text_surf = text_objects('Alive: %s' % str(alive), large_text)
    screen.blit(text_surf, (x_pos, y_pos))


def find_parents():
    global parents, parents1
    largest1 = 0
    largest2 = 0
    wlargest1 = 0
    second1 = 0
    second2 = 0
    wsecond1 = 0
    large = []
    var = 0
    for i in fitness:
        large.append([i[0], i[1], i[2]])
    for x in range(len(large)):
        if large[x][0] > largest2:
            largest1 = large[x][1]
            wlargest1 = large[x][2]
            largest2 = large[x][0]
            var = x
        if large[x][0] > second2 and x != var:
            second1 = large[x][1]
            wsecond1 = large[x][2]
            second2 = large[x][0]
    parents = [largest1, second1]
    parents1 = [wlargest1, wsecond1]


def crossover():
    points = []
    for iiii in bird:
        weights1.append(iiii.weights1)
        weights2.append(iiii.weights2)
    for iiii in range(num+1):
        if iiii > num:
            break
        child = [[], []]
        parent1 = parents[0]
        parent2 = parents[1]
        wparent1 = parents1[0]
        wparent2 = parents1[1]
        while True:
            x1 = randint(0, len(parent1))
            x2 = randint(0, len(wparent1))
            if [x1, x2] in points:
                continue
            else:
                points.append([x1, x2])
                break
        for x in range(len(parent1)):
            child[0].append(0)
        for x in range(0, points[len(points)-1][0]):
            child[0][x] = parent1[x]
        for x in range(points[len(points)-1][0], len(parent1)):
            child[0][x] = parent2[x]
        for x in range(len(wparent1)):
            child[1].append(0)
        for x in range(0, points[len(points)-1][1]):
            child[1] = wparent1[x]
        for x in range(points[len(points)-1][1], len(wparent1)):
            child[1] = wparent2[x]
        weights1.append(child[0])
        weights2.append(child[1])


def mutate():
    mutation_rate = .65
    for swapped in range(num):
        individual = randint(0, num)
        if random() > mutation_rate:
            gene1 = np.random.uniform(low=-1.0, high=1.0, size=(6, ))
            x1 = randint(0, len([weights1][0][0])-1)
            weights1[individual][x1] = gene1
            gene2 = np.random.uniform(low=-1.0, high=1.0, size=(1, ))
            while True:
                try:
                    x2 = randint(0, len([weights2][0][0]))
                    weights2[individual][x2] = gene2
                    break
                except IndexError:
                    continue


def restart():
    global gravity, score, fitness, gen
    gen += 1
    find_parents()
    crossover()
    mutate()
    fitness = []
    gravity = 0
    for iiiii in bird:
        iiiii.velocity = 1
        iiiii.y = height/2-100
        iiiii.x = 0
        iiiii.ang = 0
        iiiii.fitness_score = 0
        iiiii.dead = False
    pipe.my_list = [randint(200, 450)]
    pipe.x_pos = width - 20
    pipe.y_pos = randint(200, 450)
    pipe.x_change = 3
    score = 0
    game_loop()


bird = []
for iii in range(num):
    bird.append(Bird(40, 30, 5, 0, height/2-100))


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_change, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)
        self.x_change = x_change
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.my_list = [self.y_pos]
        self.image1 = pygame.image.load('pipe.png')
        self.image1 = pygame.transform.scale(self.image1, (28 * 2, 600 * 2)).convert_alpha()
        self.image2 = pygame.image.load('pipe1.png')
        self.image2 = pygame.transform.scale(self.image2, (28 * 2, 600 * 2)).convert_alpha()
        self.rect1 = self.image1.get_rect()
        self.rect2 = self.image2.get_rect(center=(self.x_pos, self.my_list[score]))

    def render(self):
        screen.blit(self.image1, (self.x_pos, self.my_list[score] - (600 * 2 + 150)))
        screen.blit(self.image2, (self.x_pos, self.my_list[score]))

    def rect(self):
        self.rect1 = self.image1.get_rect(x=self.x_pos, y=self.my_list[score] - 150 - 600, width=(26 * 2) + 6, height=600)
        self.rect2 = self.image2.get_rect(x=self.x_pos, y=self.my_list[score], width=(26 * 2) + 7, height=height)

    def move(self):
        self.x_pos -= self.x_change


pipe = Pipe(3, width, randint(200, 450))


def game_loop():
    global score
    while True:
        screen.blit(back1, (0, 0))
        status = []
        for iiii in bird:
            status.append(iiii.dead)
            if iiii.y > height - 115 and not iiii.dead:
                iiii.dead = True
            elif iiii.y < -80 and not iiii.dead:
                iiii.dead = True
            if not iiii.dead:
                iiii.drop()
                iiii.render()
                iiii.rect()
                iiii.check_collision(pipe.rect1)
                iiii.check_collision(pipe.rect2)
                iiii.get_data()
                iiii.ff()
                fitness.append([iiii.fitness_score, iiii.weights1, iiii.weights2])
        alive = status.count(False)
        if status[0] and alive == 0:
            restart()
        if pipe.x_pos < -26:
            pipe.x_pos = width
            pipe.y_pos = randint(200, 450)
            score += 1
            if score > len(pipe.my_list) - 1:
                pipe.my_list.append(randint(200, 450))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        global gravity
        gravity += 0.01
        for iiii in bird:
            if iiii.velocity > 0:
                iiii.ang -= 5
            elif iiii.velocity < 0:
                iiii.ang += 5
            if iiii.ang > 90:
                iiii.ang = 90
            elif iiii.ang < -90:
                iiii.ang = -90
        pipe.render()
        screen.blit(back, (0, 0))
        pipe.rect()
        pipe.move()
        score_display(width / 2, 0)
        gen_display(0, 0)
        alive_display(0, 690, alive)
        clock.tick(60)
        pygame.display.flip()


game_loop()
