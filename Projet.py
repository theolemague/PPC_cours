from multiprocessing import Process, Manager, Array
import threading
import queue
import sysv_ipc
import sys
import random
import time
import os
import signal

def createMQ(key):
	try : 
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
			
	except sysv_ipc.ExistentialError:
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		mq.remove()
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	return mq

class Carte:
	def __init__(self, couleur, nb):
		self.couleur = couleur
		self.nb = nb
	def __str__(self):
		return self.couleur+" "+str(self.nb)

"""
Board message queue : 
1 - Player propose a card to board => playerID : card : lastCardFlag (if the message is for penalty, card = 'penalty')
2 - Board give a card to player => playerID : card (if the card is the same that the sent one -> card accept)
4 - Initialization player 1
5 - Initialization player 2
6 - Endgame
"""
# Function that check the validity of the card played
def checkCard(cardstr, stack):
	cardstr = cardstr.split(" ")
	card = Carte(cardstr[0], int(cardstr[1]))
	if card.couleur == stack.couleur :
		if abs(card.nb - stack.nb) == 1 :
			return True
		else : return False
	else :
		if card.nb == stack.nb :
			return True
		else : return False 


if __name__ == '__main__':
	stack = []
	pile = []

	
	for i in range(1,11):
		pile.append(Carte("Rouge", i))
		pile.append(Carte("Bleu", i))
	
	randint = random.randint(0, (len(pile)-1))
	stack.append(pile.pop(randint))
	
	keyBMQ = 60
	bmq = createMQ(keyBMQ)


	msghand1 = "1"
	msghand2 = "2"
	for i in range(5):
		# Prepare the hand for the players
		msghand1 += ":"+str(pile.pop(random.randint(0, (len(pile)-1))))
		msghand2 += ":"+str(pile.pop(random.randint(0, (len(pile)-1))))	
	
	bmq.send(msghand2.encode(), type = 5)
	bmq.send(msghand1.encode(), type = 4)

	pid, t = bmq.receive(type = 10)
	pid = int(pid.decode())
	
	playerWon = 0
	while True : 
		print("Stack :", stack[len(stack)-1])
		
		m, t = bmq.receive(type = 1)					# Waiting for a player message
		m = m.decode().split(":")

		print("Board : j'ai recu ", m[1])
		
		if m[1] == "penalty" : 
			msg = m[0]+":"+str(pile.pop(random.randint(0,len(pile)-1)))
			print("Board : penalite, j'envoie", msg)
			if m[2] != str(10):
				bmq.send(msg.encode(), type = 2)				# send a random card to the player
			if len(pile)==0:			
				break	
		else :
			if checkCard(m[1], stack[len(stack)-1]) :	# Check the card
				if m[2]== "1": 							# if is the last card
					playerWon = m[0]					# end game (winner is m[0])
					break
				else : 
					msg = m[0]+":"+m[1]
					print("Board : carte bonne, j'envoie", msg)
					bmq.send(msg.encode(), type = 2)			# send the card received, message type 3
					m = m[1].split(" ")
					stack.append(Carte(m[0], int(m[1])))
			else :										# If the card is wrong
				if len(pile)==0:						
					break								# Pile empty 
				else :
					print(m[2])
					if m[2] == str(10) :
						msg = m[0]+":faux"
						bmq.send(msg.encode(), type = 2)
					else : 
						msg = m[0]+":"+str(pile.pop(random.randint(0,len(pile)-1)))
						print("Board : carte pas bonne, j'envoie", msg)
						bmq.send(msg.encode(), type = 2)				# send a random card to the player

	if playerWon !=0:
		print("Le joueur", playerWon, "a gagné")
	else :
		print("Partie finie, aucun joueur n'a gagné")
	
	os.kill(pid, signal.SIGKILL)

	bmq.remove()
