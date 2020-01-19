import time
import random
import multiprocessing
 
def is_prime(n):
	print(multiprocessing.current_process().name)
	if n <=3 :
		return n >=1 # True if n == 2|3, False if n == 1\0
	elif (n%2 == 0) or (n%3 == 0) : 
		return False
	i = 5
	while (i*i<n):
		if (n%i == 0) or (n%(i+2)==0):
			return False
		i += 6
	return True

	
if __name__ == "__main__":
	numbers = [random.randint(1000, 1000000) for i in range(10)]
	print("Test with numbers :", numbers)
	with multiprocessing.Pool(processes = 4) as pool:

		start = time.time()
		print("*** Synchronous map")
		for x in pool.map(is_prime, numbers):
			print(x)
		end = time.time()
		print("Executing time :", end-start)

		start = time.time()
		print("\n*** Asynchronous map")
		for x in pool.map_async(is_prime, numbers).get():
			print(x)	
		end = time.time()
		print("Executing time :", end-start)

		start = time.time()
		print("\n*** Lazy map")
		for x in pool.imap(is_prime, numbers):
			print(x)
		end = time.time()
		print("Executing time :", end-start)

		start = time.time()
		print("\n*** Asynchronous call in one process")
		results = [pool.apply_async(is_prime, (n,)) for n in numbers]
		for r in results:
			print(r)
		end = time.time()
		print("Executing time :", end-start)
