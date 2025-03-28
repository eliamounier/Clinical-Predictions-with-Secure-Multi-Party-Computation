import time
import random
import matplotlib.pyplot as plt
import os
import csv
import sys
import numpy as np

from multiprocessing import Process, Queue

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty


NumParties = [100,20,10,5,2]
numaddition = [1000,500,100,10]
numscalar = [1000,500,100,10]
nummultiplication = [100,75,50,25,10,5]
numscalarmultiplication = [100,75,50,25,10,5]

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


def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_results_to_csv(results, filename):
    """Save results to a CSV file. If file exists, append to it; otherwise create new."""
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a' if file_exists else 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header only if creating a new file
        if not file_exists:
            writer.writerow(['Parties', 'Operations', 'Time'])
            
        # Write data rows
        
        writer.writerow(results) 

def plot_boxplots_operation(data_file, operation_type, output_file):
    """Create boxplot visualization from data with all operations on the same graph."""
    # Read data from CSV
    operations = []
    times_by_operation = {}
    
    with open(data_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            p, op, t = row
            p, op, t = int(p), int(op), float(t)
            
            if op not in operations:
                operations.append(op)
                times_by_operation[op] = []
                
            times_by_operation[op].append(t)
    
    # Sort operations for consistent ordering
    operations.sort()
    
    # Prepare data for plotting
    data_to_plot = [times_by_operation[op] for op in operations]
    labels = [f"{op}" for op in operations]
    
    # Create a single plot
    plt.figure(figsize=(10, 6))
    box = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    # Add some visual enhancement
    colors = ['lightblue', 'lightgreen', 'lightpink']
    for patch, color in zip(box['boxes'], colors[:len(operations)]):
        patch.set_facecolor(color)
    
    plt.title(f"{operation_type} Performance (20 Parties)")
    plt.xlabel("Number of Operations")
    plt.ylabel("Time (seconds)")
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Boxplot saved to {output_file}")

def plot_party_scaling(data_file, operation_type, output_file):
    """Create visualization showing how execution time scales with number of parties."""
    # Read data from CSV
    parties = []
    times_by_party = {}
    operation_count = None
    
    with open(data_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            p, op, t = row
            p, op, t = int(p), int(op), float(t)
            
            # Verify we're looking at consistent operation count
            if operation_count is None:
                operation_count = op
            elif operation_count != op:
                print(f"Warning: Found inconsistent operation count: {op} vs {operation_count}")
            
            if p not in parties:
                parties.append(p)
                times_by_party[p] = []
                
            times_by_party[p].append(t)
    
    # Sort parties for consistent ordering
    parties.sort()
    
    # Prepare data for plotting
    data_to_plot = [times_by_party[p] for p in parties]
    labels = [f"{p}" for p in parties]
    
    # Create boxplot
    plt.figure(figsize=(12, 7))
    box = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    # Add color to boxes
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(parties)))
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.title(f"{operation_type} Performance Scaling with Number of Parties")
    plt.xlabel("Number of Parties")
    plt.ylabel("Time (seconds)")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add text about operations
    plt.annotate(f'All measurements with {operation_count} operations', 
                xy=(0.5, 0.01), 
                xycoords='figure fraction',
                ha='center',
                fontsize=10,
                style='italic')
    
    # Calculate and plot trend line
    means = [np.mean(times_by_party[p]) for p in parties]
    plt.plot(range(1, len(parties) + 1), means, 'r-', linewidth=2, label='Mean Times')
    
    # Add legend
    plt.legend()
    
    # Make y-axis start at 0 for better context
    plt.ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Party scaling plot saved to {output_file}")
    
    # Optional: Create additional plot showing scaling relationship
    plt.figure(figsize=(10, 6))
    plt.scatter(parties, means, color='blue', s=100, label='Mean Execution Time')
    
    # Try to fit a line to see if it's roughly linear
    if len(parties) > 2:
        coeffs = np.polyfit(parties, means, 1)
        poly = np.poly1d(coeffs)
        x_line = np.linspace(min(parties), max(parties), 100)
        plt.plot(x_line, poly(x_line), 'r--', label=f'Linear Fit: {coeffs[0]:.4f}x + {coeffs[1]:.4f}')
    
    plt.title(f"{operation_type} Scaling Relationship ({operation_count} Operations)")
    plt.xlabel("Number of Parties")
    plt.ylabel("Mean Time (seconds)")
    plt.grid(True)
    plt.legend()
    
    # Make y-axis start at 0 for better context
    plt.ylim(bottom=0)
    
    scaling_output = output_file.replace('.', '_scaling.')
    plt.tight_layout()
    plt.savefig(scaling_output)
    plt.close()
    print(f"Scaling relationship plot saved to {scaling_output}")


def test_operationperformance():
    """Run all performance tests and save results."""
    # Create directories for outputs
    ensure_directory("results")
    ensure_directory("plots")
    
    # Run tests for each operation type
    operation_types = {
        "Addition": (smc_performanceAddition, numaddition),
        "Scalar": (smc_performanceScalar, numscalar),
        "Multiplication": (smc_performanceMultiplication, nummultiplication),
        "ScalarMultiplication": (smc_performanceScalarMultiplication, numscalarmultiplication)
    }
    
    for op_name, (op_func, op_sizes) in operation_types.items():
        results = []
        csv_file = f"results/{op_name}_results.csv"
        for op_count in op_sizes:
            for i in range(5):
                print(f"Testing {op_name}: Parties={20}, Operations={op_count}")

                runtime = op_func(20, op_count)
                results = [20, op_count, runtime]
                print(f"  {runtime:.4f}s")
                # Save results to CSV    
                save_results_to_csv(results, csv_file)
                
              


def test_partyperformance():
    csv_file = f"results/party_results.csv"
    for party in NumParties:
        for i in range(20):
            print(f"Testing Parties={party}, Operations={100}")
            runtime = smc_performanceAddition(party,100)
            results = [party, 100, runtime]
            print(f"  {runtime:.4f}s")
            save_results_to_csv(results, csv_file)

def plotting():
    name = ["Addition","Scalar","Multiplication","ScalarMultiplication"]

    for n in name:
        csv_file = f"results/{n}_results.csv"
        # Create visualization
        plot_file = f"plots/{n}_boxplot.png"
        plot_boxplots_operation(csv_file, n, plot_file)
    csv_file = f"results/party_results.csv"
    plot_file = f"plots/party_boxplot.png"
    plot_party_scaling(csv_file,"Addition",plot_file)

        


if __name__ == "__main__":
    sys.setrecursionlimit(3000)
    #test_operationperformance()
    #test_partyperformance()
    #plotting()