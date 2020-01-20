from multiprocessing import Process, Manager, Array
import threading
import queue
import sysv_ipc
import sys
import random
import time
import kbhit
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
penalty = False
gameDone = False

def getInput(hand, sem):
	global penalty
	# Get the useable keys
	
	kb = kbhit.KBHit()
	
	while not gameDone :
		# Wait that the player release the semaphore
		sem.acquire()	
		keyUsed = list(hand)
		
		timer = threading.Timer(200, timeUp) # Start a timer of 10s
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
			if penalty :
				break

			if gameDone :
				timer.cancel()
				break
		
		# Send the message
		if penalty :
			penalty = False
			imq.send(b"", type = 2)
			sem.release()
			time.sleep(0.2) # Let the player take the semaphore
		elif not gameDone :		
			msg = str(hand[str(c)])
			imq.send(msg.encode(), type = 1)
			sem.release()
			time.sleep(0.2)	# Let the player take the semaphore
	
	kb.set_normal_term()

def timeUp():
	global penalty
	penalty = True


def removeFromHand(hand, card):
	# Get all key used
	keyL = list(hand)		
	# Remove the last one used
	keyPack.append(keyL.pop(len(keyL)-1))
	cardL = []
	for search_card in hand.values() : 
		if str(card) != str(search_card) : 
			cardL.append(search_card)

	hand.clear()
	for i in range(len(keyL)):
		hand[keyL[i]]=cardL[i] # Make the hand, conserving the ordre of the key (a, z, e, r...)


def addToHand(hand, card):
	try :
		global keyPack
		hand[keyPack.pop(0)] = card
	except IndexError : 
		pass

def Play(id, hand, sem):
		display(hand)

		# Unlock the getInput thread
		sem.release()

		while True :
			try : 
				m , t = imq.receive()	# Receive the key pressed by the player
			except sysv_ipc.ExistentialError : # Queue removed
				break
			# Lock the get input
			sem.acquire()		
	
			if t == 2 : 
				# If penalty
				m = id+":penalty:"+str(len(hand))
				print("Penalité !")
				bmq.send(m.encode(), type=3)
			else :
				# Else (=card)
				m = id+":"+m.decode()+":"+str(len(hand))
				bmq.send(m.encode(), type=3)
			
			try : 
				mfb, t = bmq.receive(type = int(id) )	# Respond of the board
			except sysv_ipc.ExistentialError : # Queue removed
				break
			
			mfb = mfb.decode()
			
			m = m.split(":")
			if mfb==m[1]:
				# If the card received is the same that the sent one, remove it from the hand
				removeFromHand(hand, mfb)
				if len(hand) == 0:
					sem.release()
					break		# Hand empty
			elif mfb != "faux": 
				# Else
				addToHand(hand, mfb)
			# Display the new hand
			display(hand)
			# Unlock the getInput
			sem.release()


if __name__ == "__main__" :

	bmq = sysv_ipc.MessageQueue(60)
	# Receive the player id and the key autoryze to the player
	m, t = bmq.receive(type = 10)
	keyPack = m.decode().split(":")
	id = keyPack.pop(0)

	# Receive the card
	m, t = bmq.receive(type = 9)
	cards = m.decode().split(":")
	# Sem to block input to start
	sem = threading.Semaphore(0)

	# Create inter process message queue	
	imq = createMQ(int(id))		

	with Manager() as manager:
		# hand of the player dict = {key : card,...}
		hand = manager.dict()
		for card in cards:
			hand[keyPack.pop(0)] = card

		play = threading.Thread(target=Play, args=(id, hand, sem))
		getKey = threading.Thread(target=getInput, args=(hand,sem))
	
		play.start()
		getKey.start()
		m , t = bmq.receive(type = 7)
		gameDone = True
		imq.remove()
		play.join()
		getKey.join()

		if m.decode() == id :
			bmq.remove()
