
import time
import threading

N = 5
class State:
    THINKING = 1
    HUNGRY = 2
    EATING = 3
philosopherloop = True
def philosopher(i, Lock, state, sem):
	while philosopherloop:
		time.sleep(5)
		with Lock :
			state[i] = State.HUNGRY
			if (state[(i + N - 1) % N] != State.EATING) and (state[(i + 1) % N] != State.EATING):
				# Si mes voisins de gauche et de droite ne mange pas, je mange
				state[i] = State.EATING
				sem[i].release()
		sem[i].acquire() # Attendre que mon voisin me débloque
		time.sleep(2) # Le philosopher mange
		with Lock :
			state[i] = State.THINKING
			# Si le voisin de gauche a faim et que son autre voisn ne mange pas
			if state[(i+N-1)%N] == State.HUNGRY and state[(i+N-2)%N] != State.EATING:
				state[(i+N-1)%N] = State.EATING	# Le faire manger
				sem[(i+N-1)%N].release() # Le debloquer
			# Si le voisin de droite a faim et que son autre voisn ne mange pas
			if state[(i+1)%N] == State.HUNGRY and state[(i+2)%N] != State.EATING:
				state[(i+1)%N] = State.EATING	# Le faire manger
				sem[(i+1)%N].release() # Le debloquer

if __name__ == "__main__":
	state = []
	sem = []
	Lock = threading.Lock()
	for i in range(N) : # Mettre tout les philos en penseur
		state.append(State.THINKING)
		sem.append(threading.Semaphore(0))
	threads = [threading.Thread(target=philosopher, args=(i, Lock, state, sem)) for i in range(N)]
	for thread in threads :
		thread.start()
	time.sleep(10)
	philosopherloop = False
	for thread in threads :
		thread.join()
	print("FIN")