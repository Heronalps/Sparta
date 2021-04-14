# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
import math

# Define Action class
class Actions:
    def __init__(self, m):
        self.m = m
        self.mean = 0
        self.N = 0

    # Choose a random action
    def choose(self):
        return np.random.randn() + self.m

    # Update the action-value estimate
    def update(self, x):
        self.N += 1
        self.mean = (1 - 1.0 / self.N) * self.mean + 1.0 / self.N * x


def run_experiment(m1, m2, eps, N):
    actions = []
    length = math.ceil((m2 - m1) / 0.1)
    
    for i in np.arange(m1, m2, 0.1):
        actions.append(Actions(i))
    
    data = np.empty(N)
        
    for i in range(N):
        # epsilon greedy
        p = np.random.random()
        if p < eps:
            j = np.random.choice(length)
        else:
            j = np.argmax([a.mean for a in actions])
        
        x = actions[j].choose()
        actions[j].update(x)

        # for the plot
        data[i] = x
    
    cumulative_average = np.cumsum(data) / (np.arange(N) + 1)
    
    print (cumulative_average)
    # plot moving average ctr
    plt.plot(cumulative_average)
    plt.plot(np.ones(N)*m1)
    plt.plot(np.ones(N)*(m2 - 0.1))
    plt.xscale('log')
    plt.title("Epilson : {}".format(eps))
    plt.show()

    # for a in actions:
    #     print(a.mean)

    return cumulative_average


if __name__ == '__main__':
	
    c_e_5 = run_experiment(0.8, 2.2, 0.00001, 100000)
    c_01  = run_experiment(0.8, 2.2, 0.01, 100000)
    c_1   = run_experiment(0.8, 2.2, 0.1, 100000)
    c_5   = run_experiment(0.8, 2.2, 0.5, 100000)
    c_9   = run_experiment(0.8, 2.2, 0.9, 100000)