from random import random
from random import randint

import simpy

CLIENTS = 5
DURATION = 100


class CPU:
    def __init__(self, env):
        self.env = env
        self.disk = Disk(env)
        self.core = simpy.Resource(env, capacity=1)

    def process(self, client):
        with self.core.request() as req:
            yield req
            rand = randint(1, 3)
            print('CPU running from %d" to %d" for %s' %(env.now, env.now + rand, client))
            yield self.env.timeout(rand)

    def run(self, client):
        yield self.env.process(self.process(client))
        while decision(0.3):
            yield self.env.process(self.disk.get_resource(client))
            yield self.env.process(self.process(client))


class Disk:
    def __init__(self, env):
        self.env = env
        self.controller = simpy.Resource(env, capacity=1)

    def get_resource(self, client):
        with self.controller.request() as req:
            yield req
            rand = randint(5, 10)
            print('Disk working from %d" to %d" for %s' %(env.now, env.now + rand, client))
            yield self.env.timeout(rand)


class ClientWebBrowser:
    def __init__(self, env, server, id):
        self.env = env
        self.server = server
        self.id = id
        self.action = env.process(self.working())

    def client_thinking(self):
        yield self.env.timeout(randint(20, 100))

    def working(self):
        while True:
            yield self.env.process(self.client_thinking())
            print(self.id + ' acts at %d"' %env.now)
            if decision(0.5):
                yield self.env.process(self.server.run(self.id))


def decision(prob):
    return random() < prob


env = simpy.Environment()
server = CPU(env)
for i in range(1, CLIENTS + 1):
    ClientWebBrowser(env, server, "Client " + str(i))
env.run(until=DURATION)
