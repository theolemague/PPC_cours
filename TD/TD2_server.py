import sysv_ipc
import time
import sys
 
key = 128

try :
	mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
except ExistentialError:
	sys.exit(1)

print("Starting the server")

while True:
	# Receive message from client
	mp, t = mq.receive()
	if int(t) == 2 :
		break
	if int(t) == 1 : 
		mq.send(time.asctime(), type = 3)
mq.remove()