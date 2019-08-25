import pygame
from random import randint, random
import numpy as np
import sys

sys.setrecursionlimit(10000)

pygame.init()

height = 750
width = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('FlappyAI')
back = pygame.image.load('background.png').convert_alpha()
back1 = pygame.image.load('back.jpg').convert()
clock = pygame.time.Clock()
gravity = 0
dead = False
ang = 0
smack = pygame.mixer.Sound('slap.wav')
flap = pygame.mixer.Sound('whoosh.wav')
score = 0
np.random.seed()


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
        self.inputs = [[], [], [], [], [], []]
        self.gen = 1
        self.num_weights = 6
        self.sol_per_pop = 6
        self.curr_bird = 0
        self.fitness_score = 0
        self.weights2 = np.random.uniform(low=-4.0, high=4.0, size=(2, 1))
        self.fitness = [[[]], [[]], [[]], [[]], [[]]]
        self.pop_size = (self.sol_per_pop, self.num_weights)
        self.new_population = np.random.uniform(low=-4.0, high=4.0, size=self.pop_size)
        self.parents = []
        self.parents1 = []
        self.score1 = 0
        self.out = np.array([[0], [1]])
        self.tmp1 = 0
        self.tmp2 = 0

    def render(self):
        screen.blit(self.rot_sprite, (self.x, self.y))

    def check_collision(self, sprite):
        global dead
        if self.rect1.colliderect(sprite) and not dead:
            dead = True
            self.restart()
        elif self.y > height - 115 and dead:
            dead = True
            self.restart()
        elif self.y > height - 115 and not dead:
            dead = True
            self.restart()
        elif self.y < -80 and not dead:
            dead = True
            self.restart()
        elif self.y < -80 and dead:
            dead = True
            self.restart()

    def rect(self):
        self.rect1 = self.image.get_rect(x=self.x, y=self.y, width=40, height=30)

    def rot_center(self, angle):
        self.rot_sprite = pygame.transform.rotate(self.image, angle)
        self.rot_sprite.get_rect().center = self.center
        return self.rot_sprite

    def jump(self):
        self.velocity = -7
        self.rot_center(ang)

    def jump_d(self):
        self.velocity = -7
        self.rot_center(ang)

    def drop(self):
        self.velocity += self.y_change * gravity
        self.y += self.velocity
        self.rot_center(ang)
        if self.velocity > self.term_velocity:
            self.velocity = 15

    def score(self):
        self.score1 += 1

    @staticmethod
    def s(x):
        return np.tanh(x)

    @staticmethod
    def text_objects(text, font):
        text_surface = font.render(text, True, (255, 255, 255))
        return text_surface

    def gen_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects(str(self.gen), large_text)
        screen.blit(text_surf, (x_pos, y_pos))

    def restart(self):
        global dead, gravity, ang
        dead = False
        if self.curr_bird > 4:
            self.gen += 1
            self.find_parents()
            self.curr_bird = 0
            self.fitness = [[], [], [], [], []]
            self.crossover()
            self.mutate()
            pipe.my_list = [randint(0, 650)]
        self.fitness[self.curr_bird] = [self.fitness_score, self.new_population[self.curr_bird], self.weights2]
        self.fitness_score = 0
        ang = 0
        gravity = 0
        self.velocity = 1
        self.y = 0
        self.x = 0
        pipe.x_pos = width - 20
        pipe.y_pos = randint(0, 650)
        pipe.x_change = 3
        self.curr_bird += 1
        self.score1 = 0
        game_loop()

    def get_data(self):
        self.fitness_score += 1
        self.in1 = pipe.x_pos
        self.in3 = (pipe.my_list[self.score1] - 29) - self.y
        self.in4 = (pipe.my_list[self.score1] - 119) - self.y
        self.in5 = self.y
        self.in6 = pipe.my_list[self.score1] - (150 / 2)
        self.inputs[0] = self.in1
        self.inputs[1] = self.velocity
        self.inputs[2] = self.in3
        self.inputs[3] = self.in4
        self.inputs[4] = self.in5
        self.inputs[5] = self.in6
        self.inputs = np.asarray(self.inputs)

    def find_parents(self):
        largest1 = 0
        largest2 = 0
        wlargest1 = 0
        wlargest2 = 0
        second1 = 0
        second2 = 0
        wsecond1 = 0
        wsecond2 = 0
        list3 = []
        for i in self.fitness:
            list3.extend([[i[0], i[1], i[2]]])
        for x in range(len(list3)):
            if list3[x][0] > largest2:
                largest1 = list3[x][1]
                largest2 = list3[x][0]
            if list3[x][0] < largest2 and list3[x][0] > second2:
                second1 = list3[x][1]
                second2 = list3[x][0]
            if list3[x][0] > wlargest2:
                wlargest1 = list3[x][2]
                wlargest2 = list3[x][0]
            if list3[x][0] < wlargest2 and list3[x][0] > wsecond2:
                wsecond1 = list3[x][2]
                wsecond2 = list3[x][0]
        self.parents = [largest1, second1]
        self.parents1 = [wlargest1, wsecond1]

    def crossover(self):
        self.tmp1 = self.parents[1][:3].copy()
        self.tmp2 = self.parents[0][:3].copy()
        self.new_population[1][3:], self.new_population[0][3:] = self.parents[0][:3], self.tmp1
        self.new_population[2][3:], self.new_population[3][3:] = self.parents[1][:3], self.tmp2
        wtmp1 = self.parents1[1][:1].copy()
        wtmp2 = self.parents1[0][:1].copy()
        self.weights2[1][1:], self.weights2[0][1:] = self.parents1[0][:1], wtmp1
        self.weights2[0][1:], self.weights2[1][1:] = self.parents1[1][:1], wtmp2

    def mutate(self):
        mutation_rate = .2
        individual = randint(0, 5)
        for swapped in range(len(self.new_population[individual])):
            if random() < mutation_rate:
                swap_with = int(random() * len(self.new_population[individual]))
                gene1 = self.new_population[individual][swapped]
                gene2 = self.new_population[individual][swap_with]
                self.new_population[individual][swap_with] = gene2
                self.new_population[individual][swapped] = gene1

    def ff(self):
        l1 = self.s(np.dot(self.inputs, self.new_population[self.curr_bird]))
        l2 = self.s(np.dot(l1, self.weights2))
        if l2[0] >= 0. and not dead:
            global gravity
            gravity = 0
            self.jump()

    def score_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects(str(self.score1), large_text)
        screen.blit(text_surf, (x_pos, y_pos))

    def gen_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects('Gen: ' + str(self.gen), large_text)
        screen.blit(text_surf, (x_pos, y_pos))


