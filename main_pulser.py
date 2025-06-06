# forked from QIS Summer School 2024, courtesy of QICK team, especially Sho Uemura

import sys
import json

from qick import *
from qick_training import *
from RBSupport import generate_2qgateset

import numpy as np
import matplotlib.pyplot as plt

soc = QickSoc()
soccfg = soc

class PulseSequence(AveragerProgram):
    def initialize_phases(self):
        ## Prepare state
        self.phase_ref_q1 = 0
        self.phase_ref_q2 = 0
        self.phase_ref_c = 0
    
    def play_seq(self, seq):
        for g in seq:
            for q in g:
                if q == "Q2":
                    ginfo=self.cfg["gate_set"][g[q]]
                    if g[q]=="Z":
                        self.phase_ref_q2+=180
                    elif g[q]=="Z/2":
                        self.phase_ref_q2+=90
                    elif g[q]=="-Z/2":
                        self.phase_ref_q2+=-90
                    else:
                        self.set_pulse_registers(ch=self.cfg["q2_ch"], freq=self.freq_q2,
                                                 phase=self.deg2reg(self.phase_ref_q2 + ginfo["phase"], gen_ch=self.cfg["q2_ch"]),
                                                 gain=ginfo["gain"], waveform=g[q], phrst = 1,mode="oneshot")
                        self.pulse(ch=self.cfg["q2_ch"])
                if q == "Q1": # Qubit 1
                    ginfo=self.cfg["gate_set"][g[q]]
                    """For the Z gates (virtual rotation), we need to advance the phase of all the pulses which follows afterwards"""
                    if g[q]=="Z":
                        self.phase_ref_q1+=180
                    elif g[q]=="Z/2":
                        self.phase_ref_q1+=90
                    elif g[q]=="-Z/2":
                        self.phase_ref_q1+=-90
                    else:
                        self.set_pulse_registers(ch=self.cfg["q1_ch"], freq=self.freq_q1,
                                                 phase=self.deg2reg(self.phase_ref_q1 + ginfo["phase"], gen_ch=self.cfg["q1_ch"]),
                                                 gain=ginfo["gain"], waveform=g[q], phrst = 1,mode="oneshot")
                        self.pulse(ch=self.cfg["q1_ch"])
            ################
           #modified sync_all with only DAC clocks, no ADC clocks
            self.synci(self.us2cycles(0.01))
    
    def initialize(self):
        cfg = self.cfg
        self.gate_seq = cfg['gate_seq']
        self.gate_set = cfg['gate_set']

        # set the nyquist zone
        self.declare_gen(ch=cfg["q1_ch"], nqz=1)
        self.declare_gen(ch=cfg["q2_ch"], nqz=1)

        # declare readout channels
        self.declare_readout(ch=0, freq=cfg['q0_read_freq'], length=cfg['readout_length'], sel='input')
        self.declare_readout(ch=1, freq=cfg['q1_read_freq'], length=cfg['readout_length'], sel='input')

        # convert frequency to DAC frequency (ensuring it is an available ADC frequency)
        self.freq_q1 = self.freq2reg(cfg["q1_pulse_freq"], gen_ch=cfg["q1_ch"], ro_ch=cfg["q1_ro_ch"])
        self.freq_q2 = self.freq2reg(cfg["q2_pulse_freq"], gen_ch=cfg["q2_ch"], ro_ch=cfg["q2_ro_ch"])

        for name, ginfo in self.gate_set.items():
            self.add_pulse(ch=cfg["q1_ch"], name=name,
                           idata=ginfo["idata"],
                           qdata=ginfo["qdata"],
                          )
            self.add_pulse(ch=cfg["q2_ch"], name=name,
                           idata=ginfo["idata"],
                           qdata=ginfo["qdata"],
                          )

        self.default_pulse_registers(ch=cfg["q1_ch"], style="arb")
        self.default_pulse_registers(ch=cfg["q2_ch"], style="arb")

        self.synci(500)  # give processor some time to configure pulses
        self.trigger(ddr4=True, mr=True, adc_trig_offset=self.cfg["adc_trig_offset"])
        self.synci(500) # give processor some time to configure pulses

    def body(self):
        # Trigger measurement
        self.trigger(adcs=self.ro_chs,
                     pins=[0],
                     adc_trig_offset=self.cfg["adc_trig_offset"])

        self.initialize_phases()
        self.play_seq(self.gate_seq)
        self.wait_all()
        self.sync_all(self.us2cycles(self.cfg["relax_delay"]))

