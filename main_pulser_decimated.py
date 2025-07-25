# forked from QIS Summer School 2024, courtesy of QICK team, especially Sho Uemura

import sys
import json
import gc
import time

from qick import * # type: ignore
from drivers.qick_training import * # type: ignore
from drivers.RBSupport import generate_2qgateset # type: ignore

import numpy as np
import matplotlib.pyplot as plt

soc = QickSoc() # type: ignore
soccfg = soc

class PulseSequence(AveragerProgram): # type: ignore
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

                    if self.cfg["pulse_style"] == "flat_top":
                        self.set_pulse_registers(ch=self.cfg["q2_ch"], freq=self.freq_q2,
                                                    phase=self.deg2reg(self.phase_ref_q2 + ginfo["phase"],
                                                    gen_ch=self.cfg["q2_ch"]), gain=ginfo["gain"], 
                                                    waveform=g[q], phrst = 0,
                                                    length = self.cfg["length"])
                    elif self.cfg["pulse_style"] == "const":
                        self.set_pulse_registers(ch=self.cfg["q2_ch"], freq=self.freq_q2,
                                                    phase=self.deg2reg(self.phase_ref_q2 + ginfo["phase"],
                                                    gen_ch=self.cfg["q2_ch"]), gain=ginfo["gain"], 
                                                    phrst = 0, mode="oneshot",
                                                    length = self.cfg["length"])
                    else:
                        self.set_pulse_registers(ch=self.cfg["q2_ch"], freq=self.freq_q2,
                                                    phase=self.deg2reg(self.phase_ref_q2 + ginfo["phase"],
                                                    gen_ch=self.cfg["q2_ch"]), gain=ginfo["gain"], 
                                                    waveform=g[q], phrst = 0, mode="oneshot")
                    self.pulse(ch=self.cfg["q2_ch"])

                if q == "Q1": # Qubit 1
                    ginfo=self.cfg["gate_set"][g[q]]

                    if self.cfg["pulse_style"] == "flat_top":
                        self.set_pulse_registers(ch=self.cfg["q1_ch"], freq=self.freq_q1,
                                                    phase=self.deg2reg(self.phase_ref_q1 + ginfo["phase"],
                                                    gen_ch=self.cfg["q1_ch"]), gain=ginfo["gain"], 
                                                    waveform=g[q], phrst = 0,
                                                    length = self.cfg["length"])
                    elif self.cfg["pulse_style"] == "const":
                        self.set_pulse_registers(ch=self.cfg["q1_ch"], freq=self.freq_q1,
                                                    phase=self.deg2reg(self.phase_ref_q1 + ginfo["phase"],
                                                    gen_ch=self.cfg["q1_ch"]), gain=ginfo["gain"], 
                                                    phrst = 0, mode="oneshot",
                                                    length = self.cfg["length"])
                    else:
                        self.set_pulse_registers(ch=self.cfg["q1_ch"], freq=self.freq_q1,
                                                 phase=self.deg2reg(self.phase_ref_q1 + ginfo["phase"],
                                                 gen_ch=self.cfg["q1_ch"]), gain=ginfo["gain"], 
                                                 waveform=g[q], phrst = 0, mode="oneshot")

                    self.pulse(ch=self.cfg["q1_ch"])
            ################
           #modified sync_all with only DAC clocks, no ADC clocks
            self.synci(self.us2cycles(0.01))
    
    def initialize(self):
        cfg = self.cfg
        self.gate_seq = cfg['gate_seq']
        self.gate_set = cfg['gate_set']

        # set the nyquist zone
        if cfg['q1_pulse_freq'] > 4800:
            self.declare_gen(ch=cfg["q1_ch"], nqz=2)
        else:
            self.declare_gen(ch=cfg["q1_ch"], nqz=1)

        if cfg['q2_pulse_freq'] > 4800:
            self.declare_gen(ch=cfg["q2_ch"], nqz=2)
        else:
            self.declare_gen(ch=cfg["q2_ch"], nqz=1)

        # declare readout channels
        for ch in cfg["ro_chs"]:
            self.declare_readout(ch=ch, length=cfg["readout_length"],
                                 freq=cfg["q" + str(ch + 1) +"_read_freq"], 
                                 gen_ch=cfg["q" + str(ch + 1) +"_ch"])

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

        if cfg["pulse_style"] == "flat_top":
            # set the pulse style to flat top
            self.default_pulse_registers(ch=cfg["q1_ch"], style="flat_top")
            self.default_pulse_registers(ch=cfg["q2_ch"], style="flat_top")
        elif cfg["pulse_style"] == "const":
            # set the pulse style to constant
            self.default_pulse_registers(ch=cfg["q1_ch"], style="const")
            self.default_pulse_registers(ch=cfg["q2_ch"], style="const")
        else:
            # set the pulse style to arbitrary, gaussian in our case
            self.default_pulse_registers(ch=cfg["q1_ch"], style="arb")
            self.default_pulse_registers(ch=cfg["q2_ch"], style="arb")

        self.synci(1000)  # give processor some time to configure pulses

    def body(self):
        # Trigger measurement
        self.trigger(adcs=self.ro_chs,
                     pins=[0],
                     adc_trig_offset=self.cfg["adc_trig_offset"])

        self.initialize_phases()
        self.play_seq(self.gate_seq)
        self.wait_all()
        self.sync_all(self.us2cycles(self.cfg["relax_delay"]))

