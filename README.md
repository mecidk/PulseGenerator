# PulseGenerator

A pulse generator for RFSoC4x2 board using QICK with raw data acquisition capabilities.

*Developed in/for Hoffmann Group @ UIUC*

main.py: orchestrator code to be run on a regular computer

server.py: small API server running inside the board, calling main_pulser

main_pulser.py: real pulse-sending code running inside the board

magnet_lib.py: library for controlling the magnet power supply

sc5511a_lib.py: library for controlling the RF generator