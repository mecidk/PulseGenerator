#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 11:13:34 2025

@author: mecid
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

def ReadFromTXT(filename = "readout_20250527_151714.txt"):
    loaded_data = np.loadtxt(filename, delimiter=",")
    return loaded_data

test = ReadFromTXT()

print(test)
raw = test[0]

print(raw.shape)

signal= np.concatenate(( raw[:200], raw[200:1300], raw[:200], raw[200:1300] , raw[2600:]))
print(signal.shape)

abs_signal = np.abs(signal)

# Step 2: Smooth to get envelope (simple moving average)
window_size = 20
kernel = np.ones(window_size) / window_size
smoothed = np.convolve(abs_signal, kernel, mode='same')

# Step 3: Threshold
threshold = 0.01 * np.max(smoothed)
above = smoothed > threshold

# Step 4: Detect rising and falling edges
edges = np.diff(above.astype(int))
starts = np.where(edges == 1)[0] + 1
ends = np.where(edges == -1)[0] + 1
print(starts)
print(ends)

# Step 5: Match starts to ends and calculate widths
pulse_widths = []
pulse_positions = []

for s in starts:
    for e in ends:
        if e > s:
            endpoint_pair = [s, e]
            pulse_positions.append(endpoint_pair)
            width = (test[1][e] - test[1][s]) * 1e3
            pulse_widths.append(width)
            break

for i in range(len(pulse_widths)):
    print(f"Pulse detected: starts at {pulse_positions[i][0]} ns, ends at {pulse_positions[i][1]} ns, has the width {pulse_widths[i]} ns")

pulse_positions = np.array(pulse_positions)
pulse_widths = np.array(pulse_widths)

print(pulse_positions)
print(pulse_widths)

# # Plotting
# fig, axs = plt.subplots(1, 1)

# # Subplot 1: Full signal
# axs.plot(signal, label='Original signal')
# axs.plot(smoothed, label='Smoothed envelope', alpha=0.7)
# axs.axhline(threshold, color='gray', linestyle='--', label='Threshold')
# for s, e in zip(matched_starts, matched_ends):
#     axs.axvline(s, color='red', linestyle='--')
#     axs.axvline(e, color='green', linestyle='--')
# axs.set_title(f'Detected {len(pulse_widths)} pulses')
# axs.legend()
# axs.set_ylabel('Amplitude')

# plt.tight_layout()
# plt.show()
