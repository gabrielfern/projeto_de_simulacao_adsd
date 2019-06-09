from random import random
from random import randint
from statistics import mean
from statistics import stdev
import sys

import simpy

CLIENTS = 5
DURATION = 100


class CPU:
    def __init__(self, env, id, next_server=None, busy_time=(1, 3), disk_prob=0.3, next_prob=0.14):
        self.env = env
        self.disk = Disk(env, id)
        self.id = id
        self.next_server = next_server
        self.busy_time = busy_time
        self.disk_prob = disk_prob
        self.next_prob = next_prob
        self.core = simpy.Resource(env, capacity=1)
        self.usage_time = 0
        self.response_time = []
        self.wait_time = []
        self.queue_size = []

    def process(self, client):
        with self.core.request() as req:
            self.queue_size.append(len(self.core.queue))
            arrival_time = self.env.now
            yield req
            self.wait_time.append(env.now - arrival_time)

            rand = randint(self.busy_time[0], self.busy_time[1])
            self.usage_time += min(rand, DURATION - 1 - env.now)
            print('%s - CPU running from %d" to %d" for %s' %(self.id,
                env.now, env.now + rand, client))

            yield self.env.timeout(rand)
            self.response_time.append(env.now - arrival_time)


    def run(self, client):
        yield self.env.process(self.process(client))
        while 1:
            if decision(self.disk_prob):
                yield self.env.process(self.disk.get_resource(client))
                yield self.env.process(self.process(client))
            elif self.next_server != None and decision(self.next_prob/(1-self.disk_prob)):
                yield self.env.process(self.next_server.run(client))
                yield self.env.process(self.process(client))
            else: break


class Disk:
    def __init__(self, env, id, busy_time=(5, 10)):
        self.env = env
        self.id = id
        self.busy_time = busy_time
        self.controller = simpy.Resource(env, capacity=1)
        self.usage_time = 0
        self.response_time = []
        self.wait_time = []
        self.queue_size = []

    def get_resource(self, client):
        with self.controller.request() as req:
            self.queue_size.append(len(self.controller.queue))
            arrival_time = self.env.now
            yield req
            self.wait_time.append(env.now - arrival_time)

            rand = randint(self.busy_time[0], self.busy_time[1])
            self.usage_time += min(rand, DURATION - 1 - env.now)
            print('%s - Disk working from %d" to %d" for %s' %(self.id,
                env.now, env.now + rand, client))

            yield self.env.timeout(rand)
            self.response_time.append(env.now - arrival_time)


class ClientWebBrowser:
    usage_time = [0 for _ in range(CLIENTS)]
    response_time = [[] for _ in range(CLIENTS)]
    wait_time = [[] for _ in range(CLIENTS)]
    queue_size = [[] for _ in range(CLIENTS)]

    def __init__(self, env, server, id, index, client_time=(10, 100), busy_time=(1, 3), server_prob=0.5):
        self.env = env
        self.server = server
        self.id = id
        self.index = index
        self.client_time = client_time
        self.busy_time = busy_time
        self.server_prob = server_prob
        self.thread = simpy.Resource(env, capacity=1)
        env.process(self.client_loop())

    def process(self):
        with self.thread.request() as req:
            ClientWebBrowser.queue_size[self.index].append(len(self.thread.queue))
            arrival_time = self.env.now
            yield req
            ClientWebBrowser.wait_time[self.index].append(env.now - arrival_time)

            rand = randint(self.busy_time[0], self.busy_time[1])
            ClientWebBrowser.usage_time[self.index] += min(rand, DURATION - 1 - env.now)
            print('%s Web Browser running from %d" to %d"' %(self.id,
                    env.now, env.now + rand))

            yield self.env.timeout(rand)
            ClientWebBrowser.response_time[self.index].append(env.now - arrival_time)

    def client_action_handler(self):
        yield self.env.process(self.process())

        while decision(self.server_prob):
            yield self.env.process(self.server.run(self.id))
            yield self.env.process(self.process())

    def client_thinking(self):
        yield self.env.timeout(randint(self.client_time[0], self.client_time[1]))

    def client_loop(self):
        while True:
            yield self.env.process(self.client_thinking())
            print(self.id + ' acts at %d"' %env.now)
            self.env.process(self.client_action_handler())


def decision(prob):
    return random() < prob


env = simpy.Environment()

database_server = CPU(env, 'Database Server')
application_server = CPU(env, 'Application Server', database_server)
web_server = CPU(env, 'Web Server', application_server)

