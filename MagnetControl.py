import pyvisa # type: ignore
import time

class Kepco:

    def __init__(self,GPIBchan=1):
        self.kepco_gpib = int(GPIBchan)
        self.rm = pyvisa.ResourceManager()
        print(self.rm.list_resources())

    def kepinit(self):
        # Definining termination characters ('\n') is important for this instrument!
        self.kepco_inst = self.rm.open_resource('GPIB0::{gpib_add}::INSTR'.format(gpib_add=self.kepco_gpib), read_termination='\n', write_termination='\n') # Kepco Power Supply has GPIB address 1
   
        self.kepco_inst.write("*rst; status:preset; *cls")    
        print(self.kepco_inst.query("*IDN?"))
        print("Initialization of Kepco Power Supply was successful.")

        #Sets the range to full
        self.kepco_inst.write("CURR:RANG 1")
        self.kepco_inst.write("VOLT:RANG 1")
   
    def mode_voltage(self):
        self.kepco_inst.write("VOLT 0")
        self.voltmode = 1
        self.currmode = 0
        self.kepco_inst.write("FUNC:MODE VOLT")
        self.kepco_inst.write("CURR 20")
                   
    def mode_current(self):
        self.kepco_inst.write("CURR 0")
        self.currmode = 1
        self.voltmode = 0
        self.kepco_inst.write("FUNC:MODE CURR")  
        self.kepco_inst.write("VOLT 20")
   
    def set_voltage(self,voltage):
        self.kepco_voltage = float(voltage)
        if abs(self.kepco_voltage) <= 20:
            self.kepco_inst.write("VOLT {volt}".format(volt=self.kepco_voltage))
        else:
            self.kepco_voltage = 0
            self.kepco_inst.write("VOLT {volt}".format(volt=0))
            print("Maximum voltage value is +/- 20 V. Voltage is being set to 0.")
        print("Set voltage to {volt} V".format(volt=self.kepco_voltage))
   
    def set_current(self,current):
        self.kepco_current = float(current)
        if abs(self.kepco_current) <= 20:
            self.kepco_inst.write("CURR {curr}".format(curr=self.kepco_current))
        else:
            self.kepco_current = 0
            self.kepco_inst.write("CURR {curr}".format(curr=0))
            print("Maximum current value is +/- 20 A. Current is being set to 0.")
        print("set current to {amps} A".format(amps=self.kepco_current))
        
        
    def get_current(self):
        curr = self.kepco_inst.query("CURR?")
        return curr

    def power_on(self):
        self.kepco_inst.write("OUTP ON")
       
    def power_off(self):
        self.kepco_inst.write("OUTP OFF")
        if self.currmode == 1:
            self.kepco_inst.write("CURR 0")
        if self.voltmode == 1:
            self.kepco_inst.write("VOLT 0")
   
    def ramp_current(self, I1, I2, dI, dT):
        """
        This function ramps the current from I1 to I2 with a step size of dI and a delay of dT seconds between steps.
        It takes initial current I1 (A), final current I2 (A), step size dI (A), and delay dT (sec) as parameters.
        """

        self.kepinit()
        self.mode_current()
        self.power_on()
        current = I1

        # set the direction of sweep
        if I2 >= I1:
            condition = lambda c: c <= I2
            step = abs(dI)
        else:
            condition = lambda c: c >= I2
            step = -abs(dI)

        while condition(current):
            self.set_current(current)
            if current == I1:
                time.sleep(3)
            time.sleep(dT)
            current += step

        # ensure the final current value I2 is set if not exactly on the last step.
        if (step > 0 and current - step < I2) or (step < 0 and current - step > I2):
            self.set_current(I2)

        time.sleep(dT)