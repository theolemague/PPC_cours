from multiprocessing import Process, Manager
import threading
import sysv_ipc
import sys
import random
import time
import kbhit
import View
import Board

# Global variablr
penalty = [0,0]
gameDone = False
timer = [0, 0]
TIME_MAX = 5

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


def getInput(id1, id2, sem):
	global penalty
	gameQuit = False
	# Get the useable keys
	
	kb = kbhit.KBHit()
	
	# Wait the start
	sem.acquire()	
	
	sendTo = 1
	timer[id1-1] = threading.Timer(TIME_MAX, timeUp, args=str(id1))
	timer[id1-1].start()
	timer[id2-1] = threading.Timer(TIME_MAX, timeUp, args=str(id2)) 
	timer[id2-1].start()
	while not gameQuit:

		k = ""
		keyUsed1 = list(hand1)
		keyUsed2 = list(hand2)

		while True :
			if penalty[id1-1] == 1 :
				# If penality, wait end of the penality and update hand
				penalty[id1-1] = 0
				k = "penalty"
				sendTo = id1
				break
			if penalty[id2-1] == 1 :
				# If penality, wait end of the penality and update hand
				penalty[id2-1] = 0
				k = "penalty"
				sendTo = id2
				break

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
					m , t = vmq.receive(block= False, type = 1)
					k = m.decode()
				except sysv_ipc.BusyError:
					pass
				except sysv_ipc.ExistentialError :
					gameQuit = True
					bmq.remove()
					break
			
			if k in keyUsed1 :
				sendTo = id1
				timer[id1-1].cancel()
				break

			elif k in keyUsed2 :
				sendTo = id2
				timer[id2-1].cancel()
				break
	
		# Send the message		
		if not gameQuit :
			try :
				imq.send(k.encode(), type = sendTo)
				# Let the player take the semaphore
			except :
				pass
		else :
			timer[id1-1].cancel()
			timer[id2-1].cancel()
			break
		# Wait reponse of board
		sem.release()
		time.sleep(0.2)
		sem.acquire()
		# Restart the timer if game not ended
		if not gameDone:
			timer[sendTo-1]= threading.Timer(TIME_MAX, timeUp, args=str(sendTo))
			timer[sendTo-1].start()
	

	kb.set_normal_term()

def timeUp(id):
	penalty[int(id)-1] = 1 


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
		print(m)
		# Lock the get input
		sem.acquire()
		print("playe", id, "je prend")
		
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
		print("playe", id, "je lache")


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
		gameDone = True

		# Stop all thread
		getKey.join()
		play1.join()
		play2.join()

		# Remove queue
		b.join()
		if not terminaleMode:
			v.join()
