import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import iirnotch, filtfilt, welch
import time
from MagnetControl import Kepco

def PlotReadout(read, time_row, timestamp, no_of_experiments, batch_number):
    
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
        plt.title(f"Readout, Averaged over {no_of_experiments} experiments, Total Average")
        plt.savefig(f"data_{timestamp}_total.png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"Readout, Averaged over {no_of_experiments} experiments, Batch {batch_number}")
        plt.savefig(f"data_{timestamp}_batch_{batch_number}.png", dpi=300, bbox_inches='tight')

    plt.show()

def PlotPSD(data, timestamp, fs, no_of_experiments, batch_number):

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
        plt.title(f"PSD, Averaged over {no_of_experiments} experiments, Total Average")
        plt.savefig(f"psd_{timestamp}_total.png", dpi=300, bbox_inches='tight')
    else:
        plt.title(f"PSD, Averaged over {no_of_experiments} experiments, Batch {batch_number}")
        plt.savefig(f"psd_{timestamp}_batch_{batch_number}.png", dpi=300, bbox_inches='tight')
    
    plt.show()

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

def WriteToTXT(myarray, timestamp, sample, payload, number_of_experiments, magnet_current):
    
    if not isinstance(myarray, np.ndarray):
        raise TypeError("Input must be a numpy array")
    
    # add header to the file
    filename = f"data/data_{timestamp}_Sample={sample}_Pulse={payload['freq']}MHz_AvgN={number_of_experiments}_MagnetI={magnet_current}.txt"
    file = open(filename, "w")
    file.write(f"# Date and Time: {timestamp} #\n")
    file.write(f"# Sample: {sample} #\n")
    file.write(f"# Pulse Frequency and Width: {payload['freq']} MHz, {payload['width']} #\n")
    file.write(f"# LO Frequency and Power: {5.383 - (int(payload['freq']) * 1e-3)} GHz, +18 dBm #\n")
    file.write(f"# Number of Experiments: {number_of_experiments} #\n")
    file.write(f"# Magnet Current and Field: {magnet_current} A #\n")
    file.write("# Data Format: Each row is a 1000-experiment average #\n")
    file.write("# The second-to-last row is the average of all rows above, i.e. averega of all the 1000-experiment runs #\n")
    file.write("# The last row is the time row in ns #\n")
    file.close()

    # append the data to the file
    file = open(filename, "a")
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

def TurnOnMagnet(instance, GPIB_channel = 1, current = 0.0):
    instance.ramp_current(float(instance.get_current()), current, 0.01, 0.05) # set the current to the desired value by ramping
    print(f"Current ramped up to {current} A on GPIB channel {GPIB_channel}")
    print(f"Current Read: {float(instance.get_current())}")

def TurnOffMagnet(instance, GPIB_channel = 1):
    instance.ramp_current(float(instance.get_current()), 0.0, 0.01, 0.05) # turn off the magnet by ramping to 0 A
    print(f"Current ramped down to 0 A on GPIB channel {GPIB_channel}")
    print(f"Current Read: {float(instance.get_current())}")

def main(timestamp, sample, pulse_frequency = 120, pulse_width = 15, magnet_current = 0.0, number_of_experiments = 1000):
    
    """
    This main function sends a request to the Flask (a type of web server)
    server running on the board itself. Some parameters of the pulse is passed 
    with the request, and the readouts from ADCs are returned in JSON format 
    from the board. This function then exports the data to a .txt file, detects
    the pulses present, and plots the data.
    """
    
    # create an instance of the Kepco class to control the magnet and set the current
    kepco_instance = Kepco(1)
    kepco_instance.kepinit()
    kepco_instance.mode_current()
    kepco_instance.power_on()
    TurnOnMagnet(kepco_instance, GPIB_channel = 1, current = magnet_current)  # turn on the magnet with -3.0 A current
    time.sleep(5)  # wait for the magnet to stabilize

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
    
    max_batch_size = 1000  # number of experiments to be done in one batch, this is to avoid overwhelming the server

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
    
    WriteToTXT(result, timestamp, sample, payload, number_of_experiments, magnet_current)

    # plot the final readout and PSD of the averaged data
    PlotReadout(result[-2], time_row, timestamp, number_of_experiments, 9999)
    PlotPSD(result[-2], timestamp, fs, number_of_experiments, 9999)

    # calculate the SNR of the averaged data
    snr, snr_dB = CalculateSNR(result[-2])
    print(f"SNR (linear): {snr:.2f}, SNR (dB): {snr_dB:.2f} dB")

    TurnOffMagnet(kepco_instance, GPIB_channel = 1)  # turn off the magnet after all experiments are done
    
"""
This final part is just for future use of this code. When you run this file,
it calls the funtion main() and does the job. But when you import this whole
file as a module in another script, it doesn't run main() function automatically,
you need to call the function. This is to make the integration smoother.
"""

if __name__ == "__main__":
    startt = time.time()

    main(
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S"),
        sample = "2024-Feb-Argn-YIG-2_5b-b1",
        pulse_frequency = 120,
        pulse_width = 15,
        magnet_current = -3.0, 
        number_of_experiments = 1000
    )

    endd = time.time()
    print(f"took {endd - startt} seconds")