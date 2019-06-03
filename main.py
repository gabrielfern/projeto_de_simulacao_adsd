from random import random
from random import randint

import simpy

CLIENTS = 5
DURATION = 100


class CPU:
    def __init__(self, env, id, next_server, busy_time=(1, 3)):
        self.env = env
        self.disk = Disk(env, id)
        self.id = id
        self.next_server = next_server
        self.busy_time = busy_time
        self.core = simpy.Resource(env, capacity=1)

    def process(self, client):
        with self.core.request() as req:
            yield req
            rand = randint(self.busy_time[0], self.busy_time[1])
            print('%s - CPU running from %d" to %d" for %s' %(self.id,
                env.now, env.now + rand, client))
            yield self.env.timeout(rand)

    def run(self, client):
        yield self.env.process(self.process(client))
        while 1:
            if decision(0.3):
                yield self.env.process(self.disk.get_resource(client))
                yield self.env.process(self.process(client))
            elif self.next_server != None and decision(0.2):
                yield self.env.process(self.next_server.run(client))
                yield self.env.process(self.process(client))
            else: break


class Disk:
    def __init__(self, env, id, busy_time=(5, 10)):
        self.env = env
        self.id = id
        self.busy_time = busy_time
        self.controller = simpy.Resource(env, capacity=1)

    def get_resource(self, client):
        with self.controller.request() as req:
            yield req
            rand = randint(self.busy_time[0], self.busy_time[1])
            print('%s - Disk working from %d" to %d" for %s' %(self.id,
                env.now, env.now + rand, client))
            yield self.env.timeout(rand)


class ClientWebBrowser:
    def __init__(self, env, server, id, busy_time=(20, 100)):
        self.env = env
        self.server = server
        self.id = id
        self.busy_time = busy_time
        self.action = env.process(self.working())

    def client_thinking(self):
        yield self.env.timeout(randint(self.busy_time[0], self.busy_time[1]))

    def working(self):
        while True:
            yield self.env.process(self.client_thinking())
            print(self.id + ' acts at %d"' %env.now)
            if decision(0.5):
                yield self.env.process(self.server.run(self.id))


def decision(prob):
    return random() < prob


env = simpy.Environment()

database_server = CPU(env, 'Database Server', None)
application_server = CPU(env, 'Application Server', database_server)
web_server = CPU(env, 'Web Server', application_server)

for i in range(1, CLIENTS + 1):
    ClientWebBrowser(env, web_server, 'Client ' + str(i))

env.run(until=DURATION)
