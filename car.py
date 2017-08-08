#!/usr/bin/python

import os
import pygame
import copy
import math
import numpy as np
import pickle
import time
from random import randrange, uniform, randint
from pygame.locals import *



class RaceObject(pygame.sprite.Sprite):
    obj_counter  = 0

    def __init__(self,file_name,starting_grid_pos,terrain,individuos):
        
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = pygame.image.load(file_name).convert_alpha()
        self.image_ref = copy.copy(self.image)

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.starting_grid_pos = starting_grid_pos
        
        self.direction = 0
        self.forward   = 0

        self.prev_direction = 0
        self.prev_forward   = 0

        self.origin_pos = [0,0]
        self.unitx = 0
        self.unity = 0
        self.actual_step = 0

        self.collision_count = 0

        self.set_pos(starting_grid_pos)
        self.terrain      = terrain
        self.terrain_mask = pygame.mask.from_surface(terrain, 50)
        self.obj_id = RaceObject.obj_counter
        RaceObject.obj_counter += 1

        self.syn0 = individuos[0]
        self.syn1 = individuos[1]

        self.fitness = 0.0
        self.crash = 0

    def terrain_overlap(self):
        return self.terrain_mask.overlap(self.mask,(self.rect[0],self.rect[1]))

    def set_pos(self,pos):
        self.rect[0] = pos[0]
        self.rect[1] = pos[1]

    def set_keymap(self,keymap):
        self.keymap = keymap

    def rot_center(self,image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def draw(self,screen):
        screen.blit(self.image,(self.rect[0],self.rect[1]))

    def update_pos(self,dt=1):
        if self.direction != 0 or self.forward !=0:
            self.unitx = math.cos(math.radians(self.direction))
            self.unity = math.sin(math.radians(self.direction))
            if self.direction != self.prev_direction:

                self.actual_step = 0
                
                self.image = self.rot_center(self.image_ref,-self.direction)
                self.mask = pygame.mask.from_surface(self.image)

                self.prev_direction = self.direction
                self.origin_pos[0] = self.rect[0]
                self.origin_pos[1] = self.rect[1]

            if self.forward != self.prev_forward:

                self.origin_pos[0] = self.rect[0]
                self.origin_pos[1] = self.rect[1]

                self.actual_step = self.forward
                self.prev_forward   = self.forward

            self.step_forward()
    def get_sonar_values(self,screen,angles,distances):
        ret = []

        xfront = math.cos(math.radians(self.direction))
        yfront = math.sin(math.radians(self.direction))
        #print xfront,yfront, self.image_ref.get_rect()

        xfront = int(xfront+ self.rect[0]+self.image_ref.get_width()/2.0)
        yfront = int(yfront+ self.rect[1]+self.image_ref.get_height()/2.0)

        for i in range(len(angles)):

            angle = angles[i] + self.direction
            dist  = distances[i]
            xmax = math.cos(math.radians(angle)) *dist
            ymax = math.sin(math.radians(angle)) *dist
            x = np.linspace(0,xmax,10).astype(int)
            y = np.linspace(0,ymax,10).astype(int)

            #print xmax,ymax,x,y
            acc = 0 
            for (xpos,ypos) in zip(x,y):
                xpos += xfront  
                ypos += yfront 
                #print xpos,ypos, (255-np.average(screen.get_at((xpos,ypos))))
                try:
                    acc += (255-np.average(screen.get_at((xpos,ypos))))
                except:
                    acc += 0
                pygame.draw.line(screen,[255,0,0],(xfront,yfront),(xpos,ypos))
            ret.append(acc)
        return ret

    def step_forward(self):
        if self.forward != 0:
            i = self.actual_step
            x = self.unitx*self.actual_step
            if self.unitx == 0:
                y = 0
            else:
                y = (self.unity/self.unitx)*x 

            self.rect[0] = self.origin_pos[0]+x
            self.rect[1] = self.origin_pos[1]+y

            self.actual_step+=self.forward

    def eval_event(self,events,saidas):
        
        for e in events:
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                return False
        
        if self.crash == 0:
            if saidas[0] > 0.2 and self.forward < 5.0:
                self.forward += 0.5
            else:
                self.forward -= 0.5
            if saidas[1] > 0.6:
                self.direction += 6
            else:
                self.direction -= 6

        return True

    def mlp(self, sonar):
        l1 = np.dot(sonar,self.syn0)
        l1 = nonlin(l1)
        l1 = np.dot(l1, self.syn1)
        
        return nonlin(l1)

def nonlin(x, deriv = False):
    if(deriv==True):
        return (x*(1-x))
    
    return 1/(1+np.exp(-x))

def select(n, cars):
	cars = sorted(cars, key=lambda tupla: tupla.fitness)

	if n > 1:
		melhor = [cars[-1], cars[-2]]
		synNovosIndividuos = [melhor[0].syn0,melhor[0].syn1,melhor[1].syn0,melhor[1].syn1]
		file = open("MelhoresIndividuos.pickle", "wb")
		pickle.dump(synNovosIndividuos, file, protocol = 2)
		file.close()
		cross_over(melhor,n, cars)    
		mutation(n, cars)
    
	else:
		melhor = cars[0]
		synNovosIndividuos = [melhor.syn0, melhor.syn1]
		file = open("MelhoresIndividuos.pickle", "wb")
		pickle.dump(synNovosIndividuos, file, protocol = 2)
		file.close()
		mutation(n, cars)

def cross_over(pais, n, cars):
    x = randint(0,1)

    car_aux = copy.deepcopy([pais[x].syn0, pais[1-x].syn1])

    if n > 1:
        car_aux2 = copy.deepcopy([pais[1-x].syn0, pais[x].syn1])

    for i in range(0,n-1):
        if n%2 == 0:
            cars[i].syn0 = copy.deepcopy(car_aux[0])
            cars[i].syn1 = copy.deepcopy(car_aux[1])
        else:
            cars[i].syn0 = copy.deepcopy(car_aux2[0])
            cars[i].syn1 = copy.deepcopy(car_aux2[1])


def mutation(n, cars):
    for i in range(0,n-1):
        if cars[i].fitness >= 30:
            lin = randrange(0, 8)
            col = randrange(0, 4)
            lin1 = randrange(0, 4)
            col1 = randrange(0, 2)
            cars[i].syn0[lin,col] = uniform(0,0.5)
            cars[i].syn1[lin1,col1] = uniform(-0.5,0.5)
        elif cars[i].fitness < 30 and cars[i].fitness > 18:
            for k in range(0,1):
                lin = randrange(0, 8)
                col = randrange(0, 4)
                cars[i].syn0[lin,col] = uniform(0,1)
            for l in range(0,1):    
                lin1 = randrange(0, 4)
                col1 = randrange(0, 2)
                cars[i].syn1[lin1,col1] = uniform(-0.5,0.5)
        elif cars[i].fitness < 18 and cars[i].fitness > 10:
            for k in range(0, 2):
                lin = randrange(0, 8)
                col = randrange(0, 4)
                cars[i].syn0[lin,col] = uniform(0,1)*cars[i].syn0[lin,col]
            for l in range(0,1):    
                lin1 = randrange(0, 4)
                col1 = randrange(0, 2)
                cars[i].syn1[lin1,col1] = uniform(-1,1)*cars[i].syn1[lin1,col1]
        elif cars[i].fitness < 10:
            for k in range(0,4):
                lin = randrange(0, 8)
                col = randrange(0, 4)
                cars[i].syn0[lin,col] = uniform(-1,1)*cars[i].syn0[lin,col]
            for l in range(0,1):    
                lin1 = randrange(0, 4)
                col1 = randrange(0, 2)
                cars[i].syn1[lin1,col1] = uniform(-1,1)*cars[i].syn1[lin1,col1]
        elif cars[i].fitness < 3:
            for k in range(0,10):
                lin = randrange(0, 8)
                col = randrange(0, 4)
                cars[i].syn0[lin,col] = uniform(-1,1)*cars[i].syn0[lin,col]
            for l in range(0,3):    
                lin1 = randrange(0, 4)
                col1 = randrange(0, 2)
                cars[i].syn1[lin1,col1] = uniform(-1,1)*cars[i].syn1[lin1,col1]

if __name__ == '__main__':
    if not hasattr(pygame, "Mask"):
        raise "Need pygame 1.8 for masks."

    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((640,480))
    pygame.key.set_repeat(500, 2)
    clock = pygame.time.Clock()


    # fill the screen 
    screen.fill((255,255,255))
    pygame.display.flip()
    pygame.display.set_caption("Trabalho de IA")


    terrain1 = pygame.image.load("terrain2.png").convert_alpha()


    starting_grid   = [[130,85],[170,85],[210,75],[250,75],[290,85],[330,85],[380,85], [420,85]]
    car_image_files = ["carro.png","carro.png", "carro.png","carro.png","carro.png","carro.png","carro.png","carro.png","carro.png","carro.png"]
    
    car_keymap      = [{'right':K_RIGHT,'left':K_LEFT,'up':K_UP,'down':K_DOWN,'pause':K_SPACE},
                           {'right':K_l,'left':K_j,'up':K_i,'down':K_k,'pause':K_p},
                           {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x},
                           {'right':K_l,'left':K_j,'up':K_i,'down':K_k,'pause':K_p},
                           {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x},
                           {'right':K_l,'left':K_j,'up':K_i,'down':K_k,'pause':K_p},
                           {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x},
                           {'right':K_l,'left':K_j,'up':K_i,'down':K_k,'pause':K_p},
                           {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x},
                           {'right':K_l,'left':K_j,'up':K_i,'down':K_k,'pause':K_p}]

    # n e o numero de carros a serem criados
    n = 8
    cars = []
    arq = open("individuos.pickle","rb")
    individuos = pickle.load(arq)
    arq.close()
    
    for i in range(n):
        car = RaceObject(car_image_files[i], starting_grid[i], terrain1, individuos[i])
        car.set_keymap(car_keymap[i])
        cars.append(car)
        
    # message font
    afont = pygame.font.Font(None, 16)

    # start the main loop.
    going = 1
    gameOver = 0 #termina
    t1 = time.time() #retorna tempo atual
    while going:
        events = pygame.event.get()
        for car in cars:
            sonar = car.get_sonar_values(screen,[0,30,-30,60,-60,90,-90,180],[100,50,50,50,50,50,50,50])
            going = car.eval_event(events,car.mlp(sonar))
            car.update_pos()


        # draw the background color, and the terrain.
        screen.fill((255,255,255))
        screen.blit(terrain1, (0,0))

        # draw cars.
        msg_y = 0
        for car in cars:
            car.draw(screen)
            if car.terrain_overlap():
                hitsurf = afont.render("Car "+str(car.obj_id)+" terrain hit!", 1, (255,255,255))
                if car.fitness == 0.0:
                    car.fitness = - (t1 - time.time() )


                    gameOver += 1
                    car.crash = 1
                screen.blit(hitsurf, (0,msg_y))
                msg_y+=20
                # limit the speed
                car.forward   = 0


        #check collision among cars
        # if len(cars) > 1: 
        #     for i in range(len(cars)):
        #         for j in range(i+1,len(cars)):
        #             offset = (cars[i].rect[0]-cars[j].rect[0],cars[i].rect[1]-cars[j].rect[1])
        #             if cars[i].mask.overlap(cars[j].mask,offset):
        #                 cars[i].forward = 0
        #                 if cars[i].fitness == 0.0:
        #                     cars[i].fitness = - (t1 - time.time() )

        #                     gameOver += 1
                        
        #                 cars[j].forward = 0
        #                 if cars[j].fitness == 0.0:
        #                     cars[j].fitness = - (t1 - time.time() )
                            
        #                     gameOver += 1
                        
        #                 hitsurf = afont.render("Collision!! Cars "+str(cars[i].obj_id)+" and "+str(cars[j].obj_id), 1, (255,255,255))
        #                 screen.blit(hitsurf, (0,msg_y))
        #                 msg_y+=20
     
        if gameOver >= n or time.time() - t1 >= 45:
            break

        # flip the display.
        pygame.display.flip()

        # limit the frame rate.
        clock.tick(120)
    #pais recebe os dois melhores para realizar o cross-over
    select(n, cars)

    synNovosIndividuos = list()

    for car in cars:
		car.fitness = 0.0
		synNovosIndividuos.append([car.syn0,car.syn1])
    
    file = open("individuos.pickle", "wb")
    pickle.dump(synNovosIndividuos, file, protocol = 2)
    file.close()

    pygame.quit()
