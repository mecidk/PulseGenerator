import numpy as np
import matplotlib.pyplot as plt

frequency_0 = np.loadtxt('0610-data/data_20250610_152754.txt', delimiter=',')
frequency_5 = np.loadtxt('0610-data/data_20250610_153508.txt', delimiter=',')
frequency_10 = np.loadtxt('0610-data/data_20250610_154013.txt', delimiter=',')
frequency_15= np.loadtxt('0610-data/data_20250610_154451.txt', delimiter=',')
frequency_20 = np.loadtxt('0610-data/data_20250610_154920.txt', delimiter=',')
frequency_25 = np.loadtxt('0610-data/data_20250610_155443.txt', delimiter=',')

frequency_sweep = np.vstack((frequency_0[-2], frequency_5[-2], frequency_10[-2], frequency_15[-2], frequency_20[-2], frequency_25[-2]))

def PlotFrequencySweep(data):
    plt.figure(figsize = (10, 6))

    for i, freq in enumerate([0, 5, 10, 15, 20, 25]):
        plt.plot(frequency_0[-1], data[i, :], label=f'5.263 GHz + {freq} MHz')
    
    plt.title('Frequency Sweep')
    plt.xlabel('ns')
    plt.ylabel('a.u.')
    plt.legend()
    plt.grid()
    plt.show()

field_0 = np.loadtxt('0610-data/data_20250610_160420.txt', delimiter=',')
field_4 = np.loadtxt('0610-data/data_20250610_161211.txt', delimiter=',')
field_8 = np.loadtxt('0610-data/data_20250610_161718.txt', delimiter=',')
field_12 = np.loadtxt('0610-data/data_20250610_162130.txt', delimiter=',')
field_16 = np.loadtxt('0610-data/data_20250610_162553.txt', delimiter=',')
field_20 = np.loadtxt('0610-data/data_20250610_163041.txt', delimiter=',')

field_sweep = np.vstack((field_0[-2], field_4[-2], field_8[-2], field_12[-2], field_16[-2], field_20[-2]))

def PlotFieldSweep(data):
    plt.figure(figsize=(10, 6))

    for i, field in enumerate([0, 4, 8, 12, 16, 20]):
        plt.plot(field_0[-1], data[i, :], label=f'3.000 A + {field} mA')
    
    plt.title('Field Sweep')
    plt.xlabel('ns')
    plt.ylabel('a.u.')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    PlotFrequencySweep(frequency_sweep)
    PlotFieldSweep(field_sweep)