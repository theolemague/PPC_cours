import pygame
from pygame.locals import *
import sysv_ipc


def View() : 
	def displayCard(m):
		id = m.pop(0)
		if int(id) == 1 :
			pygame.draw.rect(screen,BACKGROUND_COLOR,(60,20,880,160))
			nbcard = len(m)
			for i in range(nbcard):
				items = m[i].split('-')
				card = items[1].split(" ")
				carte = pygame.image.load("carte/"+card[0]+"_"+card[1]+".png").convert_alpha()
				perso_x = (500-nbcard*44) + i*88
				perso_y = 20
				screen.blit(carte, (perso_x, perso_y)) 
				key = font.render(items[0], True, (255, 255, 255))
				textRect = key.get_rect()
				textRect.centerx = (544-nbcard*44) + i*88 
				textRect.centery = 140
				screen.blit(key, textRect)	
		
		if int(id) == 3 :
			pygame.draw.rect(screen,BACKGROUND_COLOR,(456,220,554,160))
			card = m[0].split(" ")
			carte = pygame.image.load("carte/"+card[0]+"_"+card[1]+".png").convert_alpha()
			perso_x = 456
			perso_y = 220
			screen.blit(carte, (perso_x, perso_y)) 
			for i in range(int(m[1])):
				carte = pygame.image.load("carte/Dos.png").convert_alpha()
				perso_x = 700 + i*10
				perso_y = 220
				screen.blit(carte, (perso_x, perso_y)) 
		
		if int(id) == 2 :
			pygame.draw.rect(screen,BACKGROUND_COLOR,(60,420,880,160))
			nbcard = len(m)
			for i in range(nbcard):
				items = m[i].split('-')
				card = items[1].split(" ")
				carte = pygame.image.load("carte/"+card[0]+"_"+card[1]+".png").convert_alpha()
				perso_x = (500-nbcard*44) + i*88
				perso_y = 420
				screen.blit(carte, (perso_x, perso_y)) 
				key = font.render(items[0], True, (255, 255, 255))
				textRect = key.get_rect()
				textRect.centerx = (544-nbcard*44) + i*88
				textRect.centery = 560
				screen.blit(key, textRect)			
		pygame.display.update()

	def displayFinish(m):
		if m !="":
			text= "Le joueur "+m+" a gagné"
		else : 
			text= "Aucun jouer n'a gagné"
		pygame.draw.rect(screen,BACKGROUND_COLOR,(456,220,880,160))
		text = font.render(text, True, (255, 255, 255))
		textRect = text.get_rect()
		textRect.centerx = screen.get_rect().centerx
		textRect.centery = screen.get_rect().centery - 20
		screen.blit(text, textRect)

		text = font.render("Appuyer sur escape pour quitter", True, (255, 255, 255))
		textRect = text.get_rect()
		textRect.centerx = screen.get_rect().centerx
		textRect.centery = screen.get_rect().centery
		screen.blit(text, textRect)
		pygame.display.update()

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
		if event.key == pygame.K_ESCAPE:
			return "escape"
		return "none"


	pygame.init()
	screen = pygame.display.set_mode( (1000,600) )
	pygame.display.set_caption('Python numbers')
	BACKGROUND_COLOR = (159, 182, 205)
	screen.fill(BACKGROUND_COLOR)

	font = pygame.font.Font(None, 17)

	done = False
	m = ""
	vmq = sysv_ipc.MessageQueue(40)
	while not done:
		events = pygame.event.get()
		for event in events:	
			if event.type == pygame.KEYDOWN:
				k = getKey(event)
				if k == "escape":
					done = True
					break
				elif k!="none":
					vmq.send(k.encode(), type = 1)
			if event.type == QUIT :
				done = True
		try:
			m, t = vmq.receive(block = False, type = 3)
			if t == 3:
				m = m.decode().split(":")
				displayCard(m)
			m, t = vmq.receive(block = False, type = 5)
			if t == 5:
				displayFinish(m.decode()) 
		except sysv_ipc.BusyError :
			pass
	m = "end"
	vmq.remove()