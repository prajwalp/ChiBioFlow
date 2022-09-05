import numpy as np
from scipy.integrate import odeint


class Chemostat():
    def __init__(self, params):
        self.K = params['K']
        self.r = params['r']
        self.N = params['N']

        self.xs = np.ndarray(0)
        self.ys = np.ndarray(0)

    def model(self, N, t):
        return self.r * N * (1 - N/self.K)


class Chain():
    def __init__(self, temps):
        params = {28.0: {'r': 0.32,
                         'K': 1.1,
                         'N': 0.08},
                  33.0: {'r': 0.32,
                         'K': 0.85,
                         'N': 0},
                  38.0: {'r': 0.24,
                         'K': 0.26,
                         'N': 0},
                  43.0: {'r': 0,
                         'K': 0.8,
                         'N': 0}}
        self.chain = [Chemostat(params[temp]) for temp in temps]
        self.volume = 20
        self.dilution_rate = self.get_dilution()
        self.transfer_rate = 1

    def get_dilution(self):
        c1 = self.chain[0]
        N1 = [e[0] for e in odeint(c1.model, c1.N, [0, 1])][-1]
        return ((self.volume * (N1 - c1.N)) / c1.N) / self.volume

    def dilute(self):
        v_trans = self.dilution_rate * self.volume / self.transfer_rate
        for counter, c in enumerate(self.chain):
            if counter == 0:
                N_in = 0
            else:
                N_in = self.chain[counter - 1].N

            c.N = (N_in * v_trans + c.N * self.volume) / \
                (v_trans + self.volume)

    def experiment(self, exp_time, transfer_rate=2):
        self.transfer_rate = transfer_rate
        intervals = exp_time * self.transfer_rate
        interval = 1 / self.transfer_rate
        for i in range(intervals):
            for c in self.chain:
                xs = interval * i + np.arange(0, interval, 1/3600)
                c.xs = np.concatenate([c.xs, xs])
                ys = [e[0] for e in odeint(c.model, c.N, xs)]
                c.ys = np.concatenate([c.ys, ys])
                c.N = c.ys[-1]
            self.dilute()