clients = []
for i in range(1, CLIENTS + 1):
    clients.append(ClientWebBrowser(env, web_server, 'Client ' + str(i), i - 1))

stdout = sys.stdout
sys.stdout = open('output.log', 'w')

env.run(until=DURATION)

sys.stdout = stdout
print('Detailed log written to "output.log"')
print('Clients in the simulation:', CLIENTS)
print('Simulation time:', DURATION)
print()
for server in (web_server, application_server, database_server):
    print((server.id + ' CPU').ljust(59, '-'))
    print('Utilization:', server.usage_time / DURATION)

    m = '%11.6f' %mean(server.response_time) if len(server.response_time) > 0 else 'NaN'.rjust(11)
    sd = '%11.6f' %stdev(server.response_time) if len(server.response_time) > 1 else 'NaN'.rjust(6)
    print('Response Time mean: ' + m + '  std deviation: ' + sd)

    m = '%15.6f' %mean(server.wait_time) if len(server.wait_time) > 0 else 'NaN'.rjust(15)
    sd = '%11.6f' %stdev(server.wait_time) if len(server.wait_time) > 1 else 'NaN'.rjust(6)
    print('Wait Time mean: ' + m + '  std deviation: ' + sd)

    m = '%14.6f' %mean(server.queue_size) if len(server.queue_size) > 0 else 'NaN'.rjust(14)
    sd = '%11.6f' %stdev(server.queue_size) if len(server.queue_size) > 1 else 'NaN'.rjust(6)
    print('Queue Size mean: ' + m + '  std deviation: ' + sd)

    print((server.id + ' Disk').ljust(59, '-'))
    print('Utilization:', server.disk.usage_time / DURATION)

    m = '%11.6f' %mean(server.disk.response_time) if len(server.disk.response_time) > 0 else 'NaN'.rjust(11)
    sd = '%11.6f' %stdev(server.disk.response_time) if len(server.disk.response_time) > 1 else 'NaN'.rjust(6)
    print('Response Time mean: ' + m + '  std deviation: ' + sd)

    m = '%15.6f' %mean(server.disk.wait_time) if len(server.disk.wait_time) > 0 else 'NaN'.rjust(15)
    sd = '%11.6f' %stdev(server.disk.wait_time) if len(server.disk.wait_time) > 1 else 'NaN'.rjust(6)
    print('Wait Time mean: ' + m + '  std deviation: ' + sd)

    m = '%14.6f' %mean(server.disk.queue_size) if len(server.disk.queue_size) > 0 else 'NaN'.rjust(14)
    sd = '%11.6f' %stdev(server.disk.queue_size) if len(server.disk.queue_size) > 1 else 'NaN'.rjust(6)
    print('Queue Size mean: ' + m + '  std deviation: ' + sd)


print(('Client Web Browsers').ljust(59, '-'))
utilization = [usage_time / DURATION for usage_time in ClientWebBrowser.usage_time]
m = '%13.6f' %mean(utilization) if len(utilization) > 0 else  'NaN'.rjust(13)
sd = '%11.6f' %stdev(utilization) if len(utilization) > 1 else 'NaN'.rjust(6)
print('Utilization mean: ' + m + '  std deviation: ' + sd)

response_time = [item for sublist in ClientWebBrowser.response_time for item in sublist]
m = '%11.6f' %mean(response_time) if len(response_time) > 0 else  'NaN'.rjust(11)
sd = '%11.6f' %stdev(response_time) if len(response_time) > 1 else 'NaN'.rjust(6)
print('Response Time mean: ' + m + '  std deviation: ' + sd)

wait_time = [item for sublist in ClientWebBrowser.wait_time for item in sublist]
m = '%15.6f' %mean(wait_time) if len(wait_time) > 0 else 'NaN'.rjust(15)
sd = '%11.6f' %stdev(wait_time) if len(wait_time) > 1 else 'NaN'.rjust(6)
print('Wait Time mean: ' + m + '  std deviation: ' + sd)

queue_size = [item for sublist in ClientWebBrowser.queue_size for item in sublist]
m = '%14.6f' %mean(queue_size) if len(queue_size) > 0 else 'NaN'.rjust(14)
sd = '%11.6f' %stdev(queue_size) if len(queue_size) > 1 else 'NaN'.rjust(6)
print('Queue Size mean: ' + m + '  std deviation: ' + sd)