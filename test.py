import pygame
from pygame.locals import *
import time
import threading

def add1():
	i = 0
	while True :
		i+=1
		print("dispial")
		display(str(i))
		time.sleep(1)


def display(str):
    text = font.render(str, True, (255, 255, 255), (159, 182, 205))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery

    screen.blit(text, textRect)
    pygame.display.update()

pygame.init()
screen = pygame.display.set_mode( (640,480) )
pygame.display.set_caption('Python numbers')
screen.fill((159, 182, 205))

font = pygame.font.Font(None, 17)

num = 0
done = False
t = threading.Thread(target=add1)
t.start()
while not done:


    pygame.event.pump()
    keys = pygame.key.get_pressed()
    if keys[K_ESCAPE]:
        done = True
t.join()