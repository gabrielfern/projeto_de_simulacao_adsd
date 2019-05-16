from random import randint
import simpy


class CPU:
    def __init__(self, env):
        self.env = env
        self.disk = Disk(env)

    def run(self):
        print('CPU running at %d' %env.now)
        yield self.env.timeout(randint(1, 3))
        print('waiting the Disk at %d' %env.now)
        yield self.env.process(self.disk.get_resource())


class Disk:
    def __init__(self, env):
        self.env = env

    def get_resource(self):
        yield self.env.timeout(randint(5, 10))


class ClientWebBrowser:
    def __init__(self, env):
        self.env = env
        self.cpu = CPU(env)
        self.action = env.process(self.working())

    def client_thinking(self):
        yield self.env.timeout(randint(20, 100))

    def working(self):
        while True:
            yield self.env.process(self.client_thinking())
            print('Client acts at %d' %env.now)
            if env.now % 2 == 0:
                yield self.env.process(self.cpu.run())


env = simpy.Environment()
ClientWebBrowser(env)
env.run(until=300)
