# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 12:25:46 2022

@author: Jonathan Gibbons
@editor: Tzu-Hsiang Lo, Jinho Lim
"""

import pyvisa # type: ignore
from pyvisa.constants import StopBits, Parity # type: ignore
import numpy
import time

class signalGenerator865:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.sigGen = self.rm.open_resource('USB0::0x03EB::0xAFFF::4F1-3B4E00014-1587::INSTR')
        self.sigGen.read_termination = '\n'
        self.sigGen.write_termination = '\n'
        print(self.sigGen.query('*IDN?'))
        
    def query(self):
        print(self.sigGen.query('*IDN?'))
           
    def amplMod(self,depth): # page 46
        self.sigGen.write("SOURce:AM:DEPTh " + str(depth))
        self.sigGen.write("SOURce:AM:SOURce EXTernal")
        self.sigGen.write("SOURce:AM:STATe ON")
        
    def power(self,power): # page 29
        self.sigGen.write("SOURce:POWer:AMPLitude " + str(power))
        
    def outputon(self):
        self.sigGen.write(":OUTPut" + str(1) + ":STATe ON")
        print('output is: ' + self.sigGen.query(":OUTPut" + str(1) + ":STATe?"))

    def outputoff(self):
        self.sigGen.write(":OUTPut" + str(1) + ":STATe OFF")
        print('output is: ' + self.sigGen.query(":OUTPut" + str(1) + ":STATe?"))
              
    def freq(self,freqval=10): # page 29
        freqapp = freqval*1000000000 # in GHz
        self.sigGen.write('SOURce:FREQuency:CW ' + str(freqapp))
    
        
class signalGenerator855B:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.sigGen = self.rm.open_resource('USB0::0x03EB::0xAFFF::6E5-0B4L20014-0981::INSTR')
        self.sigGen.read_termination = '\n'
        self.sigGen.write_termination = '\n'
        print(self.rm.list_resources())
        
    def query(self):
        print(self.sigGen.query('*IDN?'))
        
    def freq(self, ch, freqval): # page 29
        freqapp = freqval*1000000000 # in GHz
        self.sigGen.write("SOURce" + str(ch) + ":FREQuency:CW " + str(freqapp))
        freq = float(self.sigGen.query("SOURce" + str(ch) + ":FREQuency:CW?"))/10**9
        print(str(freq) + " GHz")
        
    def freqQuery(self, ch):
        freq = float(self.sigGen.query("SOURce" + str(ch) + ":FREQuency:CW?"))/10**9
        print(str(freq) + " GHz")           
        
    def amplMod(self, ch, depth, mod_freq): # page 60, ch = 1 or 2
        # This signal generator has only internal modulation. DO NOT WRITE INTERNAL MODE.
        self.sigGen.write(":SOURce" + str(ch) + ":AM:SOURce INTernal")
        self.sigGen.write(":SOURce" + str(ch) + ":AM:DEPT " + str(depth))
        print('modulation depth = ' + self.sigGen.query(":SOURce" + str(ch) + ":AM:DEPTh?"))
        self.sigGen.write(":SOURce" + str(ch) + ":AM:INTernal:FREQuency " + str(mod_freq))
        print('modulation frequency = ' + self.sigGen.query(":SOURce" + str(ch) + ":AM:INTernal:FREQuency?"))
    
    def amplModOn(self, ch):
        self.sigGen.write(":SOURce" + str(ch) + ":AM:STATe ON")
        print("internal mod is " + self.sigGen.query(":SOURce" + str(ch) + ":AM:STATe?"))
        
    def amplModOff(self, ch):
        self.sigGen.write(":SOURce" + str(ch) + ":AM:STATe OFF")
        print('internal mod is ' + self.sigGen.query(":SOURce" + str(ch) + ":AM:STATe?"))        
    
    def amplModQuery(self, ch):
        print('internal mod is ' + self.sigGen.query(":SOURce" + str(ch) + ":AM:STATe?"))
        depth = float(self.sigGen.query(":SOURce" + str(ch) + ":AM:DEPTh?"))
        print('depth = ' + str(depth))
        modFreq = float(self.sigGen.query(":SOURce" + str(ch) + ":AM:INTernal:FREQuency?"))
        print('modulation frequency = ' + str(modFreq) + 'Hz')
        
    def power(self, ch, power): # page 29
        self.sigGen.write(":SOURce" + str(ch) + ":POWer:AMPLitude " + str(power))
        print(str(self.sigGen.query(":SOURce" + str(ch) + ":POWer:AMPLitude?")) + 'dBm')
              
    def powerQuery(self, ch): # page 29
        power = float(self.sigGen.query(":SOURce" + str(ch) + ":POWer:AMPLitude?"))
        print(str(power) + " dBm")
    
    def outPutOn(self, ch):
        self.sigGen.write(":OUTPut" + str(ch) + ":STATe ON")
        print('output is: ' + self.sigGen.query(":OUTPut" + str(ch) + ":STATe?"))
        
    def outPutOff(self, ch):
        self.sigGen.write(":OUTPut" + str(ch) + ":STATe OFF")
        print('output is: ' + self.sigGen.query(":OUTPut" + str(ch) + ":STATe?"))
    
    def outPutQuery(self, ch):
        print(self.sigGen.query(":OUTPut" + str(ch) + ":STATe?"))
        


       
        
        

'''
class SignalGenerator845:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.sigGen = self.rm.open_resource('USB0::0x03EB::0xAFFF::421-43A6D0610-1452::INSTR')
        self.sigGen.read_termination = '\n'
        self.sigGen.write_termination = '\n'
        print(self.rm.list_resources())
        
    def query(self):
        print(self.sigGen.query('*IDN?'))
           
    def amplMod(self,depth): # page 46
        self.sigGen.write("SOURce:AM:DEPTh " + str(depth))
        self.sigGen.write("SOURce:AM:SOURce EXTernal")
        self.sigGen.write("SOURce:AM:STATe ON")
        
    def power(self,power): # page 29
        self.sigGen.write("SOURce:POWer:AMPLitude " + str(power))
        
    def outputon(self):
        self.sigGen.write("OUTP:ON")
       
    def freq(self,freqval=10): # page 29
        freqapp = freqval*1000000000 # in GHz
        self.sigGen.write('SOURce:FREQuency:CW ' + str(freqapp))
'''