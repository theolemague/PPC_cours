#!/usr/bin/env python3
# Cette phrase est pour definir que l'environnement est en python3 dans le cas ou
# le fichier est rendu executable

from multiprocessing import Process
import time

# Utilisation de Process :
#   1er methode : classe qui herite de Process
# dans ce cas c'est la methode run() qui est appelé lorsqu'on start()
# le process
'''
class f(Process):
    def __init__(self, number):
        super().__init__()  # Ne pas oublier
        self.number = number

    def run(self):
        chain = [0,1]
        a, b = 0, 1
        i = 0
        while i < self.number :
            a, b = b, a+b
            chain.append(b)
            i +=1
        print(chain)
        time.sleep(8)
'''
#   2eme methode : utiliser l'objet Process
# en target on precise la fonction visé comme process
def f(self):
        chain = [0,1]
        a, b = 0, 1
        i = 0
        while i < self.number :
            a, b = b, a+b
            chain.append(b)
            i +=1
        print(chain)
        

if __name__ == "__main__":
    index = 5
    # 1ere methode
    '''p = f(index)'''
    
    # 2eme methode
    p = Process(target=fArray, args=(index,))
    p.start()
    p.join()