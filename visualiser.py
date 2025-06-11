import numpy as np
import matplotlib.pyplot as plt

frequency_0 = np.loadtxt('06-10-data/data_20250610_152754.txt', delimiter=',')
frequency_5 = np.loadtxt('06-10-data/data_20250610_153508.txt', delimiter=',')
frequency_10 = np.loadtxt('06-10-data/data_20250610_154013.txt', delimiter=',')
frequency_15= np.loadtxt('06-10-data/data_20250610_154451.txt', delimiter=',')
frequency_20 = np.loadtxt('06-10-data/data_20250610_154920.txt', delimiter=',')
frequency_25 = np.loadtxt('06-10-data/data_20250610_155443.txt', delimiter=',')

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

field_0 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0_A.txt', delimiter=',')
field_2 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0002_A.txt', delimiter=',')
field_4 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0004_A.txt', delimiter=',')
field_6 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0006_A.txt', delimiter=',')
field_8 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0008_A.txt', delimiter=',')
field_10 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.001_A.txt', delimiter=',')
field_12 = np.loadtxt('06-11-data/data_20250611_151505_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=120MHz_AvgN=1000_MagnetI=-3.0012_A.txt', delimiter=',')

field_sweep = np.vstack((field_0[-2], field_2[-2], field_4[-2], field_6[-2], field_8[-2], field_10[-2], field_12[-2]))

def PlotFieldSweep(data):
    plt.figure(figsize=(10, 6))

colors = plt.cm.rainbow(np.linspace(0, 1, 7))  # 7 colors

for i, (field, color) in enumerate(zip([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], colors)):
    plt.plot(field_0[-1], field_sweep[i, :], label=f'3.000 A + {field} mA', color=color)
    
plt.title('Field Sweep')
plt.xlabel('ns')
plt.ylabel('a.u.')
plt.legend()
plt.grid()
plt.show()

if __name__ == "__main__":
    # PlotFrequencySweep(frequency_sweep)
    PlotFieldSweep(field_sweep)