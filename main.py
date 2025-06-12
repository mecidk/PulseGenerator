import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import iirnotch, filtfilt, welch
import time
from magnet_lib import Kepco
from sc5511a_lib import SC5511A

def PlotReadout(read, time_row, filename, no_of_experiments, batch_number):
    
    """
    This function plots the response. It takes the response array, which is just (raw values, time) stack
    and the current timestamp to save the figure. It doesn't return anything.
    """
    
    plt.figure()
    plt.plot(time_row, read) # take the time row and the average row to plot
    plt.xlabel("ns")
    plt.ylabel("a.u.")
    plt.tight_layout()

    # this is just for naming the files properly, total average or batch average
    if batch_number == 9999:
        plt.title(f"Readout, Averaged over {no_of_experiments} experiments, Grand Average")
        plt.savefig("data/plot_" + filename + ".png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"Readout, Averaged over {no_of_experiments} experiments, Batch {batch_number}")
        plt.savefig("data/plot_" + filename + f"_Batch_{batch_number}.png", dpi=300, bbox_inches='tight')

    # plt.show()
    plt.close()

def PlotPSD(data, filename, fs, no_of_experiments, batch_number):

    """
    This function plots the Power Spectral Density (PSD) of the data using Welch's method.
    It takes the data, the current timestamp, the sampling frequency, and the number of experiments.
    """

    fft_freqs, psd = welch(data, fs * 1e-6, return_onesided=True, detrend=False, nperseg=512)
    plt.figure()
    plt.semilogy(fft_freqs, psd)
    plt.xlabel("absolute frequency (MHz)")
    plt.ylabel("power (a.u.)")
    plt.tight_layout()

    # this is just for naming the files properly, total average or batch average
    if batch_number == 9999:
        plt.title(f"PSD, Averaged over {no_of_experiments} experiments, Grand Average")
        plt.savefig("data/PSD_" + filename + ".png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"PSD, Averaged over {no_of_experiments} experiments, Batch {batch_number}")
        plt.savefig("data/PSD_" + filename + f"_Batch_{batch_number}.png", dpi=300, bbox_inches='tight')
    
    # plt.show()
    plt.close()

def CalculateSNR(signal):

    """
    This function calculates the Signal-to-Noise Ratio (SNR) of the signal.
    It takes the signal as input and returns the SNR in both linear and dB scale.
    The SNR is calculated by taking the maximum amplitude of the pulse region and
    dividing it by the standard deviation of the noise region.
    """

    pulse_region = signal[950:1390]
    signal_amplitude = np.max(pulse_region) - np.min(pulse_region)

    noise_region = signal[1540:]
    noise_amplitude = np.std(noise_region)

    snr = signal_amplitude / noise_amplitude
    snr_dB = 20 * np.log10(snr)

    return snr, snr_dB

def WriteToTXT(myarray, filename, timestamp, sample, payload, number_of_experiments, magnet_current, LO_frequency,  LO_power, note):
    
    """
    This function writes the data to a .txt file with a header containing metadata about the experiment.
    """

    if not isinstance(myarray, np.ndarray):
        raise TypeError("Input must be a numpy array")
    
    # add header to the file
    file = open("data/data_" + filename + ".txt", "w")
    file.write(f"# Date and Time: {timestamp} #\n")
    file.write(f"# Sample: {sample} #\n")
    file.write(f"# Pulse Frequency and Width: {payload['freq']} MHz, {payload['width'] * 4} ns #\n")
    file.write(f"# LO Frequency and Power: {LO_frequency} GHz, {LO_power} dBm #\n")
    file.write(f"# Number of Experiments: {number_of_experiments} #\n")
    file.write(f"# Magnet Current: {magnet_current} A #\n")
    file.write(f"# Note: {note} #\n")
    file.write("# Data Format: Each row is a 1000-experiment average #\n")
    file.write("# The second-to-last row is the average of all rows above, i.e. average of all the 1000-experiment runs #\n")
    file.write("# The last row is the time row in ns #\n")
    file.close()

    # append the data to the file
    file = open("data/data_" + filename + ".txt", "a")
    np.savetxt(file, myarray, fmt = "%.18e", delimiter = ",")
    file.close()

def CreateNotchFilter(fs):

    """
    This function creates a notch filter to filter out the harmonics of the fundamental frequency.
    It takes the raw signal and the sampling frequency as input, and returns the notch filter coefficients.
    """
    
    # define notch filter parameters
    f0 = fs / 8  # fundamental frequency to filter out (in Hz)
    harmonics = [f0 * i for i in range (1, 5)]  # harmonics to filter out (in Hz)

    # add some additional harmonics that are not exact multiples of the fundamental frequency
    harmonics.append(984.96e6)
    harmonics.append(1.47744e9)
    harmonics.append(1.96992e9)
    harmonics.append(838.08e6)

    Q = 30.0  # quality factor for the notch filter, adjust for narrower or wider notches

    # Create notch filters for each harmonic
    notch_filters = []
    for f_h in harmonics:
        w0 = f_h / (fs / 2)  # Normalized frequency (0 to 1)
        b, a = iirnotch(w0, Q)
        notch_filters.append((b, a))
    
    return notch_filters

def ApplyNotchFilter(raw_signal, filter_coeff):

    """
    This function applies the notch filter to the raw signal. It takes the raw signal and the filter coefficients as input,
    and returns the filtered signal.
    """

    filtered_signal = raw_signal.copy()
    for b, a in filter_coeff:
        filtered_signal = filtfilt(b, a, filtered_signal)
    
    return filtered_signal

def InitializeMagnet(GPIB_channel = 1):

    """
    This function initializes the magnet by creating an instance of the Kepco class.
    It sets the mode to current and powers on the magnet. It then retuns the magnet instance.
    """
    
    kepco_instance = Kepco(GPIB_channel)
    kepco_instance.kepinit()  # initialize the Kepco instance
    kepco_instance.mode_current()  # set the mode to current
    kepco_instance.power_on()  # power on the magnet

    return kepco_instance

def RampMagnetCurrent(instance, current = 0.0):

    """
    This function ramps the magnet current to the desired value.
    It takes the instance of the Kepco class and the desired current as input.
    It returns the final current read.
    """

    instance.ramp_current(float(instance.get_current()), current, 0.01, 0.05) # set the current to the desired value by ramping
    print(f"Current ramped to {current} A.")
    curr_read = float(instance.get_current())
    print(f"Current Read: {curr_read}")
    
    return curr_read

def InitializeLO(serial_no = "10003FAC"):
    """
    This function initializes the local oscillator by creating an instance of the SC5511A class.
    It then turns off all the outputs for safety. Finally, it prints the device temperature.
    """

    LO_instance = SC5511A()
    LO_instance.open_device(serial_no) # open the connection to the device
    LO_instance.set_rf_mode(0) # set the RF mode to single frequency, not sweep
    LO_instance.set_standby(0) # turn on the standby mode
    LO_instance.set_output(False) # turn off the RF output
    LO_instance.set_rf2_standby(0) # turn on the standby mode of RF2
    print("Local Oscillator initialized.")
    print("Device Temperature:", LO_instance.get_temperature(), "C")

    return LO_instance

def TurnOnLO(instance, freq = 5.0, power = 0.0):

    """
    This function sets the RF1 frequency and power of the local oscillator.
    Then, it turns on the output.
    """

    if (freq <= 0.15 or freq >= 20.5):
        raise ValueError("Frequency must be between 0.15 and 20.5 GHz")
    instance.set_freq(int(freq * 1e9))
    print(f"LO frequency has been set to {freq} GHz")

    if (power <= -20 or power >= 20):
        raise ValueError("Power must be between -20 and 20 dBm")
    instance.set_level(float(power))
    print(f"LO power has been set to {power} dBm")

    instance.set_standby(1) # turn off the standby mode
    instance.set_output(True)  # turn on the RF output
    print("LO output is ON")


def TurnOffLO(instance):
    """
    This function turns off the output of the local oscillator.
    It sets the standby mode to 0 and turns off the RF output.
    """

    instance.set_standby(0)  # turn on the standby mode
    instance.set_output(False)  # turn off the RF output
    print("LO output is OFF")

def GetLOStatus(instance):

    """
    This function prints and returns some useful status information about the local oscillator.
    """

    temperature = instance.get_temperature()
    print(f"Current device temperature: {temperature} degC")

    rf_params = instance.get_rf_parameters()
    print(f"Current RF1 frequency: {rf_params.rf1_freq * 1e-9} GHz")
    print(f"Current Power: {rf_params.rf_level:.1f} dBm")
    print(f"RF1 output is {'ON' if rf_params.rf1_output else 'OFF'}")
    print(f"RF1 standby mode is {'ON' if rf_params.rf1_standby else 'OFF'}")

    device_status = instance.get_device_status()
    print(f"Main PLL   \t{'locked' if device_status.pll_status.sum_pll_ld else 'unlocked'}")
    print(f"Coarse PLL \t{'locked' if device_status.pll_status.crs_pll_ld else 'unlocked'}")
    print(f"Fine PLL   \t{'locked' if device_status.pll_status.fine_pll_ld else 'unlocked'}")
    print(f"Ref clk PLL\t{'locked' if device_status.pll_status.ref_100_pll_ld else 'unlocked'}")
    print(f"RF2 PLL    \t{'locked' if device_status.pll_status.rf2_pll_ld else 'unlocked'}")
    print(f"Crs ref PLL\t{'locked' if device_status.pll_status.crs_ref_pll_ld else 'unlocked'}")

    return temperature, rf_params, device_status

def main(timestamp, sample, pulse_frequency = 120, pulse_width = 15, magnet_inst = None, magnet_current = 0.0, LO_inst = None, LO_frequency = 5.0, LO_power = 0.0, number_of_experiments = 1000, max_batch_size = 1000, note = ""):
    
    """
    This main function sends a request to the Flask (a type of web server)
    server running on the board itself. Some parameters of the pulse is passed 
    with the request, and the readouts from ADCs are returned in JSON format 
    from the board. This function then exports the data to a .txt file, detects
    the pulses present, and plots the data.
    """

    current_read = RampMagnetCurrent(magnet_inst, magnet_current)  # turn on the magnet with specified current
    if abs(current_read - magnet_current) > 0.001:  # check if the current is set correctly
        raise RuntimeError(f"Magnet current not set correctly.")
    time.sleep(5)  # wait for the magnet to stabilize

    # check the status of the device, if it is too hot, wait for it to cool down
    (LO_temp, LO_rf_params, LO_status) =  GetLOStatus(LO_inst)
    if LO_temp > 50:
        TurnOffLO(LO_inst)
        print(f"Local oscillator temperature is too high: {LO_temp} degC. Waiting for it to cool down...")
        # wait until the temperature is below 50 degC
        while LO_temp > 50:
            time.sleep(5)
            (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)

    print(f"Local oscillator temperature is {LO_temp} degC. Continuing...")

    TurnOnLO(LO_inst, freq = LO_frequency, power = LO_power)  # turn on the local oscillator with the specified frequency and power
    time.sleep(1)  # wait for the LO to stabilize

    # check if the LO parameters are set correctly
    (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)
    if (LO_rf_params.rf1_freq != LO_frequency * 1e9 or LO_rf_params.rf_level != LO_power or not LO_rf_params.rf1_output or LO_rf_params.rf1_standby):
        TurnOffLO(LO_inst)
        raise RuntimeError("Local oscillator parameters are not set correctly. Please check the settings.")

    url = 'http://128.174.248.50:5500/run' # this is the URL address that the server on the board is listening
    
    # specify the parameters of the pulses in this payload to be sent over the internet to the board
    payload = {
        'freq': pulse_frequency,    # underlying frequency, same for both DACs.
        'width': pulse_width,       # this parameter is weird due to QICK problems
                                    # width = 100 -> real pulse width = 393.43ns
                                    # width = 50 -> real pulse width = 199.93ns
                                    # width = 10 -> real pulse width = 49.83ns
        'pulse_count': 1,           # number of pulses to be generated back to back in one experiment
        'trigger_delay': 1,         # delay amount of the triggering of the ADC buffer, essentially when to "press record", in us
                                    # trigger_delay = 1 -> first pulse around t = 50ns
        'number_of_expt': 1,        # how many experiments to be done, just a placeholder, will be set later
        'channel': 0                # which ADC channel to read, both of the DAC channels are generating the signal simultaneously
                                    # channel 0 -> ADC_D, channel 1 -> ADC_C
                                    # for our configuration, channel 0 is connected to the sample and channel 1 is in loopback
    }
    
    # raise an error if the max_batch_size is greater than 1000 to avoid memory issues on the board
    if max_batch_size > 1000:
        raise ValueError("max_batch_size cannot be greater than 1000 due to memory limitations of the board")

    # define the notch filter coefficients, this is only done once since the filter coefficients are the same for all experiments
    fs = 4423.68e6 
    notch_filters = CreateNotchFilter(fs)  # create the notch filter coefficients

    all_avg_data = []  # this will hold the average data from all batches of experiments

    for i in range(0, number_of_experiments, max_batch_size):
        batch_size = min(max_batch_size, number_of_experiments - i) # number of experiments in this batch
        new_payload = payload.copy() # copy the original payload
        new_payload['number_of_expt'] = batch_size # set the number of experiments in this batch

        print(f"Sending batch of {batch_size} experiments...")
        # send the actual request (HTTP request) to the board. don't forget to add the password. get the response from the board 
        response = requests.post(url, json=new_payload, headers={"auth": "magnetism@ESB165"})

        # if the response is not OK, raise an error
        if response.status_code != 200:
            print(f"Request for batch {i} failed with status code {response.status_code}")
            print("Response body:", response.text)
            raise RuntimeError("Failed request")
        
        response = np.array(response.json()['array'])  # convert the response to JSON format and parse it
        print(f"Batch {i // max_batch_size + 1} acquired successfully.")
        
        if i == 0:
            time_row = response[-1] * 1e3  # the last row is the time row, we take it only once, convert it to ns
        
        data_part = response[:-1]  # all but the last row, which is the time row

        filtered_data_part = ApplyNotchFilter(data_part, notch_filters)  # apply the notch filter to the data part

        avg_data = np.mean(filtered_data_part, axis = 0)  # get the average of the batch of experiments, i.e. colunm-wise

        all_avg_data.append(avg_data)  # append the average data to the list of all average data
        
        # plot the readout and the PSD of the data
        # PlotReadout(avg_data, time_row, timestamp, number_of_experiments, i // max_batch_size + 1)
        # PlotPSD(avg_data, timestamp, fs, number_of_experiments, i // max_batch_size + 1)

        print(f"Batch {i // max_batch_size + 1} processed successfully.")
        time.sleep(1)  # wait for a bit to avoid overwhelming the server
 
    # after all the batches are done, we stack the average data and the time row
    result = np.vstack([all_avg_data, np.mean(all_avg_data, axis = 0), time_row])

    # define a filename to be used
    filename = f"{timestamp}_Sample={sample}_Pulse={payload['freq']}MHz_AvgN={number_of_experiments}_MagnetI={magnet_current}_A"

    # export the data to a .txt file
    WriteToTXT(result, filename, timestamp, sample, payload, number_of_experiments, magnet_current, LO_frequency, LO_power, note)

    # plot the final readout and PSD of the averaged data
    PlotReadout(result[-2], time_row, filename, number_of_experiments, 9999)
    PlotPSD(result[-2], filename, fs, number_of_experiments, 9999)

    # calculate the SNR of the averaged data
    snr, snr_dB = CalculateSNR(result[-2])
    print(f"SNR (linear): {snr:.2f}, SNR (dB): {snr_dB:.2f} dB")

    RampMagnetCurrent(magnet_inst, 0.0)  # turn off the magnet after all experiments are done
    TurnOffLO(LO_inst)  # turn off the local oscillator after all experiments are done
    
"""
This final part is just for future use of this code. When you run this file,
it calls the funtion main() and does the job. But when you import this whole
file as a module in another script, it doesn't run main() function automatically,
you need to call the function. This is to make the integration smoother.
"""

if __name__ == "__main__":
    startt = time.time()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # get the current timestamp in the format YYYYMMDD_HHMMSS

    magnet_instance = InitializeMagnet(GPIB_channel = 1)  # initialize the magnet

    LO_instance = InitializeLO(serial_no = "10003FAC")

    main(
        timestamp = timestamp,                                      # current time, labeling purposes
        sample = "2024-Feb-Argn-YIG-2_5b-b1",                       # sample name, labeling purposes
        pulse_frequency = 120,                                      # pulse frequency in MHz, same for both DACs
        pulse_width = 15,                                           # pulse width in "weird" units, see the comments in the main function   
        magnet_inst = magnet_instance,                              # instance of the magnet control class, technical purposes   
        magnet_current = -3.0,                                      # current to set the magnet to, in Amperes
        LO_inst = LO_instance,                                      # instance of the local oscillator control class, technical purposes
        LO_frequency = 5.263,                                       # local oscillator frequency in GHz
        LO_power = 18.0,                                              # local oscillator power in dBm
        number_of_experiments = 1000,                               # the total number of experiments
        max_batch_size = 1000,                                      # maximum number of experiments in one batch (in one go)
        note = "4.8GHz LPF at rf amp & 1GHz LPF at ADC of rfsoc"    # notes for the experiment, labeling purposes
    )

    RampMagnetCurrent(magnet_instance, 0.0)  # double check that the magnet is turned off
    TurnOffLO(LO_instance)  # double check that the local oscillator is turned off

    endd = time.time()
    print(f"took {endd - startt} seconds")