bird = Bird(40, 30, 5, 0, 0)


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
        self.rect2 = self.image2.get_rect(center=(self.x_pos, self.my_list[bird.score1]))

    def render(self):
        if self.my_list[bird.score1] < 200:
            self.my_list[bird.score1] = 200
        elif self.my_list[bird.score1] > height:
            self.my_list[bird.score1] = height
        screen.blit(self.image1, (self.x_pos, self.my_list[bird.score1] - (600 * 2 + 150)))
        screen.blit(self.image2, (self.x_pos, self.my_list[bird.score1]))

    def rect(self):
        self.rect1 = self.image1.get_rect(x=self.x_pos, y=self.my_list[bird.score1] - 150 - 600, width=(26 * 2) + 6, height=600)
        self.rect2 = self.image2.get_rect(x=self.x_pos, y=self.my_list[bird.score1], width=(26 * 2) + 7, height=height)

    def move(self):
        self.x_pos -= self.x_change


pipe = Pipe(3, width, randint(0, 650))


def game_loop():
    while True:
        bird.rand_state = randint(0, 1)
        pygame.display.set_icon(bird.image)
        screen.blit(back1, (0, 0))
        bird.drop()
        pipe.render()
        pipe.move()
        pipe.rect()
        bird.rect()
        bird.render()
        bird.check_collision(pipe.rect1)
        bird.check_collision(pipe.rect2)
        screen.blit(back, (0, 0))
        bird.get_data()
        bird.ff()
        bird.score_display(width/2, 0)
        bird.gen_display(0, height - 60)
        if pipe.x_pos < -26:
            pipe.x_pos = width
            pipe.y_pos = randint(100, 650)
            bird.passed = False
            bird.score()
            if bird.score1 > len(pipe.my_list) - 1:
                pipe.my_list.append(randint(0, 650))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        global gravity
        gravity += 0.01
        if bird.velocity > 0:
            global ang
            ang -= 5
        elif bird.velocity < 0:
            ang += 5
        if ang > 90:
            ang = 90
        elif ang < -90:
            ang = -90
        clock.tick(60)
        pygame.display.flip()


game_loop()
