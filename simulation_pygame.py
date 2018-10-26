import pygame
import sys

white = (255,255,255)
black = (0,0,0)

def draw_background():
    pygame.draw.rect(screen, black, (50,50,1400,700), 16)
    pygame.draw.line(screen, black, (285,50), (285,750), 16)
    pygame.draw.line(screen, black, (50,400), (285,400), 16)
    tube_point_list = []
    x = 360
    y = 160
    for i in range(6):
        pygame.draw.line(screen, black, (x,y), (x,y+470), 16)
        tube_point_list.append((x,y+110))
        tube_point_list.append((x,y+360))
        if i%2==1 and i<5:
            pygame.draw.line(screen, black, (x,y), (x+200,y), 16)
        elif i<5:
            pygame.draw.line(screen, black, (x,y+470), (x+200,y+470), 16)
        x+=200
    return tube_point_list

screen = pygame.display.set_mode((1500,800))
pygame.init()
while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 pygame.quit();
                 sys.exit()

    screen.fill(white)
    tube_point_list = draw_background()
    pygame.display.update()
