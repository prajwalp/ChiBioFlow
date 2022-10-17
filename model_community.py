import numpy as np
from scipy.integrate import odeint


class Chemostat():
    def __init__(self, name):
        # Model paramters are stored in chemostat class
        self.K = 1.5
        self.K_init = self.K
        self.Ks = [self.K]
        self.r = 0.273
        self.N = 0.08

        # Modelling values
        self.ys = np.ndarray(0)
        self.name = name
        self.dilution_factors = None

    def model(self, N, t):
        # Simple logistic model
        return self.r * N * (1 - N/self.K)

    def get_dilution_factor(self, xs, x_dilutions):
        # Calcualtes dilution factor for every transfer
        x_dilution_index = [list(xs).index(x_dilution)
                            for x_dilution in x_dilutions[:-1]]
        self.dilution_factors = [self.ys[i] / self.ys[i + 1]
                                 for i in x_dilution_index]


class Chain():
    def __init__(self, chems):
        self.chain = [Chemostat(chem) for chem in range(chems)]
        # Chemostat volume
        self.volume = 20
        # Transfer rates are dilutions per hour default is 2
        self.transfer_rate = 2
        self.dilution_rate = 0.31395
        # Storing time related data points
        self.xs = np.ndarray(0)
        self.x_dilutions = []

    def get_dilution(self):
        # This function calculates the dilution rate for steady state
        # Only helper function not necessary for modelling
        c1 = self.chain[0]
        # Calculating OD after 1 hour to calculate necessary dilution
        N1 = [e[0] for e in odeint(c1.model, c1.N, [0, 0.5])][-1]
        return ((2 * self.volume * (N1 - c1.N)) / c1.N) / self.volume

    def dilute(self):
        # Function that simulates a dilution row
        self.v_trans = self.dilution_rate * self.volume / self.transfer_rate
        for counter, c in enumerate(self.chain):
            # First reactor receives only media
            if counter == 0:
                N_in = 0
            else:
                # Other reactors also cells
                N_in = self.chain[counter - 1].N
            c.N = (N_in * self.v_trans + c.N * self.volume) / \
                (self.v_trans + self.volume)

    def carrying_capacity(self):
        # Recalculates carrying capacity for every reactor
        self.v_trans = self.dilution_rate * self.volume / self.transfer_rate
        for counter, c in enumerate(self.chain):
            if counter == 0:
                K_in = c.K_init
            else:
                K_in = self.chain[counter - 1].K
            c.K = (K_in * self.v_trans + c.K * self.volume) / \
                (self.v_trans + self.volume)
            c.Ks.append(c.K)

    def experiment(self, exp_time):
        if self.transfer_rate != 0:
            # Stores how many transfers are done in one experiment
            intervals = int(exp_time * self.transfer_rate)
            # Time between two dilutions
            interval = 1 / self.transfer_rate
            for i in range(intervals):
                # Simulated time scale
                xs = interval * i + np.arange(0, interval, 0.5)
                xs = np.append(xs, interval+interval*i)
                self.xs = np.concatenate([self.xs, xs])
                if i != 0:
                    # No transfers in the first cycle
                    self.dilute()
                    self.x_dilutions.append(xs[0])
                    self.carrying_capacity()
                for c in self.chain:
                    # Modelled OD values
                    ys = [e[0] for e in odeint(c.model, c.N, xs)]
                    c.ys = np.concatenate([c.ys, ys])
                    # Storing latest OD
                    c.N = c.ys[-1]
                    # Carrying capacity reduces by neto growth
                    net_N = ys[-1] - ys[0]
                    c.K = c.K - net_N

        if self.transfer_rate == 0:
            # Models growth curves with no dilutions
            for c in self.chain:
                self.xs = np.arange(0, exp_time, 0.5)
                c.ys = [e[0] for e in odeint(c.model, c.N, self.xs)]
                c.N = c.ys[-1]