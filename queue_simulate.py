import random
from collections import deque, defaultdict
import numpy as np

class Person:
    def __init__(self, arrive_time):
        self.arrival_time = arrive_time
        self.queue_entry_time = None
        self.start_service_time = None

    def __repr__(self):
        return f"{self.arrival_time:.3f}"

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

    def __repr__(self):
        return f"Server(start={self.start_time:.3f}, end={self.end_time:.3f})"

def to_hours_minutes(seconds):
    minutes = seconds / 60
    return f"{int(minutes // 60)}h {int(minutes % 60)}m"

def main():
    arrival_rate = 4
    service_rate = 12
    simulation_time = 10000

    people = []
    t = 0
    while True:
        t += random.expovariate(arrival_rate)
        if t > simulation_time:
            break
        people.append(Person(t))

    # print(people)
    print("people size: "+ str(len(people)))

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

    proportions = defaultdict(int)

    for time in np.arange(1, simulation_time + 1, 0.001):
        average_customers_in_queue += len(queue) / simulation_time
        average_customers_in_system += customers_in_system / simulation_time
        proportions[customers_in_system] += 0.001

        # Handle new arrivals
        while p < len(people) and people[p].arrival_time <= time:
            people[p].queue_entry_time = time
            queue.append(people[p])
            customers_in_system += 1
            p += 1

        # If server is done, remove the person
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

    # Final stats
    utilization = time_server_busy / simulation_time
    avg_customers_in_system = average_customers_in_system
    avg_customers_in_queue = average_customers_in_queue
    avg_time_in_system = time_spent_in_system / customers_served
    avg_time_in_queue = time_spent_in_queue / customers_served

    print("\n--- Simulation Results ---")
    print(f"Total customers served: {customers_served}")
    print(f"Total time spent in system: {time_spent_in_system:.2f}")
    print(f"Total time spent in queue: {time_spent_in_queue:.2f}")
    print(f"Total server busy time: {time_server_busy:.2f}")
    print(f"Time-averaged customers in system (L): {avg_customers_in_system:.4f}")
    print(f"Time-averaged customers in queue (Lq): {avg_customers_in_queue:.4f}")
    print(f"Utilization factor (ρ): {utilization:.4f}")
    print(f"Average time in system (Ws): {to_hours_minutes(avg_time_in_system)}")
    print(f"Average time in queue (Wq): {to_hours_minutes(avg_time_in_queue)}")

    print("\nProportion of time system had N customers:")
    for i in range(4):
        prop = proportions[i] / simulation_time
        print(f"P{i} (Probability of {i} customers): {prop:.4f}")

if __name__ == "__main__":
    main()
