import signal
import os
import time
from multiprocessing import Process

# Methode appelée lorsqu'on recoit un signal SIGUSR1
def handler(sig, frame):
	print("Die son")
	# Emettre le signal SIGKILL qui tue le process passé en pid
	os.kill(childPID, signal.SIGKILL)

def child():
	# Dire d'executer handler quand SIGUSR1 est emis
	signal.signal(signal.SIGUSR1, handler)
	while True:
		print("Hey !")
		time.sleep(1)

childPID=0

if __name__=="__main__":
	p = Process(target=child, args=())
	p.start()
	childPID = p.pid
	time.sleep(5)
	os.kill(childPID, signal.SIGUSR1) # Emettre SIGUSR1
	p.join()