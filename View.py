import pygame
from pygame.locals import *
import sysv_ipc

def display(m):
	id = m.pop(0)
	print(id)
	if int(id) == 1 :
		for i in range(0, len(m), 2):	
			text = font.render(m[i+1], True, (255, 255, 255), (159, 182, 205))
			textRect = text.get_rect()
			textRect.centerx = 100 + i*30 
			textRect.centery = 100
			screen.blit(text, textRect)
	if int(id) == 2 :
		for i in range(0, len(m), 2):	
			text = font.render(m[i+1], True, (255, 255, 255), (159, 182, 205))
			textRect = text.get_rect()
			textRect.centerx = 100 + i*30 
			textRect.centery = 380
			screen.blit(text, textRect)
	if int(id) == 3 :
		text = font.render(m[0], True, (255, 255, 255), (159, 182, 205))
		textRect = text.get_rect()
		textRect.centerx = 320 
		textRect.centery = 240
		screen.blit(text, textRect)
			
	pygame.display.update()

pygame.init()
screen = pygame.display.set_mode( (640,480) )
pygame.display.set_caption('Python numbers')
screen.fill((159, 182, 205))

font = pygame.font.Font(None, 17)

m = "test"
done = False

def getKey(event):
	if event.key == pygame.K_a:
		return "a"
	if event.key == pygame.K_z:
		return "z"
	if event.key == pygame.K_e:
		return "e"
	if event.key == pygame.K_r:
		return "r"
	if event.key == pygame.K_t:
		return "t"
	if event.key == pygame.K_y:
		return "y"
	if event.key == pygame.K_u:
		return "u"
	if event.key == pygame.K_i:
		return "i"
	if event.key == pygame.K_o:
		return "o"
	if event.key == pygame.K_p:
		return "p"

	if event.key == pygame.K_m:
		return "m"
	if event.key == pygame.K_l:
		return "l"
	if event.key == pygame.K_k:
		return "k"
	if event.key == pygame.K_j:
		return "j"
	if event.key == pygame.K_h:
		return "h"
	if event.key == pygame.K_g:
		return "g"
	if event.key == pygame.K_f:
		return "f"
	if event.key == pygame.K_d:
		return "d"
	if event.key == pygame.K_s:
		return "s"
	if event.key == pygame.K_q:
		return "q"
	return "none"


m = ""
vmq = sysv_ipc.MessageQueue(40)
while not done:
	events = pygame.event.get()
	for event in events:	
		if event.type == pygame.KEYDOWN:
			k = getKey(event)
			if k!="none":
				vmq.send(k.encode(), type = 1)
	try:
		m, t = vmq.receive(block = False, type = 3)
		print(screen.get_rect().centerx)
    
		print(m)
		m = m.decode().split(":")
		display(m)
	except sysv_ipc.BusyError :
		pass