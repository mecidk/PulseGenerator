import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time

def PlotReadout(read, time, pulse_pos, pulse_width, idx = 0):
    
    """
    This function plots the response. It takes the response array, which is just (raw values, time) stack
    and the current timestamp to save the figure. Additionally, it takes the positions of the endpoints of
    all detected pulses. It doesn't return anything.
    
    """
    
    plt.figure()
    plt.plot(read[-1], read[idx])
    plt.xlabel("ns")
    plt.ylabel("a.u.")
    plt.title(f"Direct Readout from the Buffer, Experiment {idx + 1}")
    for i in pulse_pos:
        plt.axvline(read[-1][i[0]], color='red', linestyle='--')
        plt.axvline(read[-1][i[1]], color='green', linestyle='--')
    
    text = ""
    for i in range(len(pulse_width)):
        text += f"Pulse {i + 1}: {pulse_width[i]:.2f} ns"
        if i == len(pulse_width) - 1:
            continue
        text += "\n"
        
    plt.plot([], [], label=text)
    
    plt.tight_layout()
    plt.legend()
    plt.savefig(f"plot_{time}.png", dpi=300, bbox_inches='tight')
    plt.show()

def WriteToTXT(myarray, filename = "out.txt"):
    
    """
    This function writes the readout to a .txt file. It takes the data itself and a filename.
    The data must be a numpy array like [[values], [times]]
    """
    
    if not isinstance(myarray, np.ndarray):
        raise TypeError("Input must be a numpy array")
    
    np.savetxt(filename, myarray, fmt="%.8e", delimiter=",")

def main():
    
    """
    This main function sends a request to the Flask (a type of web server)
    server running on the board itself. Some parameters of the pulse is passed 
    with the request, and the readouts from ADCs are returned in JSON format 
    from the board. This function then exports the data to a .txt file, detects
    the pulses present, and plots the data.
    """
    
    url = 'http://128.174.248.50:5500/run' # this is the URL address that the server on the board is listening
    
    # specify the parameters of the pulses in this payload to be sent over the internet to the board
    payload = {
        'freq': 100,                # underlying frequency, same for both DACs.
        'width': 10,                # this parameter is weird due to QICK problems
                                    # width = 100 -> real pulse width = 393.43ns
                                    # width = 50 -> real pulse width = 199.93ns
                                    # width = 10 -> real pulse width = 49.83ns
        'pulse_count': 1,           # number of pulses to be generated back to back in one experiment
        'trigger_delay': 1,         # delay amount of the triggering of the ADC buffer, essentially when to "press record", in us
                                    # trigger_delay = 1 -> first pulse around t = 50ns
        'number_of_expt': 1 # how many experiments to be done
    }
    
    # send the actual request (HTTP request) to the board. don't forget to add the password. get the response from the board 
    response = requests.post(url, json = payload, headers = {"auth": "magnetism@ESB165"})
    
    # if the response is not OK, raise an error
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        print("Response body:", response.text)
        raise RuntimeError("Failed request")
        
    """
    This is the main response from the board, an array consisting of 
    [[raw data], [timestamps]]. First part is the direct *raw* read of the 
    first ADC, channel 0. Second part is the corresponding timestamp of each sample.
    """
    readout = np.array(response.json()['array'])
    print(readout)
    
    readout[-1] = readout[-1] * 1e3 # the board sends the data in us, we turn it to ns
    
    # store the files with the timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename =  f"readout_{timestamp}.txt"
    WriteToTXT(readout, filename)
    
    # loop over every experiment/run
    for i in range(payload['number_of_expt']):
        """
        This part detects the pulses present in the data array.
        """
        abs_signal = np.abs(readout[i]) # take the absolute value of the data to make detection easier
    
        # apply a moving-average filter to get the envelope. window length is 20
        kernel = np.ones(20) / 20
        smoothed = np.convolve(abs_signal, kernel, mode='same')
    
        # apply the threshold to the signal to detect the pulse
        threshold = 0.015 * np.max(smoothed)
        print(f"experiment {i}, threshold {threshold}")
        above = smoothed > threshold
    
        # detect rising and falling edges
        edges = np.diff(above.astype(int))
        starts = np.where(edges == 1)[0] + 1
        ends = np.where(edges == -1)[0] + 1 
    
        # find the pulse and get the pulse width
        if len(starts) > 0 and len(ends) > 0:
            
            pulse_widths = []
            pulse_positions = []
    
            for s in starts:
                for e in ends:
                    if e > s:
                        endpoint_pair = [s, e] # CAREFUL, this pair is holding the sample number, NOT the timestamp
                        pulse_positions.append(endpoint_pair)
                        width = (readout[-1][e] - readout[-1][s])
                        pulse_widths.append(width)
                        break
            
            for i in range(len(pulse_widths)):
                print(f"Pulse detected: starts at {readout[-1][pulse_positions[i][0]]} ns, ends at {readout[-1][pulse_positions[i][1]]} ns, has the width {pulse_widths[i]} ns")
       
        else:
            print("No pulse detected")
            
        # plot the incoming data, iterator i is sent to get the correct experiment
        PlotReadout(readout, timestamp, pulse_positions, pulse_widths, i)
    
"""
This final part is just for future use of this code. When you run this file,
it calls the funtion main() and does the job. But when you import this whole
file as a module in another script, it doesn't run main() function automatically,
you need to call the function. This is to make the integration smoother.
"""    
if __name__ == "__main__":
    startt = time.time()
    main()
    endd = time.time()
    print(f"took {endd - startt} seconds")