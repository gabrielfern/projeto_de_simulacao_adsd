from random import randint
import simpy

class CPU:
    def __init__(self, env):
        self.env = env
        self.disk = Disk(env)
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('CPU running at %d' %env.now)
            yield self.env.timeout(randint(1, 3))
            print('waiting the Disk at %d' %env.now)
            yield self.env.process(self.disk.get_resource())


class Disk:
    def __init__(self, env):
        self.env = env

    def get_resource(self):
        yield self.env.timeout(randint(5, 10))


env = simpy.Environment()
CPU(env)
env.run(until=30)
