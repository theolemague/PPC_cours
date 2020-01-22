import sys
import threading
import random

inpoint = 0

def countpi(n):
	i  = n
	global inpoint
	while i :
		x = -1 + 2*random.random()
		y = -1 + 2*random.random()
		if x**2 + y**2 < 1 : 
			inpoint += 1
		i -= 1


if __name__ == "__main__":
	try :
		n = int(input("Entrez un nombre\n"))
	except :
		print("Probleme gros con")
		exit(1)
	
	if n < 0:
		print("T'as mis un nombre negatif gros con")
		exit(2)
	
	threadpi = threading.Thread(target=countpi, args=(n,))
	threadpi.start()
	threadpi.join()
	print("Estimation of pi :", round((4*(float(inpoint)/float(n))), 5))

	print("Ending thread:", threading.current_thread().name)                