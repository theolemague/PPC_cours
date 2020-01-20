from multiprocessing import Process, Manager, Array
import threading
import queue
import sysv_ipc
import sys
import random
import time
import kbhit
import os
import View
import Board


endgame = False

def createMQ(key):
	try : 
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)			
	except sysv_ipc.ExistentialError:
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		mq.remove()
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	return mq

def finish(m):
	if terminaleMode : 
		if m != "" :
			print("Fini ! le joueur", m,"a gagné")
		else :
			print("Aucun joueur n'a gagné")
		print("Appuyer sur escape pour quitter")
	else :
		vmq.send(m.encode(), type = 5)

def display(id,hand) :
	if terminaleMode : 
		print(hand)
	else : 
		m = id
		for key, card in hand.items():
			m += ":"+key+"-"+card
		vmq.send(m.encode(), type = 3)

penalty = [0,0]

timer = [0, 0]
TIME_MAX = 5

def getInput(id1, id2, sem):
	global penalty
	gameQuit = False
	# Get the useable keys
	
	kb = kbhit.KBHit()
	
	timer[id2-1] = threading.Timer(TIME_MAX, timeUp, args=str(id2)) # Start a timer of 10s
	timer[id2-1].start()
	
	timer[id1-1] = threading.Timer(TIME_MAX, timeUp, args=str(id1)) # Start a timer of 10s
	timer[id1-1].start()
	
	while not gameQuit:
		# Wait that the player release the semaphore
		sendTo = 1
		sem.acquire()	
		k = ""
		keyUsed1 = list(hand1)
		keyUsed2 = list(hand2)
		while True :
			if terminaleMode : 
				if kb.kbhit():
					c = kb.getch()
					if ord(c) == 27: # ESC
						gameQuit = True
						bmq.remove()
						break
					else :
						k = str(c)
			else:
				try :
					m , t = vmq.receive(type = 1)
					k = m.decode()
				except sysv_ipc.ExistentialError :
					gameQuit = True
					bmq.remove()
					break
			if k in keyUsed1 :
				sendTo = id1
				timer[id1-1].cancel()
				timer[id1-1] = threading.Timer(TIME_MAX, timeUp, args=str(id1)) # Start a timer of 10s
				timer[id1-1].start()
				break
			if k in keyUsed2 :
				sendTo = id2
				timer[id2-1].cancel()
				timer[id2-1] = threading.Timer(TIME_MAX, timeUp, args=str(id2)) # Start a timer of 10s
				timer[id2-1].start()
				break
		
		# Send the message
		if penalty[sendTo-1] == 1 :
			# If penality, wait end of the penality
			sem.acquire()
			penalty[sendTo-1] = 0
			
		if not gameQuit :
			msg = str(k)
			try : 
				imq.send(msg.encode(), type = sendTo)
				# Let the player take the semaphore
			except :
				pass
			sem.release()
			time.sleep(0.2)
		else :
			timer[id1-1].cancel()
			timer[id2-1].cancel()
			break
	kb.set_normal_term()

def timeUp(id):
	id = int(id)
	penalty[int(id)-1] =1 
	m = "penalty"
	try :
		imq.send(m.encode(), type = int(id))
		timer[id-1] = threading.Timer(TIME_MAX, timeUp, args=str(id)) # Start a timer of 10s
		timer[id-1].start()
	except :
		pass
	sem.release()
	time.sleep(0.2) # Let the player take the semaphore


def removeFromHand(hand,keyPack, card):
	# Get all key used
	keys = list(hand)		
	cards = hand.values()
	# Remove the last one
	keys.pop()
	if card in cards : 
		cards.remove(card)
	
	hand.clear()
	for i in range(len(keys)):
		hand[keys[i]]=cards[i] # Make the hand, conserving the ordre of the key (a, z, e, r...)


def addToHand(hand, keyPack, card):
	try :
		hand[keyPack.pop(0)] = card
	except IndexError : 
		pass



def Play(id, hand, keyPack, sem):
	display(id, hand)

	while True :
		try :
			m, t = imq.receive(type = int(id))
			m = m.decode()
		except sysv_ipc.ExistentialError:
			break
		
		# Lock the get input
		sem.acquire()
		
		if m == "penalty": 
			# If penalty
			if terminaleMode :
				print("Penalité joueur",id, "!")
			m = id+":penalty:"+str(len(hand))
			bmq.send(m.encode(), type=3)
		else :
			# Else (=card)
			card = hand[m]
			m = id+":"+card+":"+str(len(hand))
			bmq.send(m.encode(), type=3)
		try : 
			mfb, t = bmq.receive(type = int(id) )	# Respond of the board
		except sysv_ipc.ExistentialError : # Queue removed
			break
		
		mfb = mfb.decode()
		m = m.split(":")
		if mfb==m[1]:
			# If the card received is the same that the sent one, remove it from the hand
			removeFromHand(hand, keyPack, mfb)
			if len(hand) == 0:
				# Finished
				m = id+":gameDone"
				bmq.send(m.encode(), type = 3)
				display(id, hand)
				sem.release()
				break		
		elif mfb != "": 
			# Else
			addToHand(hand, keyPack, mfb)
		# Display the new hand
		
		display(id, hand)
		# Unlock the getInput
		sem.release()


if __name__ == "__main__" :
	terminaleMode = False
	if len(sys.argv)>1:
		if sys.argv[1] == 'terminale':
			terminaleMode = True

	bmq = createMQ(60)
	vmq = createMQ(40)

	b = Process(target=Board.Board, args=(terminaleMode,))
	b.start()
	
	if not terminaleMode :
		v = Process(target=View.View)
		v.start()
	
	# Receive the player id and the key autoryze to the player
	m, t = bmq.receive(type = 10)
	keyPack1 = m.decode().split(":")
	id1 = keyPack1.pop(0)
	
	m, t = bmq.receive(type = 10)
	keyPack2 = m.decode().split(":")
	id2 = keyPack2.pop(0)
	
	# Receive the card
	m, t = bmq.receive(type = 9)
	cards1 = m.decode().split(":")
	m, t = bmq.receive(type = 9)
	cards2 = m.decode().split(":")

	# Sem to block input to start
	sem = threading.Semaphore(0)

	# Create inter process message queue	
	imq = createMQ(20)		

	with Manager() as manager:
		# hand of the player dict = {key : card,...}
		hand1 = manager.dict()
		for card in cards1:
			hand1[keyPack1.pop(0)] = card
		hand2 = manager.dict()
		for card in cards2:
			hand2[keyPack2.pop(0)] = card

		play1 = threading.Thread(target=Play, args=(id1, hand1, keyPack1, sem))
		play2 = threading.Thread(target=Play, args=(id2, hand2, keyPack2, sem))
		getKey = threading.Thread(target=getInput, args=( int(id1), int(id2), sem))
		play1.start()
		play2.start()	
		getKey.start()
		# Unlock the getKey Thread
		sem.release()

		try : 
			m, t = bmq.receive(type = 7)
			finish(m.decode())
		except sysv_ipc.ExistentialError:
			pass
			
		# Stop all the player
		imq.remove()

		# Stop all thread
		getKey.join()
		play1.join()
		play2.join()

		# Remove queue
		b.join()
		if not terminaleMode:
			v.join()
