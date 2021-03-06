import sysv_ipc
import random

class Carte:
	def __init__(self, couleur, nb):
		self.couleur = couleur
		self.nb = nb
	def __str__(self):
		return self.couleur+" "+str(self.nb)


def Board(developMode):
	global bmq
	global vmq
	global stack
	global pile
	bmq = sysv_ipc.MessageQueue(60)
	vmq = sysv_ipc.MessageQueue(40)
	stack = []
	pile = []

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
	def checkCard(cardstr):
		st = stack[len(stack)-1] 
		cardstr = cardstr.split(" ")
		card = Carte(cardstr[0], int(cardstr[1]))
		if card.couleur == st.couleur :
			if abs(card.nb - st.nb)==1 or abs(card.nb - st.nb)==9:
				return True
			else : return False
		else :
			if card.nb == st.nb :
				return True
			else : return False 

	def displayBoard(developMode):
		card = stack[len(stack)-1]
		if developMode :
			print(card)
		else : 
			m = "3:"+str(card)+":"+str(len(pile))
			vmq.send(m.encode(), type = 3)


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
	
	while True : 
		displayBoard(developMode)
		# Waiting for a player message
		try : 
			m, t = bmq.receive(type = 3)
		except sysv_ipc.ExistentialError :
			break
		m = m.decode().split(":")

		# If a player has finished
		if m[1] == "gameDone":
			bmq.send(m[0].encode(), type=7)
			break
		
		# If a player has a penality
		elif m[1] == "penalty" : 
			# If the limit of card is not reached, send a card
			if int(m[2]) < 10:
				card = str(pile.pop(random.randint(0,len(pile)-1)))
			# If it is, send nothing
			else :
				card = ""
			bmq.send(card.encode(), type = int(m[0]))

			# If pile
			if len(pile)==0:
				empty =""
				bmq.send(empty.encode(), type = 7)		
				break

		# Else => a player play a card 
		else :
			# If the card is valid, send the same card
			if checkCard(m[1]) :
				card = m[1].split(" ")
				bmq.send(m[1].encode(), type = int(m[0]))
				stack.append(Carte(card[0], int(card[1])))

			else :
				# If the limit of card is not reached, send a card
				if int(m[2]) < 10:
					card = str(pile.pop(random.randint(0,len(pile)-1)))
				# If it is, send nothing
				else :
					card = ""
				bmq.send(card.encode(), type = int(m[0]))
				
				# If pile is empty
				if len(pile)==0:
					empty =""
					bmq.send(empty.encode(), type = 7)		
					break

				


