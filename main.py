from random import randint, random
import numpy as np
import sys
import pygame

sys.setrecursionlimit(100000)
pygame.init()

height = 750
width = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('FlappyAI')
back = pygame.image.load('background.png').convert_alpha()
back1 = pygame.image.load('back.jpg').convert()
whoosh = pygame.mixer.Sound('whoosh.wav')
slap = pygame.mixer.Sound('slap.wav')
up = pygame.mixer.Sound('level_up.wav')
evolve = pygame.mixer.Sound('Absorb.wav')
clock = pygame.time.Clock()
gravity = 0
dead = False
ang = 0
score = 0


class Bird(pygame.sprite.Sprite):
    def __init__(self, bird_width, bird_height, y_change, x, y, num):
        pygame.sprite.Sprite.__init__(self)
        self.num = num
        self.image = pygame.image.load('bird.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (bird_width, bird_height))
        self.bird_width = bird_width
        self.bird_height = bird_height
        self.y_change = y_change
        self.x = x
        self.x = int(self.x)
        self.y = y
        self.y = int(self.y)
        self.term_velocity = 15
        self.rect1 = self.image.get_rect()
        self.center = self.rect1.center
        self.rot_sprite = None
        self.velocity = 1
        self.in1 = 0
        self.in3 = 0
        self.in4 = 0
        self.in6 = 0
        self.inputs = [[], [], [], [], [], []]
        self.gen = 1
        self.num_weights = len(self.inputs)
        self.curr_bird = 0
        self.fitness_score = 0
        self.weights2 = []
        self.new_population = []
        for i in range(self.num + 1):
            self.new_population.append(np.random.uniform(low=-1.0, high=1.0, size=(6, 10)))
        for i in range(self.num+1):
            self.weights2.append(np.random.uniform(low=-1.0, high=1.0, size=(10, 2)))
        self.fitness = []
        for i in range(self.num):
            self.fitness.append([])
        self.parents = []
        self.parents1 = []
        self.score1 = 0
        self.max_score = 0

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
        self.rect1 = self.image.get_rect(x=self.x, y=self.y, width=self.bird_width, height=self.bird_height)

    def rot_center(self, angle):
        self.rot_sprite = pygame.transform.rotate(self.image, angle)
        self.rot_sprite.get_rect().center = self.center
        return self.rot_sprite

    def jump(self):
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
        pygame.mixer.Sound.play(up)
        pygame.mixer.music.stop()
        if self.score1 > self.max_score:
            self.max_score = self.score1

    @staticmethod
    def s(x):
        return np.tanh(x)

    @staticmethod
    def text_objects(text, font):
        text_surface = font.render(text, True, (255, 255, 255))
        return text_surface

    def restart(self):
        global dead, gravity, ang
        dead = False
        pygame.mixer.Sound.play(slap)
        pygame.mixer.music.stop()
        if self.curr_bird == self.num:
            pygame.mixer.Sound.play(evolve)
            pygame.mixer.music.stop()
            self.gen += 1
            self.find_parents()
            self.curr_bird = 0
            self.fitness = []
            for i in range(self.num):
                self.fitness.append([])
            self.crossover()
            pipe.my_list = [randint(250, 450)]
        self.fitness[self.curr_bird] = [self.fitness_score, self.new_population[self.curr_bird], self.weights2]
        self.fitness_score = 0
        ang = 0
        gravity = 0
        self.velocity = 1
        self.y = height/2-100
        self.x = 0
        pipe.x_pos = width - 20
        pipe.y_pos = randint(250, (750-115)-250)
        pipe.x_change = 3
        self.curr_bird += 1
        self.score1 = 0
        game_loop()

    def get_data(self):
        self.fitness_score += 1
        self.in1 = pipe.x_pos
        self.in3 = (pipe.my_list[self.score1] - 29) - self.y
        self.in4 = (pipe.my_list[self.score1] - 119) - self.y
        self.in6 = pipe.my_list[self.score1] - (150 / 2)
        self.inputs[0] = self.in1
        self.inputs[1] = self.velocity
        self.inputs[2] = self.in3
        self.inputs[3] = self.in4
        self.inputs[4] = self.y
        self.inputs[5] = self.in6
        self.inputs = np.asarray(self.inputs)
        self.inputs = self.inputs / np.linalg.norm(self.inputs)

    def find_parents(self):
        largest1 = 0
        largest2 = 0
        wlargest1 = 0
        wlargest2 = 0
        second1 = 0
        second2 = 0
        wsecond1 = 0
        wsecond2 = 0
        large = []
        for i in self.fitness:
            large.extend([[i[0], i[1], i[2]]])
        for x in range(len(large)):
            if large[x][0] > largest2:
                largest1 = large[x][1]
                largest2 = large[x][0]
            if largest2 > large[x][0] > second2:
                second1 = large[x][1]
                second2 = large[x][0]
            if large[x][0] > wlargest2:
                wlargest1 = large[x][2][0]
                wlargest2 = large[x][0]
            if wlargest2 > large[x][0] > wsecond2:
                wsecond1 = large[x][2][0]
                wsecond2 = large[x][0]
        self.parents = [largest1, second1]
        self.parents1 = [wlargest1, wsecond1]

    def crossover(self):
        for i in range(self.num):
            if i > self.num:
                break
            child = []
            child2 = []
            parent1 = self.parents[0]
            parent2 = self.parents[1]
            wparent1 = self.parents1[0]
            wparent2 = self.parents1[1]
            start = randint(0, len(parent1))
            end = randint(0, len(parent1))
            while start == end or end < start:
                start = randint(0, len(parent1))
                end = randint(0, len(parent1))
            start2 = randint(0, len(wparent1))
            end2 = randint(0, len(wparent1))
            while start2 == end2 or end2 < start2 or start2 > end2:
                start2 = randint(0, len(parent1))
                end2 = randint(0, len(parent1))
            for x in range(len(parent1)):
                child.append(0)
            for x in range(len(wparent1)):
                child2.append(0)
            for x in range(0, start):
                child[x] = parent1[x]
            for x in range(start, end):
                child[x] = parent2[x]
            for x in range(end, len(child)):
                child[x] = parent1[x]
            for x in range(0, start2):
                child2[x] = wparent1[x]
            for x in range(start2, end2):
                child2[x] = wparent2[x]
            for x in range(end2, len(child2)):
                child2[x] = wparent1[x]
            self.new_population[i] = child
            self.weights2[i] = child2

    def mutate(self):
        mutation_rate = .2
        mutations = 0
        for swapped in range(self.num):
            individual = randint(0, self.num)
            x = 0
            if random() > mutation_rate:
                x += 1
                if x > len(self.new_population[individual]):
                    x = 0
                test = self.new_population[individual]
                mutations += 1
                swap_with = int(random() * len(test))
                gene1 = self.new_population[individual][x]
                gene2 = self.new_population[individual][swap_with]
                self.new_population[individual][swap_with] = gene2
                self.new_population[individual][x] = gene1

    def ff(self):
        l1 = self.s(np.dot(self.inputs, self.new_population[self.curr_bird]))
        l2 = self.s(np.dot(l1, self.weights2[self.curr_bird]))
        if l2[0] > 0 and not dead:
            global gravity
            pygame.mixer.Sound.play(whoosh)
            pygame.mixer.music.stop()
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

    def curr_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects('Bird: ' + str(self.curr_bird), large_text)
        screen.blit(text_surf, (x_pos, y_pos))

    def highscore(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects('HS: ' + str(self.max_score), large_text)
        screen.blit(text_surf, (int(x_pos), int(y_pos)))


bird = Bird(40, 30, 5, 0, height/2-100, 15)
pygame.display.set_icon(bird.image)


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
        screen.blit(self.image1, (self.x_pos, self.my_list[bird.score1] - (600 * 2 + 150)))
        screen.blit(self.image2, (self.x_pos, self.my_list[bird.score1]))

    def rect(self):
        self.rect1 = self.image1.get_rect(x=self.x_pos, y=self.my_list[bird.score1] - 150 - 600, width=(26 * 2) + 6, height=600)
        self.rect2 = self.image2.get_rect(x=self.x_pos, y=self.my_list[bird.score1], width=(26 * 2) + 7, height=height)

    def move(self):
        self.x_pos -= self.x_change


pipe = Pipe(3, width, randint(250, (750-115)-250))


def game_loop():
    while True:
        bird.rand_state = randint(0, 1)
        screen.blit(back1, (0, 0))
        bird.drop()
        pipe.render()
        pipe.move()
        pipe.rect()
        bird.rect()
        bird.render()
        bird.check_collision(pipe.rect1)
        bird.check_collision(pipe.rect2)
        bird.get_data()
        bird.ff()
        screen.blit(back, (0, 0))
        bird.score_display(int(width/2), 0)
        bird.gen_display(0, int(height - 60))
        bird.curr_display(0, 0)
        bird.highscore(width/2, height-60)
        if pipe.x_pos < -26:
            pipe.x_pos = width
            pipe.y_pos = randint(250, (750-115)-250)
            bird.passed = False
            bird.score()
            if bird.score1 > len(pipe.my_list) - 1:
                pipe.my_list.append(randint(250, (750-115)-250))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        global gravity, ang
        gravity += 0.01
        if bird.velocity > 0:
            ang -= 5
        elif bird.velocity < 0:
            ang += 5
        if ang > 90:
            ang = 90
        elif ang < -90:
            ang = -90
        clock.tick(50)
        pygame.display.flip()


game_loop()
