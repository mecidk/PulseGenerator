import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import time
from magnet_lib import Kepco
from sc5511a_lib import SC5511A
from bnc855b_lib import signalGenerator855B

def PlotReadout(read, time_row, filename, no_of_experiments, channel):
    
    """
    This function plots the response. It takes the response array, which is just (raw values, time) stack
    and the current timestamp to save the figure. It doesn't return anything.
    """
    
    plt.figure()
    plt.plot(time_row, read) # take the time row and the average row to plot
    plt.xlabel("ns")
    plt.ylabel("a.u.")
    plt.tight_layout()

    if channel == 0:
        plt.title(f"Magnitude, Grand Average of {no_of_experiments} Experiments, Channel 0")
        plt.savefig("data/plot_" + filename + "_ch0.png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"Magnitude, Grand Average of {no_of_experiments} Experiments, Channel 1")
        plt.savefig("data/plot_" + filename + "_ch1.png", dpi=300, bbox_inches='tight')

    plt.close()

def PlotPSD(data, filename, fs, no_of_experiments, channel):

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
    if channel == 0:
        plt.title(f"PSD, Grand Average of {no_of_experiments} Experiments, Channel 0")
        plt.savefig("data/PSD_" + filename + "_ch0.png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"PSD, Grand Average of {no_of_experiments} Experiments, Channel 1")
        plt.savefig("data/PSD_" + filename + "_ch1.png", dpi=300, bbox_inches='tight')

    plt.close()

def CalculateSNR(signal):

    """
    This function calculates the Signal-to-Noise Ratio (SNR) of the signal.
    It takes the signal as input and returns the SNR in both linear and dB scale.
    The SNR is calculated by taking the maximum amplitude of the pulse region and
    dividing it by the standard deviation of the noise region.
    """

    pulse_region = signal[120:160]
    signal_amplitude = np.max(pulse_region) - np.min(pulse_region)

    noise_region = signal[250:]
    noise_amplitude = np.std(noise_region)

    snr = signal_amplitude / noise_amplitude
    snr_dB = 20 * np.log10(snr)

    return snr, snr_dB

def StartTXTFile(filename, timestamp, sample, payload, number_of_experiments, max_batch_size, use_batch_average, magnet_current, LO_frequency,  LO_power, read_freq, note):
    
    """
    This function initiates .txt files with a headers containing metadata about the experiment.
    """
    for index, signal_type in enumerate(["ch0_I", "ch0_Q", "ch1_I", "ch1_Q"]):
        file = open("data/data_" + filename + f"_{signal_type}.txt", "w")
        file.write(f"# Date and Time: {timestamp} #\n")
        file.write(f"# Sample: {sample} #\n")
        file.write(f"# Channel {signal_type[2]} {'In-phase' if signal_type[-1] == 'I' else 'Quadrature'} #\n")
        file.write(f"# Pulse Type: {payload['type']} #\n")
        file.write(f"# Pulse Frequency and Width: {payload['freq']} MHz, {payload['width'] * 4} ns #\n")
        file.write(f"# Downconverting Frequency: {read_freq} MHz #\n")

        if index in [0, 1]:  # only for channel 0 and 1
            file.write(f"# LO Frequency and Power: {LO_frequency} GHz, {LO_power} dBm #\n")
            file.write(f"# Magnet Current: {magnet_current} A #\n")
        else:
            file.write("# Loopback channel, no LO and Magnet #\n")

        file.write(f"# Number of Experiments: {number_of_experiments} #\n")
        file.write(f"# Max Batch Size: {max_batch_size} #\n")
        file.write(f"# Is each batch averaged?: {use_batch_average} #\n")

        file.write(f"# Note: {note} #\n")

        if use_batch_average:
            file.write(f"# Data Format: Each row is a {max_batch_size}-experiment average #\n")
        else:
            file.write("# Data Format: Each row is an experiment #\n")

        file.write("# The second-to-last row is the average of all rows above #\n")
        file.write("# The last row is the time row in ns #\n")
        file.close()

def AppendToTXTFile(filename, data_type, data):

    """
    This function appends a row of data to the .txt file.
    It takes the filename, type of data (either 'array' or 'time'), and the data itself as input.
    """

    if not isinstance(data, np.ndarray):
        raise TypeError("Input must be a numpy array")

    for index, signal_type in enumerate(["ch0_I", "ch0_Q", "ch1_I", "ch1_Q"]):

        if data_type == "array":
            file = open("data/data_" + filename + f"_{signal_type}.txt", "a")
            np.savetxt(file, data[index], fmt = "%.6e", delimiter = ",")
            file.close()
        elif data_type == "time":
            file = open("data/data_" + filename + f"_{signal_type}.txt", "a")
            np.savetxt(file, data, fmt = "%.6e", delimiter = ",")
            file.close()
        else:
            raise ValueError("data_type must be 'array' or 'time'")

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
    
    print(f"Ramping current to {current} A")
    instance.ramp_current(float(instance.get_current()), current, 0.01, 0.05) # set the current to the desired value by ramping
    print(f"Current ramped to {current} A")

    # check if the current read is within the expected range
    curr_read = float(instance.get_current())
    if abs(curr_read - current) > 0.001:
        print("Current read is not within the expected range. Retrying...")
        curr_read = RampMagnetCurrent(instance, current)

    print(f"Current read: {curr_read} A")
    
    return curr_read

def InitializeLO(LO_type = ""):

    """
    This function initializes the local oscillator based on the type specified.
    It creates an instance of the appropriate class based on the LO_type, and sets some initial parameters.
    """

    if LO_type == "SC5511A":
        serial_no = "10003FAC"
        LO_instance = SC5511A()
        LO_instance.open_device(serial_no) # open the connection to the device
        LO_instance.set_rf_mode(0) # set the RF mode to single frequency, not sweep
        LO_instance.set_standby(1) # turn on the standby mode
        LO_instance.set_output(False) # turn off the RF output
        LO_instance.set_rf2_standby(1) # turn on the standby mode of RF2
        print("Local Oscillator initialized")
    elif LO_type == "BNC855B":
        LO_instance = signalGenerator855B()
        LO_instance.outPutOff(1)  # turn off the output for safety
        LO_instance.outPutOff(2)  # turn off the output for safety
        print("BNC 855B Local Oscillator initialized")
    else:
        raise ValueError("Unsupported LO type. Please use 'SC5511A' or 'BNC855B'")
    
    return LO_instance

def TurnOnLO(instance, freq = 1.0, power = 0.0):

    """
    This function turns on the local oscillator (LO) by setting the frequency and power.
    It takes the instance of the LO class, frequency in GHz, and power in dBm as input.
    """

    if isinstance(instance, SC5511A):

        if (freq <= 0.15 or freq >= 20.5):
            raise ValueError("Frequency must be between 0.15 and 20.5 GHz")
        instance.set_freq(int(freq * 1e9))
        print(f"LO frequency has been set to {freq} GHz")

        if (power <= -20 or power >= 20):
            raise ValueError("Power must be between -20 and 20 dBm")
        instance.set_level(float(power))
        print(f"LO power has been set to {power} dBm")

        instance.set_standby(0) # turn off the standby mode
        instance.set_output(True)  # turn on the RF output
        print("LO output is ON")
    elif isinstance(instance, signalGenerator855B):
        for channel in [1, 2]:
            if (freq <= 0.0003 or freq >= 40.0):
                raise ValueError("Frequency must be between 300 kHz and 40 GHz")
            instance.freq(channel, freq)  # set the frequency of the channel
            print(f"BNC LO channel {channel} frequency has been set to {freq} GHz")

            if (power <= -20 or power >= 25):
                raise ValueError("Power must be between -20 and 25 dBm")
            instance.power(channel, power)  # set the power of channel 1
            print(f"BNC LO channel {channel} power has been set to {power} dBm")

            instance.outPutOn(channel)  # turn on the output of channel 1
            print(f"BNC LO channel {channel} output is ON")
    else:
        raise ValueError("Unsupported LO instance. Please use an instance of SC5511A or signalGenerator855B")

def TurnOffLO(instance):
    """
    This function turns off the local oscillator (LO) by setting the output to False.
    It takes the instance of the LO class as input.
    """

    if isinstance(instance, SC5511A):

        instance.set_standby(1)  # turn on the standby mode
        instance.set_output(False)  # turn off the RF output
        # check if the output is turned off, if not call TurnOffLO again
        if (instance.get_device_status().operate_status.rf1_standby) and (not instance.get_device_status().operate_status.rf1_out_enable):
            print("LO output is OFF")
        else:
            print("Failed to turn off LO output, trying again...")
            TurnOffLO(instance)
    elif isinstance(instance, signalGenerator855B):

        for channel in [1, 2]:
            instance.outPutOff(channel)  # turn off the output of channel 1
        
        if (not instance.outPutQuery(1)) and (not instance.outPutQuery(2)):
            print("BNC LO output is OFF")
        else:
            print("Failed to turn off LO output, trying again...")
            TurnOffLO(instance)
    else:
        raise ValueError("Unsupported LO instance. Please use an instance of SC5511A or signalGenerator855B")
    
def GetLOStatus(instance):

    """
    This function retrieves the status of the local oscillator (LO).
    It returns the temperature, RF parameters, and device status.
    Temperature is only available for SC5511A, so it will be 0 for signalGenerator855B.

    """

    if isinstance(instance, SC5511A):

        temperature = instance.get_temperature()

        rf_params = {
            'rf1_freq': instance.get_rf_parameters().rf1_freq * 1e-9,  # frequency in GHz
            'rf2_freq': instance.get_rf_parameters().rf2_freq * 1e-9,  # frequency in GHz
            'rf1_level': instance.get_rf_parameters().rf_level,  # power in dBm
            'rf2_level': instance.get_rf_parameters().rf_level  # power in dBm
        }
        
        device_status = {
            'rf1_standby': instance.get_device_status().operate_status.rf1_standby,
            'rf1_out_enable': instance.get_device_status().operate_status.rf1_out_enable,
            'rf2_standby': instance.get_device_status().operate_status.rf2_standby,
            'rf2_out_enable': True  # SC5511A does not have extra RF2 control, it is always enabled if not in standby
        }
    elif isinstance(instance, signalGenerator855B):

        temperature = 0 # BNC 855B does not provide temperature information

        rf_params = {
            'rf1_freq': instance.freqQuery(1),  # frequency in GHz
            'rf2_freq': instance.freqQuery(2),  # frequency in GHz
            'rf1_level': instance.powerQuery(1),  # power in dBm
            'rf2_level': instance.powerQuery(2)   # power in dBm
        }

        device_status = {
            'rf1_standby': False,  # BNC 855B does not have a standby mode
            'rf1_out_enable': instance.outPutQuery(1),
            'rf2_standby': False,   # BNC 855B does not have a standby mode
            'rf2_out_enable': instance.outPutQuery(2)
        }
    else:
        raise ValueError("Unsupported LO instance. Please use an instance of SC5511A or signalGenerator855B")

    return temperature, rf_params, device_status

def main(timestamp, sample, pulse_type = "gaussian", pulse_frequency = 120, pulse_width = 15, read_frequency = 0, magnet_inst = None, magnet_current = 0.0, LO_inst = None, LO_frequency = 5.0, LO_power = 0.0, number_of_experiments = 1000, max_batch_size = 1000, use_batch_average = True,  note = ""):
    
    """
    This main function sends a request to the Flask (a type of web server)
    server running on the board itself. Some parameters of the pulse is passed 
    with the request, and the readouts from ADCs are returned in JSON format 
    from the board. This function then exports the data to a .txt file, detects
    the pulses present, and plots the data.
    """

    # raise an error if the max_batch_size is greater than 1000 to avoid memory issues on the board
    if max_batch_size > 1000:
        raise ValueError("max_batch_size cannot be greater than 1000 due to memory limitations of the board")
    
    # raise an error if the pulse type is not 'gaussian' or 'flat_top'
    if pulse_type not in ["gaussian", "flat_top", "const"]:
        raise ValueError("Only supported pulse types are 'gaussian', 'flat_top' and 'const'")
    
    current_read = RampMagnetCurrent(magnet_inst, magnet_current)  # turn on the magnet with specified current
    time.sleep(5)  # wait for the magnet to stabilize
    if abs(current_read - magnet_current) > 0.001:  # check if the current is set correctly
        raise RuntimeError("Magnet current not set correctly.")

    TurnOnLO(LO_inst, freq = LO_frequency, power = LO_power)  # turn on the local oscillator with the specified frequency and power
    time.sleep(1)  # wait for the LO to stabilize

    # check if the LO parameters are set correctly
    (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)
    if ((np.abs(LO_rf_params["rf1_freq"] - LO_frequency) > 1e-9) or (np.abs(LO_rf_params["rf1_level"] - LO_power) > 1e-3) or not LO_status["rf1_out_enable"] or LO_status["rf1_standby"]):
        TurnOffLO(LO_inst)
        raise RuntimeError("Local oscillator parameters are not set correctly. Please check the settings.")
    
    url = 'http://128.174.248.50:5500/run' # this is the URL address that the server on the board is listening

    # specify the parameters of the pulses in this payload to be sent over the internet to the board
    payload = {
        'mode': 'decimated',                                # mode of the pulse, can be 'raw' or 'decimated'
        'type': pulse_type,                                 # type of the pulse, can be 'gaussian' or 'flat_top'
        'freq': pulse_frequency,                            # underlying frequency, same for both DACs.
        'width': pulse_width,                               # this parameter is weird due to QICK problems
                                                            # width = 100 -> real pulse width = 393.43ns
                                                            # width = 50 -> real pulse width = 199.93ns
                                                            # width = 10 -> real pulse width = 49.83ns
        'pulse_count': 1,                                   # number of pulses to be generated back to back in one experiment
        'trigger_delay': 0.2,                               # delay amount of the triggering of the ADC buffer, essentially when to "press record", in us
                                                            # trigger_delay = 1 -> first pulse around t = 50ns
        'number_of_expt': 1,                                # how many experiments to be done, just a placeholder, will be set later
        'read_freq': read_frequency                         # frequency to downconvert the signal
    }

    fs = 552.96e6 # define decimated sampling frequency of the ADCs

    all_batches_data_ch0_I = []  # list to store the data for channel 0 I
    all_batches_data_ch0_Q = []  # list to store the data for channel 0 Q
    all_batches_data_ch1_I = []  # list to store the data for channel 1 I
    all_batches_data_ch1_Q = []  # list to store the data for channel 1 Q

    filename = f"decimated_{timestamp}_Sample={sample}_Pulse={pulse_type}_{payload['freq']}MHz_AvgN={number_of_experiments}_MagnetI={magnet_current}_A"
    
    # export the data to a .txt file
    StartTXTFile(filename, timestamp, sample, payload, number_of_experiments, max_batch_size, use_batch_average, magnet_current, LO_frequency, LO_power, read_frequency, note)

    for i in range(0, number_of_experiments, max_batch_size):
        batch_size = min(max_batch_size, number_of_experiments - i) # number of experiments in this batch
        new_payload = payload.copy() # copy the original payload
        new_payload['number_of_expt'] = batch_size # set the number of experiments in this batch

        # check the status of the LO device, if it is too hot, wait for it to cool down
        (LO_temp, LO_rf_params, LO_status) =  GetLOStatus(LO_inst)
        if LO_temp > 50:
            TurnOffLO(LO_inst)
            print(f"Local oscillator temperature is too high: {LO_temp} degC. Waiting for it to cool down...")

            # wait until the temperature is below 50 degC
            while LO_temp > 50:
                time.sleep(5)
                (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)

            # turn the LO back on after cooling down
            TurnOnLO(LO_inst, freq = LO_frequency, power = LO_power)
            time.sleep(1)

            # check if the LO parameters are set correctly
            (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)
            if ((np.abs(LO_rf_params["rf1_freq"] - LO_frequency) > 1e-9) or (np.abs(LO_rf_params["rf1_level"] - LO_power) > 1e-3) or not LO_status["rf1_out_enable"] or LO_status["rf1_standby"]):
                TurnOffLO(LO_inst)
                raise RuntimeError("Local oscillator parameters are not set correctly. Please check the settings.")
        elif ((np.abs(LO_rf_params["rf1_freq"] - LO_frequency) > 1e-9) or (np.abs(LO_rf_params["rf1_level"] - LO_power) > 1e-3) or not LO_status["rf1_out_enable"] or LO_status["rf1_standby"]):
            print("Local oscillator parameters are not set correctly. Turning it off and trying again...")
            TurnOffLO(LO_inst)
            TurnOnLO(LO_inst, freq = LO_frequency, power = LO_power)
            time.sleep(1)
            
            # if still not set correctly, raise an error
            (LO_temp, LO_rf_params, LO_status) = GetLOStatus(LO_inst)
            if ((np.abs(LO_rf_params["rf1_freq"] - LO_frequency) > 1e-9) or (np.abs(LO_rf_params["rf1_level"] - LO_power) > 1e-3) or not LO_status["rf1_out_enable"] or LO_status["rf1_standby"]):
                TurnOffLO(LO_inst)
                raise RuntimeError("Local oscillator parameters are not set correctly. Please check the settings.")
        
        # check the status of the magnet, if it is not set to the desired current, try again
        curr_read = float(magnet_inst.get_current())
        if abs(curr_read - magnet_current) > 0.001:
            RampMagnetCurrent(magnet_inst, magnet_current)
            time.sleep(5)  # wait for the magnet to stabilize
            curr_read = float(magnet_inst.get_current())
            
            if abs(curr_read - magnet_current) > 0.001:
                raise RuntimeError("Magnet current not set correctly. Please check the settings.")

        print(f"Sending batch of {batch_size} experiments...")

        # send the actual request (HTTP request) to the board. don't forget to add the password. get the response from the board 
        response = requests.post(url, json=new_payload, headers={"auth": "magnetism@ESB165"})

        # if the response is not OK, raise an error
        if response.status_code != 200:
            print(f"Request for batch {i} failed with status code {response.status_code}")
            print("Response body:", response.text)
            raise RuntimeError("Failed request")
        
        # get the response and parse it
        response_ch0_I = np.array(response.json()['ch0_I'])
        response_ch0_Q = np.array(response.json()['ch0_Q'])
        response_ch1_I = np.array(response.json()['ch1_I'])  
        response_ch1_Q = np.array(response.json()['ch1_Q'])

        print(f"Batch {i // max_batch_size + 1} acquired successfully.")
        
        if i == 0:
            time_row = response_ch0_I[-1] * 1e3 # the last row is the time row, we take it only once, convert it to ns
        
        data_part_ch0_I = response_ch0_I[:-1]
        data_part_ch0_Q = response_ch0_Q[:-1]
        data_part_ch1_I = response_ch1_I[:-1]
        data_part_ch1_Q = response_ch1_Q[:-1]

        if use_batch_average:
            # if we are using batch averaging, we take the average of the data part
            avg_data_ch0_I = np.mean(data_part_ch0_I, axis=0)
            avg_data_ch0_Q = np.mean(data_part_ch0_Q, axis=0)
            avg_data_ch1_I = np.mean(data_part_ch1_I, axis=0)
            avg_data_ch1_Q = np.mean(data_part_ch1_Q, axis=0)

            all_batches_data_ch0_I.append(avg_data_ch0_I[np.newaxis, :])
            all_batches_data_ch0_Q.append(avg_data_ch0_Q[np.newaxis, :])
            all_batches_data_ch1_I.append(avg_data_ch1_I[np.newaxis, :])
            all_batches_data_ch1_Q.append(avg_data_ch1_Q[np.newaxis, :])

            AppendToTXTFile(filename, data_type = "array", data = np.array([avg_data_ch0_I[np.newaxis, :], avg_data_ch0_Q[np.newaxis, :], avg_data_ch1_I[np.newaxis, :], avg_data_ch1_Q[np.newaxis, :]]))
        else:
            # if we are not using batch averaging, we append the whole data part to the all_batches_data
            all_batches_data_ch0_I.extend(data_part_ch0_I)
            all_batches_data_ch0_Q.extend(data_part_ch0_Q)
            all_batches_data_ch1_I.extend(data_part_ch1_I)
            all_batches_data_ch1_Q.extend(data_part_ch1_Q)

            AppendToTXTFile(filename, data_type = "array", data = np.array([data_part_ch0_I, data_part_ch0_Q, data_part_ch1_I, data_part_ch1_Q]))

        print(f"Batch {i // max_batch_size + 1} processed successfully")
        time.sleep(1)  # wait for a bit to avoid overwhelming the server

    all_batches_data_ch0_I = np.array(all_batches_data_ch0_I)
    all_batches_data_ch0_Q = np.array(all_batches_data_ch0_Q)
    all_batches_data_ch1_I = np.array(all_batches_data_ch1_I)
    all_batches_data_ch1_Q = np.array(all_batches_data_ch1_Q)

    # calculate the grand average of all batches
    if use_batch_average:
        grand_average_ch0_I = np.mean(all_batches_data_ch0_I, axis=0)[0]
        grand_average_ch0_Q = np.mean(all_batches_data_ch0_Q, axis=0)[0]
        grand_average_ch1_I = np.mean(all_batches_data_ch1_I, axis=0)[0]
        grand_average_ch1_Q = np.mean(all_batches_data_ch1_Q, axis=0)[0]
    else:
        grand_average_ch0_I = np.mean(all_batches_data_ch0_I, axis=0)
        grand_average_ch0_Q = np.mean(all_batches_data_ch0_Q, axis=0)
        grand_average_ch1_I = np.mean(all_batches_data_ch1_I, axis=0)
        grand_average_ch1_Q = np.mean(all_batches_data_ch1_Q, axis=0)

    # append the final average data and the time row to the .txt file
    AppendToTXTFile(filename, data_type = "array", data = np.array([grand_average_ch0_I[np.newaxis, :], grand_average_ch0_Q[np.newaxis, :],
                                        grand_average_ch1_I[np.newaxis, :], grand_average_ch1_Q[np.newaxis, :]]))
    AppendToTXTFile(filename, data_type = "time", data = time_row[np.newaxis, :])

    # plot the final readout and PSD of the averaged data
    PlotReadout(np.abs(grand_average_ch0_I + 1j * grand_average_ch0_Q), time_row, filename, number_of_experiments, channel = 0)
    # PlotReadout(np.abs(grand_average_ch1_I + 1j * grand_average_ch1_Q), time_row, filename, number_of_experiments, channel = 1)
    PlotPSD(np.abs(grand_average_ch0_I + 1j * grand_average_ch0_Q), filename, fs, number_of_experiments, channel = 0)
    # PlotPSD(np.abs(grand_average_ch1_I + 1j * grand_average_ch1_Q), filename, fs, number_of_experiments, channel = 1)

    # calculate the SNR of the averaged data
    snr_ch0, snr_dB_ch0 = CalculateSNR(np.abs(grand_average_ch0_I + 1j * grand_average_ch0_Q))
    print(f"Channel 0 SNR (linear): {snr_ch0:.2f}, SNR (dB): {snr_dB_ch0:.2f} dB")
    snr_ch1, snr_dB_ch1 = CalculateSNR(np.abs(grand_average_ch1_I + 1j * grand_average_ch1_Q))
    print(f"Channel 1 SNR (linear): {snr_ch1:.2f}, SNR (dB): {snr_dB_ch1:.2f} dB")

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

    magnet_instance = InitializeMagnet(GPIB_channel = 1)  # initialize the magnet

    LO_instance = InitializeLO(LO_type = "SC5511A")  # initialize local oscillator, can be "SC5511A" or "BNC855B"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # get the current timestamp in the format YYYYMMDD_HHMMSS

    try:
        main(
            timestamp = timestamp,                                      # current time, labeling purposes
            sample = "2024-Feb-Argn-YIG-2_5b-b1",                       # sample name, labeling purposes
            pulse_type = "flat_top",                                    # type of the pulse, can be "gaussian", "flat_top" or "const"
            pulse_frequency = 5383,                                      # pulse frequency in MHz, same for both DACs
            pulse_width = 10,                                           # pulse width in "weird" units, see the comments in the main function
            read_frequency = 5383,                                      # frequency used to downconvert the signal
            magnet_inst = magnet_instance,                              # instance of the magnet control class, technical purposes   
            magnet_current = -3.0,                                      # current to set the magnet to, in Amperes
            LO_inst = LO_instance,                                      # instance of the local oscillator control class, technical purposes
            LO_frequency = 5.263,                                       # local oscillator frequency in GHz
            LO_power = 0.0,                                            # local oscillator power in dBm
            number_of_experiments = 300,                                # total number of experiments
            max_batch_size = 1000,                                      # maximum number of experiments in one batch (in one go)
            use_batch_average = False,                                  # whether to average batches of experiments or not
            note = "decimated test second case: upconverting outside the board, rf amp, downconverting to 120 outside, IF amplifier"                              # notes for the experiment, labeling purposes
        )
    finally:
        RampMagnetCurrent(magnet_instance, 0.0)  # double check that the magnet is turned off

        TurnOffLO(LO_instance)  # double check that the local oscillator is turned off

        if isinstance(LO_instance, SC5511A):
            LO_instance.close_device() # close the connection to the SC5511A device, this is needed since it is NOT a VISA device
            print("LO connection closed")

        endd = time.time()
        print(f"took {endd - startt} seconds")