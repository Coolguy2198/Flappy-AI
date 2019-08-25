import pygame
from random import randint, random
import numpy as np

pygame.init()

height = 750
width = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('FlappyAI')
back = pygame.image.load('background.png').convert_alpha()
back1 = pygame.image.load('back.jpg').convert()
clock = pygame.time.Clock()
dead = False
ang = 0
smack = pygame.mixer.Sound('slap.wav')
flap = pygame.mixer.Sound('whoosh.wav')
score = 0
gravity = 0


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
        self.rot_sprite = 0
        self.velocity = 1
        self.in1 = 0
        self.in3 = 0
        self.in4 = 0
        self.inputs = [[], [], [], []]
        self.gen = 1
        self.num_weights = 4
        self.sol_per_pop = 6
        self.curr_bird = 0
        self.fitness_score = 0
        self.pop_size = (self.sol_per_pop, self.num_weights)
        self.new_population = np.random.uniform(low=-4.0, high=4.0, size=self.pop_size)
        self.weights2 = np.random.uniform(low=-4.0, high=4.0, size=(2, 1))
        self.fitness = [[], [], [], [], []]
        self.parents = []
        self.out = np.array([[0], [1]])
        self.time = 0

    def render(self):
        screen.blit(self.rot_sprite, (self.x, self.y))

    def check_collision(self, sprite):
        global dead
        if self.rect1.colliderect(sprite) and not dead:
            self.velocity = 0
            pygame.mixer.Sound.play(smack)
            pygame.mixer.music.stop()
            pipe.x_change = 0
            dead = True
            self.jump_d()
        elif self.y > height - 115 and dead:
            pipe.x_change = 0
            dead = True
            self.restart()
        elif self.y > height - 115 and not dead:
            pygame.mixer.Sound.play(smack)
            pygame.mixer.music.stop()
            pipe.x_change = 0
            dead = True
            self.restart()
        elif self.y < -80 and not dead:
            self.velocity = 7
            dead = True
            pygame.mixer.Sound.play(smack)
            pygame.mixer.music.stop()
            pipe.x_change = 0
            self.restart()
        elif self.y < -80 and dead:
            self.velocity = 7
            dead = True
            pipe.x_change = 0
            self.restart()

    def rect(self):
        self.rect1 = self.image.get_rect(x=self.x, y=self.y, width=40, height=30)

    def rot_center(self, angle):
        self.rot_sprite = pygame.transform.rotate(self.image, angle)
        self.rot_sprite.get_rect().center = self.center
        return self.rot_sprite

    def jump(self):
        global gravity
        pygame.mixer.Sound.play(flap)
        pygame.mixer.music.stop()
        self.velocity = -6
        gravity = 0
        self.rot_center(ang)

    def jump_d(self):
        self.velocity = -10
        self.rot_center(ang)

    def drop(self):
        self.velocity += self.y_change * gravity
        self.y += self.velocity
        self.rot_center(ang)
        if self.velocity > self.term_velocity:
            self.velocity = 15

    @staticmethod
    def score():
        global score
        score += 1

    @staticmethod
    def s(x):
        sig = 1.0 / (1.0 + np.exp(-1 * x))
        return sig

    @staticmethod
    def text_objects(text, font):
        text_surface = font.render(text, True, (255, 255, 255))
        return text_surface

    def score_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects(str(score), large_text)
        screen.blit(text_surf, (x_pos, y_pos))

    def gen_display(self, x_pos, y_pos):
        large_text = pygame.font.Font('font.TTF', 50)
        text_surf = self.text_objects(str(self.gen), large_text)
        screen.blit(text_surf, (x_pos, y_pos))

    def restart(self):
        global score, dead, gravity, ang
        dead = False
        if self.curr_bird > 4:
            self.find_parents()
            self.curr_bird = 0
            self.fitness = [[], [], [], [], []]
            self.crossover()
            self.mutate()
            self.gen += 1
        self.fitness[self.curr_bird] = [self.fitness_score, self.new_population[self.curr_bird]]
        self.fitness_score = 0
        ang = 0
        self.time = 0
        gravity = 0
        self.velocity = 1
        score = 0
        self.y = 0
        self.x = 0
        pipe.x_pos = width - 40
        pipe.y_pos = randint(0, 650)
        pipe.x_change = 3
        self.curr_bird += 1
        self.new_population = np.random.uniform(high=1.0, low=0.0, size=self.pop_size)
        game_loop()

    def get_data(self):
        self.fitness_score += 1
        self.in1 = pipe.x_pos
        self.in3 = (pipe.y_pos - 29) - self.y
        self.in4 = (pipe.y_pos - 119) - self.y
        self.inputs[0] = self.in1
        self.inputs[1] = self.velocity
        self.inputs[2] = self.in3
        self.inputs[3] = self.in4
        self.inputs = np.asarray(self.inputs)

    def find_parents(self):
        largest1 = 0
        largest2 = 0
        second1 = 0
        second2 = 0
        backup = randint(0, 4)
        list1 = []
        list2 = []
        list3 = []
        for i in self.fitness:
            list1.append(i[0])
            list2.append(i[1])
            list3.extend([[i[0], i[1]]])
        for x in range(len(list3)):
            if list3[x][0] > largest2:
                largest1 = list3[x][1]
                largest2 = list3[x][0]
                while x == backup:
                    backup = randint(0, 4)
            if list3[x][0] < largest2 and list3[x][0] > second2:
                second1 = list3[x][1]
                second2 = list3[x][0]
            if second2 == 0:
                second1 = list3[backup][1]
                second2 = list3[backup][0]
        self.parents = [largest1, second1]

    def crossover(self):
        x = np.random.randint(1, 4)
        tmp1 = self.parents[1][:x].copy()
        tmp2 = self.parents[0][:x].copy()
        self.new_population[1][:x], self.new_population[0][:x] = self.parents[0][:x], tmp1
        self.new_population[2][:x], self.new_population[3][:x] = self.parents[1][:x], tmp2

    def mutate(self):
        mutation_rate = .5
        individual = randint(0, 5)
        for swapped in range(len(self.new_population[individual])):
            if random() < mutation_rate:
                swap_with = int(random() * len(self.new_population[individual]))
                gene1 = self.new_population[individual][swapped]
                gene2 = self.new_population[individual][swap_with]
                self.new_population[individual][swap_with] = gene2
                self.new_population[individual][swapped] = gene1

    def ff(self):
        l1 = np.tanh(np.dot(self.inputs, self.new_population[self.curr_bird]))
        l2 = np.tanh(np.dot(l1, self.weights2))
        print(l2)
        if l2[1] >= 0.5 and not dead:
            self.jump()


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_change, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)
        self.x_change = x_change
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image1 = pygame.image.load('pipe.png')
        self.image1 = pygame.transform.scale(self.image1, (28 * 2, 600 * 2)).convert_alpha()
        self.image2 = pygame.image.load('pipe1.png')
        self.image2 = pygame.transform.scale(self.image2, (28 * 2, 600 * 2)).convert_alpha()
        self.rect1 = self.image1.get_rect()
        self.rect2 = self.image2.get_rect()

    def render(self):
        if self.y_pos < 170:
            self.y_pos = 170
        screen.blit(self.image1, (self.x_pos, self.y_pos - (600 * 2 + 90)))
        screen.blit(self.image2, (self.x_pos, self.y_pos))

    def rect(self):
        self.rect1 = self.image1.get_rect(x=self.x_pos, y=self.y_pos - 90 - 600, width=(26 * 2) + 6, height=600)
        self.rect2 = self.image2.get_rect(x=self.x_pos, y=self.y_pos, width=(26 * 2) + 7, height=height)

    def move(self):
        self.x_pos -= self.x_change


pipe = Pipe(3, width, randint(0, 650))
bird = Bird(40, 30, 5, 0, 0)


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
        bird.score_display(width / 2, 0)
        bird.gen_display(10, 0)
        screen.blit(back, (0, 0))
        bird.get_data()
        bird.ff()
        if pipe.x_pos < -26:
            pipe.x_pos = width - 40
            pipe.y_pos = randint(100, 650)
            bird.score()
            bird.passed = False
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
        clock.tick(200)
        pygame.display.flip()
        pygame.time.delay(10)


game_loop()
