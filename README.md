# PulseGenerator

A pulse generator for RFSoC4x2 board using QICK with raw data acquisition capabilities.

*Developed in/for Hoffmann Group @ UIUC with Dr. Jinho Lim*

main.py: orchestrator code to be run on a regular computer

server.py: small API server running inside the board, calling main_pulser

main_pulser.py: real pulse-sending code running inside the board, using raw acquisition

main_pulser_decimated.py: real pulse-sending code running inside the board, using downconverted decimated acquisition

plotter.py: small GUI application for plotting exported .txt files

magnet_lib.py: library for controlling the magnet power supply

sc5511a_lib.py: library for controlling the SignalCore SC5511A RF generator

bnc855b_lib.py: library for controlling the BNC 855B RF generator