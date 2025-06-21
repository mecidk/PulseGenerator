import numpy as np
import matplotlib.pyplot as plt

import numpy as np

data_files = [
    # ("06-19-data/data_20250618_120420_Sample=2024_Feb_Argn_YIG_2_5b_b1_Pulse=flat.txt", 120),
    ("06-19-data/data_20250619_122511_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_40MHz_AvgN=3000_MagnetI=-0.0_A.txt", 40),
    ("06-19-data/data_20250619_131701_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_60MHz_AvgN=3000_MagnetI=-0.0_A.txt", 60),
    ("06-19-data/data_20250619_133559_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_80MHz_AvgN=3000_MagnetI=-0.0_A.txt", 80),
    ("06-19-data/data_20250619_135345_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_100MHz_AvgN=3000_MagnetI=-0.0_A.txt", 100),
    ("06-19-data/data_20250619_154502_Sample=2024_Feb_Argn_YIG_2_5b_b1_Pulse=flat.txt", 120),
    ("06-19-data/data_20250619_141151_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_140MHz_AvgN=3000_MagnetI=-0.0_A.txt", 140),
    ("06-19-data/data_20250619_143012_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_160MHz_AvgN=3000_MagnetI=-0.0_A.txt", 160),
    ("06-19-data/data_20250619_162727_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_180.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 180),
    ("06-19-data/data_20250619_164446_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_200.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 200),
    ("06-19-data/data_20250619_170200_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_220.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 220),
    ("06-19-data/data_20250619_171915_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_240.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 240),
    ("06-19-data/data_20250619_173627_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_260.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 260),
    ("06-19-data/data_20250619_175340_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_280.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 280),
    ("06-19-data/data_20250619_181058_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_300.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 300),
    ("06-19-data/data_20250619_182808_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_320.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 320),
    ("06-19-data/data_20250619_184520_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_340.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 340),
    ("06-19-data/data_20250619_190230_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_360.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 360),
    ("06-19-data/data_20250619_191943_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_380.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 380),
    ("06-19-data/data_20250619_193653_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_400.0MHz_AvgN=3000_MagnetI=-0.0_A.txt", 400)
]

new_data_files = [
    ("06-20-data/data_20250620_181345_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_40MHz_AvgN=300_Loopback.txt", 40),
    ("06-20-data/data_20250620_181448_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_60MHz_AvgN=300_Loopback.txt", 60),
    ("06-20-data/data_20250620_181552_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_80MHz_AvgN=300_Loopback.txt", 80),
    ("06-20-data/data_20250620_181654_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_100MHz_AvgN=300_Loopback.txt", 100),
    ("06-20-data/data_20250620_181754_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_120MHz_AvgN=300_Loopback.txt", 120),
    ("06-20-data/data_20250620_181856_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_140MHz_AvgN=300_Loopback.txt", 140),
    ("06-20-data/data_20250620_181958_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_160MHz_AvgN=300_Loopback.txt", 160),
    ("06-20-data/data_20250620_182101_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_180MHz_AvgN=300_Loopback.txt", 180),
    ("06-20-data/data_20250620_182206_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_200MHz_AvgN=300_Loopback.txt", 200),
    ("06-20-data/data_20250620_182309_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_220MHz_AvgN=300_Loopback.txt", 220),
    ("06-20-data/data_20250620_182414_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_240MHz_AvgN=300_Loopback.txt", 240),
    ("06-20-data/data_20250620_182517_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_260MHz_AvgN=300_Loopback.txt", 260),
    ("06-20-data/data_20250620_182618_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_280MHz_AvgN=300_Loopback.txt", 280),
    ("06-20-data/data_20250620_182719_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_300MHz_AvgN=300_Loopback.txt", 300),
    ("06-20-data/data_20250620_182821_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_320MHz_AvgN=300_Loopback.txt", 320),
    ("06-20-data/data_20250620_182927_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_340MHz_AvgN=300_Loopback.txt", 340),
    ("06-20-data/data_20250620_183029_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_360MHz_AvgN=300_Loopback.txt", 360),
    ("06-20-data/data_20250620_183130_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_380MHz_AvgN=300_Loopback.txt", 380),
    ("06-20-data/data_20250620_183232_Sample=2024-Feb-Argn-YIG-2_5b-b1_Pulse=flat_top_400MHz_AvgN=300_Loopback.txt", 400)
]

for file_path, freq in new_data_files:

    data = np.loadtxt(file_path, delimiter=',')

    noise = np.std(data[:-2], axis=0) # calculate the noise of the data, not including the avg row and time row

    noise_segment = noise[346:435] # get to the middle of the noise segment
    
    # calculate some metrics
    noise_var = np.max(noise_segment) - np.min(noise_segment)
    max_min_ratio = (np.max(noise_segment) -  np.min(noise_segment)) / np.min(noise_segment)
    
    print(f"{freq} MHz noise variation: {noise_var:.4f}, "
          f"(max - min)/min percentage: {max_min_ratio * 100:.2f}%")
    
    print(f"one-shot max: {np.max(np.max(data[:-2], axis = 0)):.4f}, ")
    print(f"averaged max: {np.max(data[-2]):.4f}")

data_400 = np.loadtxt(new_data_files[-1][0], delimiter=',')
data_120 = np.loadtxt(new_data_files[4][0], delimiter=',')
data_400_noise = np.std(data_400[:-2], axis=0)
data_120_noise = np.std(data_120[:-2], axis=0)

bigdata = [data_120, data_400]
data_noise = [data_120_noise, data_400_noise]

fig, axs = plt.subplots(1, 2, figsize=(14, 10))
axs = axs.flatten()  # Flatten to easily loop over 1D index

for i in range(2):
    ax1 = axs[i]
    ax2 = ax1.twinx()

    # Replace these with your actual data arrays
    ax1.plot(bigdata[i][-1], bigdata[i][0], label=f"{120 + i*280} MHz", color='tab:blue')
    ax1.set_ylabel("a.u.", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2.plot(bigdata[i][-1], data_noise[i], label=f'{120 + i*280} MHz noise', color='tab:orange')
    ax2.set_ylabel("a.u.", color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    ax2.set_ylim(bottom=-data_noise[i].max())
    ax1.set_xlim(left=25, right=150)
    ax2.set_xlim(left=25, right=150)

    ax1.set_xlabel("ns")
    plt.suptitle("One-shot Noise Analysis")

    # Optional: Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.tight_layout()
plt.show()