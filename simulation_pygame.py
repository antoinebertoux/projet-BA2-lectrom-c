import pygame
import sys
import random

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)

class Tube:
    def __init__(self, position, radius, scr):
        self.position = position
        self.radius = radius
        self.screen = scr
        self.draw()
    def draw(self):
        pygame.draw.circle(self.screen, blue, self.position, self.radius, 0)

    def setPosition(self, pos):
        self.position = pos
        self.draw()

def get_background():
    background = pygame.Surface((1500,800))
    background.fill(white)
    pygame.draw.rect(background, black, (50,50,1400,700), 16)
    pygame.draw.line(background, black, (285,50), (285,750), 16)
    pygame.draw.line(background, black, (50,400), (285,400), 16)
    tube_point_list = []
    x = 360
    y = 160
    for i in range(6):
        pygame.draw.line(background, black, (x,y), (x,y+470), 16)
        tube_point_list.append((x,y+110))
        tube_point_list.append((x,y+360))
        if i%2==1 and i<5:
            pygame.draw.line(background, black, (x,y), (x+200,y), 16)
        elif i<5:
            pygame.draw.line(background, black, (x,y+470), (x+200,y+470), 16)
        x+=200
    return background, tube_point_list

screen = pygame.display.set_mode((1500,800))
pygame.init()
background, tube_point_list = get_background()
tube_point_list = random.sample(tube_point_list, 6)
tube_radius_list = [18,18,20,20,25,25]
tube_list = []
for i in range(6):
    tube_list.append(Tube(tube_point_list[i], tube_radius_list[i], background))

while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 pygame.quit();
                 sys.exit()
    screen.blit(background, (0,0))
    pygame.display.update()
