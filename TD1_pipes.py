#!/usr/bin/env python3
import signal
import os
import time
import sys
from multiprocessing import Process, Pipe

def child(conn, sentence):
    # [::-1] -> inverser la phrase
    conn.send(sentence[::-1])
    conn.close()

if __name__=="__main__":
    # Creer un pipe
    conn_par, conn_child = Pipe()
    print("Entrez une phrase")
    sentence = input()
    p = Process(target=child, args=(conn_child,sentence))
    p.start()
    # Receive cote parent
    reversed_sent = conn_par.recv()
    print(reversed_sent)
    p.join()
    conn_par.close()