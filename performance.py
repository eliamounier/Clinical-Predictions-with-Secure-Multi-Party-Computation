import time
import random
import numpy as np
import matplotlib.pyplot as plt

from multiprocessing import Process, Queue

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty


NumParties = [2, 5,10,100,200,500,1000,2000,5000]
numaddition = [10,100,500,1000]
numscalar = [10,100,500,1000]
nummultiplication = [10,100,500,1000]
numscalarmultiplication = [10,100,500,1000]

def smc_performanceAddition(P,A):
    Secretvalues: list[Secret] = []
    expression = None
    participantsids = [ i for i in range(P)]
    value_dict = {}
    # Initialize the dictionary with the first secret equal to 0 for each party such that they will be in the protocol
    for i in range(P):
        value_dict[str(i)] = {Secret(): 0}
    for i in range(A):
        randParty = random.randint(0, P-1)
        randParty_str = str(randParty)
        Secretvalues.append(Secret()) # For the expression

        # Creating a dictionary for the value of the secret
        if randParty_str in value_dict:
            # If the key exists, update the nested dictionary
            value_dict[randParty_str][Secretvalues[i]] =  random.randint(0, 100)
        else:
            # If the key does not exist, create a new nested dictionary
            value_dict[randParty_str] = {Secretvalues[i]: random.randint(0, 100)}
        if expression is None:
            expression = Secretvalues[i]  # Initialize expression with the first Secret
        else:
            expression += Secretvalues[i]  # Add subsequent Secrets to the expression

    start = time.time()
    res = suite(value_dict, expression)
    end = time.time()

    #print(res)
    #print(value_dict)
    #print(expression)
    #print(Secretvalues)
    return end - start

def smc_performanceScalar(P,S):
    expression = None
    value_dict = {}
    # Initialize the dictionary with the first secret equal to 0 for each party such that they will be in the protocol
    for i in range(P):
        value_dict[str(i)] = {Secret(): 0}
    for i in range(S):
        if expression is None:
            expression =  Scalar(random.randint(0, 100)) # Initialize expression with the first Secret
        else:
            expression += Scalar(random.randint(0, 100))  # Add subsequent Secrets to the expression
    start = time.time()

    res = suite(value_dict, expression)
    end = time.time()
    #print(res)
    #print(expression)
    return end - start

def smc_performanceMultiplication(P,M):
    Secretvalues: list[Secret] = []
    expression = None
    participantsids = [ i for i in range(P)]
    value_dict = {}
    # Initialize the dictionary with the first secret equal to 0 for each party such that they will be in the protocol
    for i in range(P):
        value_dict[str(i)] = {Secret(): 0}
    for i in range(M):
        randParty = random.randint(0, P-1)
        randParty_str = str(randParty)
        Secretvalues.append(Secret())
        # Creating a dictionary for the value of the secret
        if randParty_str in value_dict:
            # If the key exists, update the nested dictionary
            value_dict[randParty_str][Secretvalues[i]] =  random.randint(0, 100)
        else:
            # If the key does not exist, create a new nested dictionary
            value_dict[randParty_str] = {Secretvalues[i]: random.randint(0, 100)}
        if expression is None:
            expression = Secretvalues[i]
        else:
            expression *= Secretvalues[i]


    start = time.time()
    res = suite(value_dict, expression)
    end = time.time()
    #print(res)
    #print(value_dict)
    #print(expression)
    return end - start

def smc_performanceScalarMultiplication(P,SM):
    expression = None
    value_dict = {}
    # Initialize the dictionary with the first secret equal to 0 for each party such that they will be in the protocol
    for i in range(P):
        value_dict[str(i)] = {Secret(): 0}
    for i in range(SM):
        if expression is None:
            expression =  Scalar(random.randint(0, 100))
        else:
            expression *= Scalar(random.randint(0, 100))
    start = time.time()
    res = suite(value_dict, expression)
    end = time.time()
    #print(res)
    #print(expression)
    return end - start


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)

    return results


#test = smc_performanceAddition(34,130)
#print(test)

#test2 = smc_performanceScalar(10,10)
#print(test2)

#test3 = smc_performanceMultiplication(10,10)
#print(test3)

#test4 = smc_performanceScalarMultiplication(10,10)
#print(test4)


def test_performance():
    index = 0
    A = np.zeros((len(numaddition),30)) # 30 is the number of iterations
    S = np.zeros((len(numscalar),30))
    M = np.zeros((len(nummultiplication),30))
    SM = np.zeros((len(numscalarmultiplication),30))

    for i in NumParties:
        for j in numaddition:
            index += 1
            for k in range(30):
                print(f"Number of Parties: {i}, Number of Additions: {j}")
                res = smc_performanceAddition(i,j)
                #print(res)
                A[index][k] = res

        index = 0
        for j in numscalar:
            index += 1
            for k in range(30):
                print(f"Number of Parties: {i}, Number of Scalar: {j}")
                res = smc_performanceScalar(i,j)
                #print(res)
                S[index][k] = res

        index = 0
        for j in nummultiplication:
            index += 1
            for k in range(30):
                print(f"Number of Parties: {i}, Number of Multiplication: {j}")
                res = smc_performanceMultiplication(i,j)
                #print(res)
                M[index][k] = res

        index = 0
        for j in numscalarmultiplication:
            index += 1
            for k in range(30):
                print(f"Number of Parties: {i}, Number of Scalar Multiplication: {j}")
                res = smc_performanceScalarMultiplication(i,j)
                #print(res)
                SM[index][k] = res


    print(A)

#test_performance()
