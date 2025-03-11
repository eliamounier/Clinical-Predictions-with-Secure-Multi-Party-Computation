from multiprocessing import Process, Queue, Value
from flask import request
from typing import List, Tuple
from time import sleep
from sys import getsizeof
import logging
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime


from server import app, run
from smc_party import SMCParty
from protocol import ProtocolSpec
from secret_sharing import Share
from expression import *
from config import SERVER_PORT

DISABLE_LOGS = True


def smc_client(
	client_id: str,
	prot: ProtocolSpec,
	value_dict: dict[str, dict[Secret, int]],
	queue: Queue,
):
	if DISABLE_LOGS:
		sys.stdout = open(os.devnull, "w")
	cli = SMCParty(
		client_id, "localhost", SERVER_PORT, protocol_spec=prot, value_dict=value_dict
	)
	res = cli.run()
	queue.put(res)
	print(f"{client_id} has finished!")


def smc_server(participants: List[str]):
	if DISABLE_LOGS:
		sys.stdout = open(os.devnull, "w")
	run("localhost", SERVER_PORT, participants)


def run_processes(server_args, *client_args):
	queue = Queue()
	server = Process(target=smc_server, args=(server_args,))
	clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]
	server.start()
	sleep(3)
	for client in clients:
		client.start()
	results = list()
	for client in clients:
		client.join()
	for client in clients:
		results.append(queue.get())
	server.terminate()
	server.join()
	sleep(2)

	return results


def unregister_before_request(handler):
	if handler in app.before_request_funcs[None]:
		app.before_request_funcs[None].remove(handler)


def unregister_after_request(handler):
	if handler in app.after_request_funcs[None]:
		app.after_request_funcs[None].remove(handler)


def run_experiment(
	parties: dict[str, dict[Secret, int]], expr: Expression, expected: int
) -> Tuple[int, int]:
	bytes_received = Value("i", 0)
	bytes_sent = Value("i", 0)

	def calculate_request_size():
		# Calculate request size
		request_size = getsizeof(request.headers) + getsizeof(request.url)
		if request.method == "POST":
			request_size += getsizeof(request.get_data())
		bytes_received.value += request_size

	def calculate_response_size(response):
		# Calculate response size
		response_size = getsizeof(response.headers) + getsizeof(response.get_data())
		bytes_sent.value += response_size
		return response

	app.before_request(calculate_request_size)
	app.after_request(calculate_response_size)

	participants = list(parties.keys())

	prot = ProtocolSpec(expr=expr, participant_ids=participants)
	clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

	results = run_processes(participants, *clients)

	unregister_before_request(calculate_request_size)
	unregister_after_request(calculate_response_size)

	for result in results:
		assert result == expected % Share.prime(), f"expected: {expected}, result: {result}"

	return bytes_received.value, bytes_sent.value


def process_results(experiment_name, results: dict[int, List[int]]):
	current_time = datetime.now().strftime("%d-%m_%H-%M-%S")
	filename = f"results/{experiment_name}_{current_time}.json"

	os.makedirs("results", exist_ok=True)
	with open(filename, "w") as file:
		json.dump(results, file)

	x = list(results.keys())
	y_received = [
		np.mean([measure[0] for measure in measures]) for measures in results.values()
	]
	yerr_received = [
		np.std([measure[0] for measure in measures]) for measures in results.values()
	]
	y_sent = [
		np.mean([measure[1] for measure in measures]) for measures in results.values()
	]
	yerr_sent = [
		np.std([measure[1] for measure in measures]) for measures in results.values()
	]

	return x, y_received, yerr_received, y_sent, yerr_sent

def show_plot(x, y_received, yerr_received, y_sent, yerr_sent, x_axis_title):
	# Create the plot with error bars
	plt.errorbar(x, y_received, yerr=yerr_received, fmt="-o", label="Total number of bytes received")
	plt.errorbar(x, y_sent, yerr=yerr_sent, fmt="-o", label="Total number of bytes sent")

	# Labels and title
	plt.xlabel(x_axis_title)
	plt.ylabel("")

	# Show the legend
	plt.legend()

	# Display the plot
	plt.show()

