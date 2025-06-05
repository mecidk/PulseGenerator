import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time

def PlotReadout(read, time, no_of_experiments):
    
    """
    This function plots the response. It takes the response array, which is just (raw values, time) stack
    and the current timestamp to save the figure. It doesn't return anything.
    
    """
    
    plt.figure()
    plt.plot(read[-1], read[-2]) # take the time row and the average row to plot
    plt.xlabel("ns")
    plt.ylabel("a.u.")
    plt.title(f"Direct Readout from the Buffer, Averaged over {no_of_experiments} experiments")

    plt.tight_layout()
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
        'freq': 120,                # underlying frequency, same for both DACs.
        'width': 15,                # this parameter is weird due to QICK problems
                                    # width = 100 -> real pulse width = 393.43ns
                                    # width = 50 -> real pulse width = 199.93ns
                                    # width = 10 -> real pulse width = 49.83ns
        'pulse_count': 1,           # number of pulses to be generated back to back in one experiment
        'trigger_delay': 1,         # delay amount of the triggering of the ADC buffer, essentially when to "press record", in us
                                    # trigger_delay = 1 -> first pulse around t = 50ns
        'number_of_expt': 1         # how many experiments to be done, just a placeholder, will be set later
    }
    
    number_of_experiments = 1000 # total number of experiments to be done

    all_data_rows = []

    for i in range(0, number_of_experiments, 1000):
        batch_size = min(1000, number_of_experiments - i) # number of experiments in this batch
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
        
        response = response.json()['array']  # convert the response to JSON format
        print(f"Batch {i // 1000 + 1} completed successfully.")
        
        data_part = response[:-1]  # all but the last row, which is the time row
        all_data_rows.extend(data_part)  # extend the responses list with the data part

        if i == 0:
            time_row = response[-1]  # the last row is the time row, we take it only once

        time.sleep(1)  # wait for a bit to avoid overwhelming the server

    """
    This is the main response from the board, an array consisting of 
    [[raw data 1], [raw data 2], ..., [timestamps]]. First part is the direct *raw* reads of the 
    first ADC, channel 0. Last part is the corresponding timestamp of each sample.
    """
    readout = np.array(all_data_rows + [time_row])
    # print(readout)

    data_rows = readout[:-1]
    avg_data = np.mean(data_rows, axis = 0) # get the average over all experiments to increase SNR
    time_row = readout[-1] * 1e3 # the board sends the data in us, we turn it to ns
    
    result = np.vstack([data_rows, avg_data, time_row])
    
    # store the files with the timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename =  f"readout_{timestamp}.txt"
    WriteToTXT(result, filename)
    
    PlotReadout(result, timestamp, number_of_experiments)
    
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