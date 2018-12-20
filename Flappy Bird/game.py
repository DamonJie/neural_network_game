import pygame
import random
import pygame.locals as locals
import neuro_evolution as neuro_evolution

pygame.init()
FPS = 50
SCREEN_SIZE = (300, 400)
PIPE_GAP_SIZE = 60  # 管道上下之间的间隙
surface = pygame.display.set_mode(SCREEN_SIZE)


class Bird(object):
    def __init__(self,neuronetwork):
        self.img = pygame.image.load("./bluebird-midflap.png")
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = 100
        self.y = SCREEN_SIZE[1] / 2 - self.height / 2
        self.speed = 0
        self.neuronetwork=neuronetwork

    def update(self):
        self.y -= self.speed
        if self.speed > -7:
            self.speed -= 1
        surface.blit(self.img, (self.x, self.y))

    def fly(self):
        self.speed = 7

    def is_dead(self, pipes):
        if self.y < 0 or self.y > SCREEN_SIZE[1] - self.height:
            return True
        for pipe in pipes:
            if self.x + self.width > pipe.x \
                    and self.x < pipe.x + pipe.width:
                if self.y < pipe.upper_y \
                        or self.y + self.height > pipe.lower_y:
                    return True
        return False

    def feed_value(self,pipes):
        inputs=[0.0,0.0]
        if len(pipes)>0:
            inputs[0]=self.x-pipes[0].x
            inputs[1]=(pipes[0].upper_y+pipes[0].lower_y)/2-self.y
            # inputs[2]=pipes[0].upper_y
            # inputs[3] = pipes[0].lower_y
            # inputs[4] = pipes[0].width
            ret=self.neuronetwork.feed_value(inputs)
            return ret[0]


class Pipe(object):
    IMAGES = (
        pygame.transform.rotate(
            pygame.image.load("./pipe-green.png").convert_alpha(), 180),
        pygame.image.load("./pipe-green.png").convert_alpha(),
    )

    def __init__(self):
        self.width = Pipe.IMAGES[0].get_width()
        self.height = Pipe.IMAGES[0].get_height()
        self.upper_y = random.randint(30, (SCREEN_SIZE[1] - PIPE_GAP_SIZE - 30))
        self.lower_y = self.upper_y + PIPE_GAP_SIZE
        self.x = SCREEN_SIZE[0]

    def update(self):
        self.x -= 4
        surface.blit(Pipe.IMAGES[0], (self.x, self.upper_y - self.height))
        surface.blit(Pipe.IMAGES[1], (self.x, self.lower_y))

    def need_remove(self):
        if self.x < -self.width:
            return True
        return False


class Game(object):
    def __init__(self):
        self.ai = neuro_evolution.AI()
        self.gen = 0
        self.max=0

    def start(self):
        self.network_list=self.ai.next_generation_network_list()
        self.birds= []
        self.pipes = []
        self.pipes.append(Pipe())
        self.score = 0
        for neuronetwork in self.network_list:
            self.birds.append(Bird(neuronetwork))
        self.gen+=1

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == locals.QUIT:
                    exit()
                # if event.type == locals.KEYDOWN and event.key == locals.K_SPACE:
                #     self.bird.fly()
            self.score += 1
            surface.fill((155, 155, 155))
            self.update_pipe()
            self.update_bird()
            pygame.display.update()
            if self.max<self.score:
                self.max=self.score
            print("代数："+str(self.gen)+"存活的小鸟数："+str(len(self.birds))+"分数："+str(self.score)+"最高分："+str(self.max))
            clock.tick(FPS)

    def update_pipe(self):
        for pipe in self.pipes:
            if pipe.need_remove():
                self.pipes.remove(pipe)
            else:
                pipe.update()
        if self.score % 100 == 0:
            self.pipes.append(Pipe())

    def update_bird(self):
        for bird in self.birds:
            if not bird.is_dead(self.pipes):
                ret=bird.feed_value(self.pipes)
                if ret:
                    if ret>0.5:
                        bird.fly()
                bird.update()
            else:
                self.birds.remove(bird)
                self.ai.gather_score(bird.neuronetwork,self.score)
        if self.all_dead():
            self.start()
    def all_dead(self):
        if len(self.birds)>0:
            return False
        else:
            return True

if __name__ == '__main__':
    game = Game()
    game.start()
    game.run()