def main():
    
    # get the data from the server.py call
    data = json.load(sys.stdin)
    pulse_type = data.get("type")
    pulse_frequency = data.get("freq")
    pulse_width = data.get("width") # in ns
    pulse_amplitude = data.get("amplitude") # in DAC units
    pulse_count = data.get("pulse_count")
    trigger_delay = data.get("trigger_delay")
    number_of_expt = data.get("number_of_expt")
    max_batch_size = data.get("max_batch_size", 1000) # default is 1000
    read_freq = data.get("read_freq")

    # safety checks for the input parameters
    if max_batch_size <= 0 or max_batch_size > 3000:
        max_batch_size = 1000
    if pulse_type not in ["gaussian", "flat_top", "const"]:
        pulse_type = "gaussian"
    if pulse_frequency < 0 or pulse_frequency > 9800:
        pulse_frequency = 100
    if pulse_amplitude < 0 or pulse_amplitude > 32767:
        pulse_amplitude = 30000
    if pulse_width < 0 or pulse_width > 50:
        pulse_width = 10

    q1_pulse_freq = pulse_frequency
    q1_read_freq = read_freq
    q2_pulse_freq = pulse_frequency
    q2_read_freq = pulse_frequency
    pi_sigma_width = pulse_width * 1e-3

    # set up the config which is the main argument for QICK programs (default is for gaussian pulses)
    config = {"q1_ch": 0,
              "q2_ch": 1,
              "q1_ro_ch": 0,
              "q2_ro_ch": 1,
              "ro_chs": [0,1],
              "reps": 1,
              "relax_delay": 1.0,  # in us
              "res_phase": 0,  # in degrees
              "pulse_style": "arb",  # gaussian is actually called "arb" in QICK
              "length": soc.us2cycles(pi_sigma_width, gen_ch=0) * 4, # factor of 4 is since the length parameter does not work with standard deviation, but with the full width of the pulse
              "pi_sigma": soc.us2cycles(pi_sigma_width, gen_ch=0), # standard deviation of the pulse in cycles
              "readout_length": soc.us2cycles(1, ro_ch=0), # in cycles
              "pi_gain": pulse_amplitude, # in DAC units
              "pi_2_gain": pulse_amplitude,
              "q1_pulse_freq": q1_pulse_freq, # in MHz
              "q2_pulse_freq": q2_pulse_freq, # in MHz
              "q1_read_freq": q1_read_freq,
              "q2_read_freq": q2_read_freq,
              "adc_trig_offset": soc.us2cycles(trigger_delay, ro_ch=0), # delay for the ADC trigger in cycles
              "soft_avgs": 1,
              "expts": 1
              }
    
    # edit the config if the pulse type is flat_top or constant
    if pulse_type == "flat_top":
        config["pulse_style"] = "flat_top"
        config["pi_sigma"] = 3  # shortest possible transition time for flat top pulse
    elif pulse_type == "const":
        config["pulse_style"] = "const"
      
    config["gate_set"] = generate_2qgateset(config)

    # get the desired sequence of gates (pi pulses). for now, only X gates are applied.
    config['gate_seq'] = [{'Q1': 'X', 'Q2': 'X'}] * pulse_count

    prog = PulseSequence(soccfg, config) # initiate the pulse program which does everything

    # acquire a single shot to define time row
    soc.reset_gens() # clear out any DC or periodic values from the generator channels
    iq_sample = prog.acquire_decimated(soc, load_pulses=True, progress=False)
    time_row = soc.cycles2us(np.arange(0, len(iq_sample[0, 0])), ro_ch=0)

    # do the measurement in batches to avoid memory issues
    print("[", flush=True)

    for i in range(0, number_of_expt, max_batch_size):
        this_batch = min(max_batch_size, number_of_expt - i)

        ch0_I = []
        ch0_Q = []
        ch1_I = []
        ch1_Q = []

        for _ in range(this_batch):
            soc.reset_gens()
            iq = prog.acquire_decimated(soc, load_pulses=False, progress=False)
            ch0_I.append(iq[0, 0].tolist())
            ch0_Q.append(iq[0, 1].tolist())
            ch1_I.append(iq[1, 0].tolist())
            ch1_Q.append(iq[1, 1].tolist())

        batch_result = {
            "batch_index": i // max_batch_size,
            "ch0_I": ch0_I,
            "ch0_Q": ch0_Q,
            "ch1_I": ch1_I,
            "ch1_Q": ch1_Q,
            "time_row": time_row.tolist() if i == 0 else None
        }

        json.dump(batch_result, sys.stdout)
        print("", flush=True)

        # clean up to avoid memory issues
        del ch0_I, ch0_Q, ch1_I, ch1_Q, iq
        gc.collect()
        time.sleep(0.1)

    print("]", flush=True)

if __name__ == "__main__":
    main()