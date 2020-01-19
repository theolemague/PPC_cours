import os
import sys
import time
import sysv_ipc
 
key = 666

try:
	mq = sysv_ipc.MessageQueue(key)
except ExistentialError:
	print("Cannot connect to message queue", key, ", terminating.")
	sys.exit(1)
t = getRequest()
if t == 1:
	pid = os.getpid()
	m = str(pid).encode()
	mq.send(m, type = 1)
	m, t = mq.receive(type = (pid + 3))
	dt = m.decode()
	print("Server response:", dt)
if t == 2:
	m = b""
	mq.send(m, type = 2)