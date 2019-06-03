from random import random
from random import randint
import simpy


class CPU:
    def __init__(self, env, base_time = 1, top_time = 3):
        self.env = env
        self.disk = Disk(env)
        self.base_time = base_time
        self.top_time = top_time

    def run(self):
        print('CPU running at %d' %env.now)
        yield self.env.timeout(randint(self.base_time, self.top_time))
        print('waiting the Disk at %d' %env.now)
        yield self.env.process(self.disk.get_resource())


class Disk:
    def __init__(self, env, base_time = 5, top_time = 10):
        self.env = env
        self.base_time = base_time
        self.top_time = top_time

    def get_resource(self):
        yield self.env.timeout(randint(self.base_time, self.top_time))


class ClientWebBrowser:
    def __init__(self, env, base_time = 20, top_time = 100):
        self.env = env
        self.base_time = base_time
        self.top_time = top_time
        self.cpu = CPU(env)
        self.action = env.process(self.working())

    def client_thinking(self):
        yield self.env.timeout(randint(self.base_time, self.top_time))

    def working(self):
        while True:
            yield self.env.process(self.client_thinking())
            print('Client acts at %d' %env.now)
            if env.now % 2 == 0:
                yield self.env.process(self.cpu.run())


def decision(prob):
    return random() < prob


env = simpy.Environment()
ClientWebBrowser(env)
env.run(until=300)
