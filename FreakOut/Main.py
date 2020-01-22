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
TIME_MAX = 10

def createMQ(key):
	try : 
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)			
	except sysv_ipc.ExistentialError:
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		mq.remove()
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	return mq

def finish(m):
	if developMode : 
		if m != "" :
			print("Fini ! le joueur", m,"a gagné")
		else :
			print("Aucun joueur n'a gagné")
		print("Appuyer sur escape pour quitter")
	else :
		vmq.send(m.encode(), type = 5)

def display(id,hand) :
	if developMode : 
		print(hand)
	else : 
		m = id
		for key, card in hand.items():
			m += ":"+key+"-"+card
		vmq.send(m.encode(), type = 3)


def getInput(id1, id2, sem):
	global penalty
	gameQuit = False
	kb = kbhit.KBHit()
	
	# Wait the start
	sem.acquire()	
	
	# Initialize default player, timers, used keypacks and keypressed 
	sendTo = 1
	timer[id1-1] = threading.Timer(TIME_MAX, timeUp, args=str(id1))
	timer[id1-1].start()
	timer[id2-1] = threading.Timer(TIME_MAX, timeUp, args=str(id2)) 
	timer[id2-1].start()
	keyUsed1 = list(hand1)
	keyUsed2 = list(hand2)
	k = ""
	while not gameQuit:

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

			# Get the pressed key (in terminale or in UI)
			if developMode :	
				if kb.kbhit():
					c = kb.getch()
					if ord(c) == 27: # ESC
						gameQuit = True
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
					# Queue removed (='esc' pressed in View process)
					gameQuit = True
					break
			
			# if k is in one of key pack used
			if k in keyUsed1 :
				sendTo = id1
				timer[id1-1].cancel()
				break
			elif k in keyUsed2 :
				sendTo = id2
				timer[id2-1].cancel()
				break

		# If 'esc' pressed, remove all queue, cancel timer
		if  gameQuit :
			imq.remove()
			try :
				bmq.remove()
			except sysv_ipc.ExistentialError:
				pass
			timer[id1-1].cancel()
			timer[id2-1].cancel()
			break
		# Else send the pressed key
		else :
			imq.send(k.encode(), type = sendTo)
		
		# Wait the end of the player
		sem.release()
		time.sleep(0.2)
		sem.acquire()

		# If game done, empty the keypacks => only 'esc' is accept, cancel timer
		if gameDone :
			keyUsed1 = []
			keyUsed2 = []
			timer[id1-1].cancel()
			timer[id2-1].cancel()
		# Else udpate keypacks used and pressed key, restart timer
		else : 
			keyUsed1 = list(hand1)
			keyUsed2 = list(hand2)
			k = ""
			timer[sendTo-1]= threading.Timer(TIME_MAX, timeUp, args=str(sendTo))
			timer[sendTo-1].start()

	kb.set_normal_term()


def timeUp(id):
	global penalty
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


def Player(id, hand, keyPack, sem):
	global gameDone
	while True :
		# Display hand
		display(id, hand)

		# Receive pressed key from inter message queue
		try :
			m, t = imq.receive(type = int(id))
			m = m.decode()
		except sysv_ipc.ExistentialError:
			break
		
		# Lock the get input
		sem.acquire()
		
		# If penalty
		if m == "penalty":
			if developMode :
				print("Penalité joueur",id, "!")
			m = id+":penalty:"+str(len(hand))
		# Else (=card)
		else :
			card = hand[m]
			m = id+":"+card+":"+str(len(hand))
		
		# Send message and wait response from board message queue
		try : 
			bmq.send(m.encode(), type=3)
			mfb, t = bmq.receive(type = int(id) )	
		except sysv_ipc.ExistentialError : 
			sem.release()
			# Queue removed
			break
		except OSError : 
			sem.release()
			# Queue removed
			break
		
		mfb = mfb.decode()
		m = m.split(":")
		
		# If the card received is the same that the sent one, remove it from the hand
		if mfb==m[1]:
			removeFromHand(hand, keyPack, mfb)
			# Finished
			if len(hand) == 0:
				gameDone = True
				m = id+":gameDone"
				bmq.send(m.encode(), type = 3)
				display(id, hand)
				sem.release()
				break		
		# Else
		elif mfb != "": 
			addToHand(hand, keyPack, mfb)
		
		# Unlock the getInput
		sem.release()


if __name__ == "__main__" :
	# Develop mode = print game in the terminale
	developMode = False

	if len(sys.argv)>1:
		TIME_MAX = int(sys.argv[1])
		if len(sys.argv) == 3 :
			if sys.argv[2] == '-d':
				developMode = True

	# Board message queue (between main end board)
	bmq = createMQ(60)
	# View message queue (betwee Board, Main -> View)
	vmq = createMQ(40)

	# Start board process
	b = Process(target=Board.Board, args=(developMode,))
	b.start()
	
	# Start View process
	if not developMode :
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

		play1 = threading.Thread(target=Player, args=(id1, hand1, keyPack1, sem))
		play2 = threading.Thread(target=Player, args=(id2, hand2, keyPack2, sem))
		getKey = threading.Thread(target=getInput, args=( int(id1), int(id2), sem))
		play1.start()
		play2.start()	
		getKey.start()
		# Unlock the getKey Thread
		sem.release()

		try : 
			m, t = bmq.receive(type = 7)
			finish(m.decode())
			bmq.remove()
		except sysv_ipc.ExistentialError:
			pass
			
		# Stop all the player


		# Stop all thread
		getKey.join()
		play1.join()
		play2.join()
		
		b.join()
		if not developMode:
			v.join()
