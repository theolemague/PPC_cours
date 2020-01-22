import threading
from queue import Queue
import statistics
import sys
 
def worker(task_queue, data, data_ready, res_queue):
	data_ready.wait() 			# Wait for an event (if not the data will be empty)
	function = task_queue.get()	# Récupération des fonctions
	res = function(data)		# Récupération du resultats de chaque fonction
	res_queue.put([function.__name__, res])	# Valeur du résultat mise dans la queue de resultat avec le nom de la fonction

if __name__ == "__main__":
	data = []
	tasks = [min, max, statistics.median, statistics.mean, statistics.stdev]	# Fonction a effectuer
	
	task_queue = Queue()
	for task in tasks :
		task_queue.put(task)	# Queue contenant les fonctions voulues
	
	data_ready = threading.Event()
	res_queue = Queue()	# Queue des resultats

	# Creation d'un thread pour chaque fonction a effetuer
	threads = [threading.Thread(target=worker, args=(task_queue, data, data_ready, res_queue)) for i in range(len(tasks))]
	# Démarrer chaque thread
	for thread in threads:
		thread.start()
	

	# Make a list of float
	in_str = input("Entrez une séquence de nombre").split()
	for s in in_str:
		try : 
			data.append(float(s))
		except:
			print("Bad number", s)

	print(data)
	data_ready.set()	# Make an event to say that data is ready

	for thread in threads:
		thread.join()	# Wait for the finish of all thread
	
	while not res_queue.empty():
		print(res_queue.get())	# Print the result