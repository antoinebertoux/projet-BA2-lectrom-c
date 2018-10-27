import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location




pygame.init()

BackGround = Background('background.png', [0,0])

display_width = 1439
display_height = 733

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('car.png').convert()


x =  (display_width * 0.5)
y = (display_height * 0.5)
x_change = 0
y_change = 0
car_speed = 0
angle_change = 0
angle = 0

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = -5
            elif event.key == pygame.K_RIGHT:
                x_change = 5
            elif event.key == pygame.K_UP:
                y_change = -5
            elif event.key == pygame.K_DOWN:
                y_change = 5
            elif event.key == pygame.K_a:
                angle_change = 1
            elif event.key == pygame.K_z:
                angle_change = -1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT :
                x_change = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                y_change = 0
            elif event.key == pygame.K_a or event.key == pygame.K_z:
                angle_change = 0

    x += x_change
    y += y_change

    angle += angle_change
    angle = angle%360

    # gameDisplay.fill(white)
    # gameDisplay.fill(black)
    gameDisplay.blit(BackGround.image, BackGround.rect)
    #car(x,y)


    rotCarImg = pygame.transform.rotate(carImg, angle)
    # screen.fill([255, 255, 255])

    corrected_x = x + carImg.get_rect()[2] - rotCarImg.get_rect()[2]/2
    corrected_y = y + carImg.get_rect()[3] - rotCarImg.get_rect()[3]/2

    # gameDisplay.blit(rotCarImg, (x,y))




    gameDisplay.blit(rotCarImg, (corrected_x,corrected_y))



    # print(rotCarImg.get_rect())
    # print(carImg.get_rect())

    pygame.display.update()
    clock.tick(600)

pygame.quit()
quit()
