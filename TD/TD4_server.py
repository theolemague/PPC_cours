import sysv_ipc
import time
import sys
import concurrent.futures
 
key = 666

def worker(mq, m) :
	dt = time.asctime()
	msg = str(dt).encode()
	pid = int(m.decode())
	t = pid + 3
	mq.send(msg, type=t)

if __name__=="__main__":	
	try :
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	except ExistentialError:
		sys.exit(1)
	
	print("Starting the server")

	threads=[]
	with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor : 	
		while True :
			m, t = mq.receive()
			if t == 1:
				executor.submit(worker, mq, m)
			if t == 2:
				mq.remove()
				break
	print("Terminating time server")


	"""
def worker(mq, m) :
	dt = time.asctime()
	msg = str(dt).encode()
	pid = int(m.decode())
	t = pid + 3
	mq.send(msg, type=t)

if __name__=="__main__":	
	try :
		mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
	except ExistentialError:
		sys.exit(1)
	
	print("Starting the server")

	Threads=[]
	while True :
		m, t = mq.receive()
		if t == 1:
			p = threading.Thread(target = worker, args=(mq, m))
			p.start()
			threads.append(p)
		if t == 2
			for thread in threads : 
				thread.join()
			mq.remove()
			break
	print("Terminating time server")
	"""