def GeneratePulse(freq = 1000, width = 10, pulse_count = 1, trig_delay = 1, no_of_expt = 1, channel = 0):
    # transfer the input parameters to local variables
    q1_pulse_freq = freq 
    q1_read_freq = freq
    q2_pulse_freq = freq 
    q2_read_freq = freq
    pi_sigma_width = width * 1e-3
    
    # set up the config, which is the main argument for QICK programs
    config = {"q1_ch": 0,  # --Fixed
              "q2_ch": 1,
              "q1_ro_ch": 0,
              "q2_ro_ch": 1,
              "ro_chs": [0,1],
              "reps": 1,  # --Fixed
              "relax_delay": 1.0,  # --us
              "res_phase": 0,  # --degrees
              "pulse_style": "arb",  # --Fixed
              "pi_sigma": soc.us2cycles(pi_sigma_width, gen_ch=0),
              "readout_length": soc.us2cycles(1, ro_ch=0),  # [Clock ticks]
              "pi_gain": 30000,  # [DAC units]
              "pi_2_gain": 15000,
              "q1_pulse_freq": q1_pulse_freq,  # [MHz]
              "q2_pulse_freq": q2_pulse_freq,  # [MHz]
              "q1_read_freq": q1_read_freq,
              "q2_read_freq": q2_read_freq,
              "adc_trig_offset": soc.us2cycles(trig_delay, ro_ch=0),  # [Clock ticks] # 0.1 wokred
              "soft_avgs": 1,
              "expts": 1
              }
    config["gate_set"] = generate_2qgateset(config)
    
    # get the desired sequence of gates (pi pulses). for now, only X gates are applied.
    sequence = []
    for _ in range(0, pulse_count):
        sequence.append({'Q1': 'X', 'Q2': 'X'})
    config['gate_seq'] = sequence

    prog = PulseSequence(soccfg, config) # initiate the pulse program which does everything
    
    readout = []
    
    for _ in range(no_of_expt):
        soc.reset_gens() # clear out any DC or periodic values from the generator channels

        soc.arm_mr(ch = channel) # arm (get ready) the MR buffer

        prog.config_all(soc) # send the config to the FPGA

        soc.tproc.start() # start the main process, which runs everything

        readout.append(soc.get_mr()) # read from the MR buffer
    
    return np.array(readout)

def main():
    
    # get the data from the server.py call
    data = json.load(sys.stdin)
    frequency = data.get("freq")
    pulsewidth = data.get("width") # in ns
    pulse_count = data.get("pulse_count")
    trigger_delay = data.get("trigger_delay")
    number_of_expt = data.get("number_of_expt")
    channel = data.get("channel")
    
    readout = GeneratePulse(frequency, pulsewidth, pulse_count, trigger_delay, number_of_expt, channel) # execute the main function
    
    time_row = (soc.cycles2us(np.arange(0, len(readout[0][:, 0])), ro_ch = channel) / 8)  # create the timestamps for each sample,
                                                                                    # divide by 8 is due to ADC ticks being 8
                                                                                    # times slower than the real clock cycles
            
    time_row = time_row + time_row[8] # since get_mr() function deletes the first 8 samples of the ADC (they are junk from
                                      # previous reads), we add that lost time back.
    
    # create the response
    result = {
        "array": np.vstack((readout[:, :, 0], time_row)).tolist()
    }
    
    json.dump(result, sys.stdout) # send the response to the handler (server.py)

if __name__ == "__main__":
    main()