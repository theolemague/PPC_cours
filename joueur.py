from multiprocessing import Process, Manager, Array
import threading
import queue
import sysv_ipc
import sys
import random
import time
import kbhit
from tkinter import *
import os

endgame = False

def createMQ(key):
	try : 
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
			
	except sysv_ipc.ExistentialError:
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		mq.remove()
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	return mq


def display(hand) :

	print(hand)


"""
Interne Message Queue type : 
1 card to played => card
2 time penalty => 
"""
penalty = 0

def getInput(ident, hand, semInput):
	global penalty
	imq = sysv_ipc.MessageQueue(ident)		# create inter process message queue 
	# Get the useable keys
	
	
	kb = kbhit.KBHit()
	
	while True :
		semInput.acquire()	# Wait that the player release the semaphore
		keyUsed = list(hand)
		
		timer = threading.Timer(100, timeUp, args=[ident]) # Start a timer of 10s
		timer.start()
		
		done = False
		while not done:
			if kb.kbhit():
				c = kb.getch()
			
				for key in keyUsed :
					if ord(c)==ord(key): # If c is a key useable, cancel the timer and quit the while loop
						timer.cancel()
						done = True
						break
			if penalty == ident :
				break
		
		# Send the message
		if penalty :
			penalty = 0
			imq.send(b"", type = 2)
			semInput.release()
			time.sleep(0.2) # Let the player take the semaphore
		else :		
			msg = str(hand[str(c)])
			imq.send(msg.encode(), type = 1)
			semInput.release()
			time.sleep(0.2)	# Let the player take the semaphore
	
	kb.set_normal_term()

def timeUp(ident):
	global penalty
	penalty = ident


def removeFromHand(hand, card):
	keyL = list(hand)		# Get all key used
	keyL.pop(len(keyL)-1)	# Remove the last one used
	cardL = []
	for search_card in hand.values() : 
		if str(card) != str(search_card) : 
			cardL.append(search_card)

	if len(keyL) == len(cardL):
		hand.clear()
		for i in range(len(keyL)):
			hand[keyL[i]]=cardL[i] # Make the hand, conserving the ordre of the key (a, z, e, r...)
	else : 
		pass
		# PROBLEM TODO

def addToHand(hand, card, keyPack):
	try :
		hand[keyPack.pop(0)] = card
	except IndexError : 
		pass

def Player(ident, keyPack, lock):
	with Manager() as manager:
		hand = manager.dict()			# Hand of the player
		
		semInput = threading.Semaphore(0)	# Sem to block input to start

		imq = createMQ(ident)		# create inter process message queue	
		bmq = sysv_ipc.MessageQueue(60) # open Board Message Queue

		m ,t = bmq.receive(type = (ident+3))
		md = m.decode().split(":")

		# Initialyze the 5 first cards
		for i in range(5):
			hand[keyPack.pop(0)] = md[i+1]	# Create the hand dict => {key : card, ...}

		threadcard = threading.Thread(target=getInput, args=(ident, hand, semInput))
		threadcard.start()
		
		display(hand)
		# Unlock the getInput thread
		semInput.release()

		while True :
			try : 
				m , t = imq.receive()	# Receive the key pressed by the player
			except sysv_ipc.ExistentialError : # Queue removed
				break
				
			semInput.acquire()		# Lock the get input
	
			with lock : # Lock the other player
				if t == 2 : # if this is a penalty
					m = str(ident)+":penalty:"+str(len(hand))
					print("Joueur",ident," : Penalité")
					bmq.send(m.encode(), type=1)	# penalty message
				else : 
					print(len(hand))
					m = str(ident)+":"+m.decode()+":"+str(len(hand))
					bmq.send(m.encode(), type = 1)
				
				try : 
					mfb, t = bmq.receive(type = 2 )	# Respond of the board
				except sysv_ipc.ExistentialError : # Queue removed
					break
				
				mfbd = mfb.decode().split(":")
				if mfbd[0] != str(ident):
					bmq.send(mfb, type = 1)	# If the message is not for the player, send it
				else : 			
					m = m.split(":")
					if str(mfbd[1])==str(m[1]):		# If the card received is the same that the sent one, remove it from the hand
						removeFromHand(hand, mfbd[1])
						if len(hand) == 0:
							break		# Hand empty
					elif str(mfbd[1] != "faux") : 
						addToHand(hand, mfbd[1], keyPack)
					display(hand)

			semInput.release()
		
		threadcard.join()

if __name__ == "__main__" :

	lock = threading.Lock()

	keyPackP1 = ['a','z','e','r','t','y','u','i','o','p']	# Pack off the key used by player 1
	keyPackP2 = ['m','l','k','j','h','g','f','d','s','q']	# Pack off the key used by player 2

	bmq = sysv_ipc.MessageQueue(60)
	m = str(os.getpid())
	bmq.send(m.encode(), type = 10)
	
	p1 = threading.Thread(target=Player, args=(1, keyPackP1, lock))
	p2 = threading.Thread(target=Player, args=(2, keyPackP2, lock))
	p1.start()
	p2.start()

	p1.join()
	p2.join()

