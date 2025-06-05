from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__) # create a Flask app

# need a specific auth keyword to run, just a pinch of safety
@app.before_request
def check_token():
    if request.headers.get("auth") != "magnetism@ESB165":
        return jsonify({"error": "unauthorized"}), 401

# actual code that will be run if a request is sent to /run
@app.route('/run', methods=['POST'])
def run():
    try:
        # get the input parameters from the request body
        input_data = json.dumps(request.get_json()).encode()
        
        # call the main file as a subprocess, this is just for better handling on OS level
        proc = subprocess.run(
            ["python3", "main_pulser.py"],
            input = input_data, # send the parameters from the request body
            stdout = subprocess.PIPE, # get the output from the subprocess i.e. your main file
            stderr = subprocess.PIPE, # get the error
            timeout = 300 # wait for the response from the main file for 6000 secs
        )
        
        # if there is an error, return the error to the client
        if proc.returncode != 0:
            return jsonify({"error": "Script failed", "details": proc.stderr.decode()}), 500
        
        # if everything is OK, send the output of the main file
        result = json.loads(proc.stdout.decode())
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500) # expose to LAN
