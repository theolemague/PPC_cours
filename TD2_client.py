import sysv_ipc
import sys
 
key = 128

def user():
	answer = 0
	while answer not in [1, 2, 3]:
		print("1. to get current date/time")
		print("2. to terminate time server")
		print("3. quit")
		answer = int(input())
	return answer

try:
	mq = sysv_ipc.MessageQueue(key)
except ExistentialError:
	print("Cannot connect to message queue", key, ", terminating.")
	sys.exit(1)

while True:
	request = user()
	if request == 1:
		m = b"" # Type Byte
		mq.send(m, type=1)
		m, t = mq.receive(type = 3)
		print("Server response: ", m.decode())
	if request == 2:
		m= b""
		mq.send(m, type = 2)
	if request == 3:
		break
mq.remove() # ne pas oublier 