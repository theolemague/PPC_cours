import sys
import array
import threading

BUFFER_SIZE = 5
def producer(n, buffer, full, empty, lock): # Ecrivain
	i = p = 0
	a,b = 0,1
	while i <n+1:
		a,b = b, a+b
		if i == n: # Definir la fin
			a = -1
		empty.acquire() # Prendre un semaphore
		with lock:
			print(a)
			buffer[p]= a
			p = (p+1)%BUFFER_SIZE
			i += 1
		full.release() # Debloquer le lecteur
		
def consumer(buffer, full, empty, lock): # Lecteur
	q = 0
	while True:
		full.acquire()# Attendre qu'un producer envoie un semaphore
		with lock:
			res = buffer[q]
			print("consumer :",res) # lecture
			q = (q+1)%BUFFER_SIZE
		empty.release()	# Envoyer un semaphore
		if res == -1: # Fin
			break

if __name__ == "__main__":
	n = 10
	buffer = array.array('l', range(BUFFER_SIZE))
	lock = threading.Lock()
	full = threading.Semaphore(0)
	empty = threading.Semaphore(BUFFER_SIZE)
	prod = threading.Thread(target = producer, args = (n, buffer, full, empty, lock))
	cons = threading.Thread(target = consumer, args = (buffer, full, empty, lock))	
	cons.start()
	prod.start()
	cons.join()
	prod.join()
  