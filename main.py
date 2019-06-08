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

    def get_resource(self, client):
        with self.controller.request() as req:
            yield req
            rand = randint(self.busy_time[0], self.busy_time[1])
            self.usage_time += min(rand, DURATION - 1 - env.now)
            print('%s - Disk working from %d" to %d" for %s' %(self.id,
                env.now, env.now + rand, client))
            yield self.env.timeout(rand)


class ClientWebBrowser:
    def __init__(self, env, server, id, busy_time=(20, 100), server_prob=0.5):
        self.env = env
        self.server = server
        self.id = id
        self.busy_time = busy_time
        self.server_prob = server_prob
        self.action = env.process(self.working())

    def client_thinking(self):
        yield self.env.timeout(randint(self.busy_time[0], self.busy_time[1]))

    def working(self):
        while True:
            yield self.env.process(self.client_thinking())
            print(self.id + ' acts at %d"' %env.now)
            if decision(self.server_prob):
                yield self.env.process(self.server.run(self.id))


def decision(prob):
    return random() < prob


env = simpy.Environment()

database_server = CPU(env, 'Database Server')
application_server = CPU(env, 'Application Server', database_server)
web_server = CPU(env, 'Web Server', application_server)

for i in range(1, CLIENTS + 1):
    ClientWebBrowser(env, web_server, 'Client ' + str(i))

stdout = sys.stdout
sys.stdout = open('log', 'w')

env.run(until=DURATION)

sys.stdout = stdout
print('Log written to "log" file')
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
    print('Queue Size mean: '+ m + '  std deviation: ' + sd)

    print((server.id + ' Disk').ljust(59, '-'))
    print('Utilization:', server.disk.usage_time / DURATION)