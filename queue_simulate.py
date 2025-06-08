import random
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import numpy as np

class Person:
    def __init__(self, arrive_time):
        self.arrival_time = arrive_time
        self.queue_entry_time = None
        self.start_service_time = None

class Server:
    def __init__(self, lam):
        self.service_rate = lam
        self.start_time = 0
        self.end_time = 0
        self.person = None

    def insert(self, person, time):
        self.start_time = time
        self.end_time = time + random.expovariate(self.service_rate)
        self.person = person

    def done(self, time):
        return time >= self.end_time

    def get_person(self):
        tmp = self.person
        self.person = None
        server_time = self.end_time - self.start_time
        return tmp, server_time

def simulate_queue(arrival_rate, service_rate, simulation_time=10000):
    people = []
    t = 0
    while True:
        t += random.expovariate(arrival_rate)
        if t > simulation_time:
            break
        people.append(Person(t))

    queue = deque()
    server = Server(service_rate)
    p = 0

    customers_served = 0
    time_spent_in_system = 0
    time_spent_in_queue = 0
    time_server_busy = 0
    customers_in_system = 0
    average_customers_in_system = 0
    average_customers_in_queue = 0
    proportions = defaultdict(float)

    num_steps = len(np.arange(1, simulation_time + 1, 0.001))
    for time in np.arange(1, simulation_time + 1, 0.001):
        average_customers_in_queue += len(queue) / num_steps
        average_customers_in_system += customers_in_system / num_steps
        proportions[customers_in_system] += 0.001

        while p < len(people) and people[p].arrival_time <= time:
            people[p].queue_entry_time = time
            queue.append(people[p])
            customers_in_system += 1
            p += 1

        if server.done(time):
            person, server_time = server.get_person()
            if person is not None:
                customers_served += 1
                time_spent_in_system += (time - person.arrival_time)
                time_spent_in_queue += (person.start_service_time - person.queue_entry_time)
                time_server_busy += server_time
                customers_in_system -= 1

            if queue:
                next_person = queue.popleft()
                next_person.start_service_time = time
                server.insert(next_person, time)

    utilization = time_server_busy / simulation_time
    avg_customers_in_system = average_customers_in_system
    avg_customers_in_queue = average_customers_in_queue
    avg_time_in_system = time_spent_in_system / customers_served
    avg_time_in_queue = time_spent_in_queue / customers_served

    results = {
        # Simulation metrics
        "Total Served": customers_served,
        "Total System Time": time_spent_in_system,
        "Total Queue Time": time_spent_in_queue,
        "Total Busy Time": time_server_busy,
        # Performance metrics
        "p": utilization,
        "L": avg_customers_in_system,
        "Lq": avg_customers_in_queue,
        "Ws": avg_time_in_system / 60,  # convert to minutes
        "Wq": avg_time_in_queue / 60,  # convert to minutes
        # Probabilities
        "P0": proportions[0] / simulation_time,
        "P1": proportions[1] / simulation_time,
        "P2": proportions[2] / simulation_time,
        "P3": proportions[3] / simulation_time,
    }

    return results

def calculate_theoretical_mm1(arrival_rate, service_rate):
    p = arrival_rate / service_rate
    L = p / (1 - p)
    Lq = p**2 / (1 - p)
    Ws = 1 / (service_rate - arrival_rate)
    Wq = arrival_rate / (service_rate * (service_rate - arrival_rate))
    Pn = lambda n: (1 - p) * p**n

    return {
        "Total Served": "-",
        "Total System Time": "-",
        "Total Queue Time": "-",
        "Total Busy Time": "-",
        "p": p,
        "L": L,
        "Lq": Lq,
        "Ws": Ws / 60,  # convert to minutes
        "Wq": Wq / 60,
        "P0": Pn(0),
        "P1": Pn(1),
        "P2": Pn(2),
        "P3": Pn(3),
    }

def print_results_comparison(arrival_rate, service_rate):
    sim = simulate_queue(arrival_rate, service_rate)
    theo = calculate_theoretical_mm1(arrival_rate, service_rate)

    print(f"{'Metric':<20} | {'Simulation':<15} | {'Theoretical':<15}")
    print("-" * 55)
    for key in [
        "Total Served", "Total System Time", "Total Queue Time", "Total Busy Time",
        "p", "L", "Lq", "Ws", "Wq", "P0", "P1", "P2", "P3"
    ]:
        sim_val = sim[key]
        theo_val = theo[key]

        if isinstance(sim_val, float):
            sim_val = f"{sim_val:.4f}" if key not in ["Ws", "Wq"] else f"{sim_val:.4f} min"
        if isinstance(theo_val, float):
            theo_val = f"{theo_val:.4f}" if key not in ["Ws", "Wq"] else f"{theo_val:.4f} min"

        print(f"{key:<20} | {sim_val:<15} | {theo_val:<15}")

def plot_simulation_wq_vs_utilization():
    service_rate = 12
    utilization_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    sim_wq_values = []
    theo_wq_values = []

    for rho in utilization_values:
        arrival_rate = rho * service_rate
        
        result = simulate_queue(arrival_rate, service_rate, simulation_time=5000)
        sim_wq_values.append(result["Wq"])  # Wq in minutes
        
        Wq_theoretical = (arrival_rate / (service_rate * (service_rate - arrival_rate))) / 60
        theo_wq_values.append(Wq_theoretical)

    plt.figure(figsize=(10, 6))
    # simulation line
    plt.plot(utilization_values, sim_wq_values, marker='o', linestyle='-', label='Simulation $W_q$')
    # theoretical line
    plt.plot(utilization_values, theo_wq_values, marker='s', linestyle='--', label='Theoretical $W_q$')
    plt.title("Average Queue Time in Queue ($W_q$) vs Utilization ($\\rho$)")
    plt.xlabel("Utilization ($\\rho$)")
    plt.ylabel("Average Waiting Time in Queue ($W_q$) [minutes]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print_results_comparison(4, 12)
    print("-" * 55)
    print()
    print_results_comparison(6, 12)
    print("-" * 55)
    print()
    print_results_comparison(10, 12)
    print("-" * 55)
    print()

    plot_simulation_wq_vs_utilization()