# effect of the number of participants
def experiment_1():
	print("Starting experiment 1: effect of the number of participants...")
	alice_secret = Secret()
	bob_secret = Secret()

	expr = alice_secret + bob_secret
	expected = 3 + 14

	number_of_participants = [2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

	results: dict[int, List[int]] = {}
	repeats = 10
	for n in number_of_participants:
		results[n] = []
		for r in range(repeats):
			parties = {
				"Alice": {alice_secret: 3},
				"Bob": {bob_secret: 14},
			}
			if (n - 2) < 0:
				raise ValueError("Not enough participants")
			for i in range(n - 2):
				parties[str(i)] = {}
			results[n].append(run_experiment(parties, expr, expected))
			print(f"  {n} participants, repeat n°{r + 1} done")

	x, y_received, yerr_received, y_sent, yerr_sent = process_results(
		"network_exp1", results
	)
	print("Experiment 1 done !")
	show_plot(x, y_received, yerr_received, y_sent, yerr_sent, "Number of parties")

# effect of the number of addition operations
def experiment_2():
	print("Starting experiment 2: effect of the number of addition operations...")
	alice_secret = Secret()
	bob_secret = Secret()

	parties = {
		"Alice": {alice_secret: 3},
		"Bob": {bob_secret: 14},
	}

	number_of_addition_operations = [10, 50, 100, 200, 500, 700, 1000]

	results: dict[int, List[int]] = {}
	repeats = 10
	for n in number_of_addition_operations:
		results[n] = []
		for r in range(repeats):
			expr = alice_secret + bob_secret
			expected = 3 + 14
			if (n - 2) < 0:
				raise ValueError("Not enough operations")
			for i in range(n - 2):
				if i % 2 == 0:
					expr += alice_secret
					expected += 3
				else:
					expr += bob_secret
					expected += 14
			results[n].append(run_experiment(parties, expr, expected))
			print(f"  {n} additions, repeat n°{r + 1} done")

	x, y_received, yerr_received, y_sent, yerr_sent = process_results(
		"network_exp2", results
	)
	print("Experiment 2 done !")
	show_plot(x, y_received, yerr_received, y_sent, yerr_sent, "Number of addition operations")

# effect of the number of additions of scalars
def experiment_3():
	print("Starting experiment 3: effect of the number of additions of scalars...")

	parties = {
		"Alice": {},
		"Bob": {},
	}

	number_of_addition_of_scalars = [10, 50, 100, 200, 500, 700, 1000]

	results: dict[int, List[int]] = {}
	repeats = 10
	for n in number_of_addition_of_scalars:
		results[n] = []
		for r in range(repeats):
			expr = Scalar(3) + Scalar(14)
			expected = 3 + 14
			if (n - 2) < 0:
				raise ValueError("Not enough operations")
			for i in range(n - 2):
				if i % 2 == 0:
					expr += Scalar(3)
					expected += 3
				else:
					expr += Scalar(14)
					expected += 14
			results[n].append(run_experiment(parties, expr, expected))
			print(f"  {n} additions of scalars, repeat n°{r + 1} done")

	x, y_received, yerr_received, y_sent, yerr_sent = process_results(
		"network_exp3", results
	)
	print("Experiment 3 done !")
	show_plot(x, y_received, yerr_received, y_sent, yerr_sent, "Number of additions of scalars")

# effect of the number of multiplication operations
def experiment_4():
	print("Starting experiment 4: effect of the number of multiplication operations...")
	alice_secret = Secret()
	bob_secret = Secret()

	parties = {
		"Alice": {alice_secret: 3},
		"Bob": {bob_secret: 14},
	}

	number_of_addition_of_scalars = [10, 50, 100, 200, 500, 700, 1000]

	results: dict[int, List[int]] = {}
	repeats = 10
	for n in number_of_addition_of_scalars:
		results[n] = []
		for r in range(repeats):
			expr = alice_secret * bob_secret
			expected = 3 * 14
			if (n - 2) < 0:
				raise ValueError("Not enough operations")
			for i in range(n - 2):
				if i % 2 == 0:
					expr *= alice_secret
					expected *= 3
				else:
					expr *= bob_secret
					expected *= 14
			results[n].append(run_experiment(parties, expr, expected))
			print(f"  {n} multiplication operations, repeat n°{r + 1} done")

	x, y_received, yerr_received, y_sent, yerr_sent = process_results(
		"network_exp4", results
	)
	print("Experiment 4 done !")
	show_plot(x, y_received, yerr_received, y_sent, yerr_sent, "Number of multiplication operations")

# effect of the number of multiplications of scalars
def experiment_5():
	print("Starting experiment 4: effect of the number of multiplications of scalars...")

	parties = {
		"Alice": {},
		"Bob": {},
	}

	number_of_addition_of_scalars = [10, 50, 100, 200, 500, 700, 1000]

	results: dict[int, List[int]] = {}
	repeats = 10
	for n in number_of_addition_of_scalars:
		results[n] = []
		for r in range(repeats):
			expr = Scalar(3) * Scalar(14)
			expected = 3 * 14
			if (n - 2) < 0:
				raise ValueError("Not enough operations")
			for i in range(n - 2):
				if i % 2 == 0:
					expr *= Scalar(3)
					expected *= 3
				else:
					expr *= Scalar(14)
					expected *= 14
			results[n].append(run_experiment(parties, expr, expected))
			print(f"  {n} multiplications of scalars, repeat n°{r + 1} done")

	x, y_received, yerr_received, y_sent, yerr_sent = process_results(
		"network_exp5", results
	)
	print("Experiment 5 done !")
	show_plot(x, y_received, yerr_received, y_sent, yerr_sent, "Number of multiplications of scalars")


def main():
	if DISABLE_LOGS:
		log = logging.getLogger("werkzeug")
		log.setLevel(logging.WARNING)

	# Uncomment the one you want to run
	# experiment_1()
	experiment_2()
	# experiment_3()
	# experiment_4()
	# experiment_5()


if __name__ == "__main__":
	main()
