from multiprocessing import Process, Array, Manager

# Soltution avec Array
def fArray(number, mem):
    mem[0] = 0
    a, b = 0, 1
    i = 0
    while i < number :
        a, b = b, a+b
        mem[i+1] = a
        i +=1
    if i+1 < MEMORY_SIZE:
        mem[i+1] = -1  #stop flag
        
# Solution avec Manager
def fManager(n, lst):
    lst.append(0)
    a,b = 0,1
    i=0
    while i < n :
        a, b = b, a+b
        lst.append(a)
        i += 1

MEMORY_SIZE = 100

if __name__ == "__main__":
	index = 5
	shared_memory = Array('l', MEMORY_SIZE)
	p = Process(target=fArray, args=(index, shared_memory))

	#Solution avec manager
	with Manager() as manager:
		lst = manager.list()
	p = Process(target=fManager, args=(index, lst))

	p.start()
	p.join()

	#Solution Array
	for x in shared_memory[:]:
		if x == -1:
			break
		print(x, end=" ")

	#Solution Manager
	print(lst)   


