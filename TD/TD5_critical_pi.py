# prefere un with plutot qu'un lock.aquire() / lock.release() car il permet de relacher le mutex s'il y a une couille 
import sys
import threading
import random
import multiprocessing

inpoint = 0

def countpi(n, lock):
	i  = n
	global inpoint
	while i :
		x = -1 + 2*random.random()
		y = -1 + 2*random.random()
		if x**2 + y**2 < 1 : 
			with lock:
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
	
	# Max of thread 
	# inpoint = multiprocessing.value('d', 0.0)
	
	#MAX_COUNTER = 10
	lock = threading.Lock()
	threadList = []
	NB_THREAD = 10
	for i in range(NB_THREAD):
		threadList.append(threading.Thread(target=countpi, args=(n,lock)))

	# for i in range(NB_PROCESS):
	#	ProcessList.append(multiprocessing.Process(target=countpi, args=(n,lock)))
	
	for thread in threadList :
		thread.start()
	# for Process in ProcessList :
	# 	proces.start()
	
	for thread in threadList :
		thread.join()
	# for Process in ProcessList :
	# 	proces.join()
		
	print("Estimation of pi :", round((4*(float(inpoint)/float(n*NB_THREAD))), 5))

	print("Ending thread:", threading.current_thread().name)                