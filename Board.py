from multiprocessing import Process, Manager, Array
import threading
import queue
import sysv_ipc
import sys
import random
import time
import os
import signal

class Carte:
	def __init__(self, couleur, nb):
		self.couleur = couleur
		self.nb = nb
	def __str__(self):
		return self.couleur+" "+str(self.nb)

"""
Board message queue : 
1 - To player 1
2 - To player 2
3 - From Player
7 - Endgame
9 - Send 5 card
10 - Send key autoryze
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

def displayBoard(card, vmq, terminaleMode):
	if terminaleMode :
		print(card)
	else : 
		m = "3:"+str(card)
		vmq.send(m.encode(), type = 3)


def Board(terminaleMode):
	bmq = sysv_ipc.MessageQueue(60)
	vmq = sysv_ipc.MessageQueue(40)
	
	stack = []
	pile = []

	for i in range(1,11):
		pile.append(Carte("Rouge", i))
		pile.append(Carte("Bleu", i))
	
	randint = random.randint(0, (len(pile)-1))
	stack.append(pile.pop(randint))

	# Send the key autorise for each player
	keyPackP1 = "1:a:z:e:r:t:y:u:i:o:p"	# Pack off the key used by player 1
	keyPackP2 = "2:m:l:k:j:h:g:f:d:s:q"	# Pack off the key used by player 2
	bmq.send(keyPackP1.encode(), type = 10)
	bmq.send(keyPackP2.encode(), type = 10)

	# Send the hand of each player
	msghand1 = str(pile.pop(random.randint(0, (len(pile)-1))))
	msghand2 = str(pile.pop(random.randint(0, (len(pile)-1))))

	for i in range(4):
		msghand1 += ":"+str(pile.pop(random.randint(0, (len(pile)-1))))
		msghand2 += ":"+str(pile.pop(random.randint(0, (len(pile)-1))))	
	bmq.send(msghand1.encode(), type = 9)
	bmq.send(msghand2.encode(), type = 9)
	
	displayBoard(stack[len(stack)-1], vmq, terminaleMode)
	while True : 
		# Waiting for a player message
		try : 
			m, t = bmq.receive(type = 3)
		except sysv_ipc.ExistentialError :
			break
		m = m.decode().split(":")

		if m[1] == "gameDone":
			# If a player has finished
			bmq.send(m[0].encode(), type=7)
			break

		
		if m[1] == "penalty" : 
			#If it is a penality
			if m[2] != str(10):
				# If the limit of card is not reached
				card = str(pile.pop(random.randint(0,len(pile)-1)))
				bmq.send(card.encode(), type = int(m[0]))
			else :
				card = ""
				bmq.send(card.encode(), type = int(m[0]))
			if len(pile)==0:
				empty =""
				bmq.send(empty.encode(), type = int(m[0]))
				bmq.send(empty.encode(), type = 7)		
				break	
		else :
			if checkCard(m[1], stack[len(stack)-1]) :
				# If the card is valid
				bmq.send(m[1].encode(), type = int(m[0]))
				card = m[1].split(" ")
				stack.append(Carte(card[0], int(card[1])))
				displayBoard(stack[len(stack)-1], vmq, terminaleMode)
			else :
				if len(pile)==0:				
					empty = ""
					bmq.send(empty.encode(), type = int(m[0]))
					bmq.send(empty.encode(), type = 7)
					break	# Pile empty 
				else: 
					# If the card is wrong
					if m[2] == str(10) :
						# If the limit of card is reached
						msg = ""
						bmq.send(msg.encode(), type = int(m[0]))
					else : 
						# Else, send a new card
						card = str(pile.pop(random.randint(0,len(pile)-1)))
						bmq.send(card.encode(), type = int(m[0]))



