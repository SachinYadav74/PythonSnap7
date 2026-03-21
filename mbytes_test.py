from flask import Flask, request
import os, webbrowser, threading, datetime, signal, json, psutil, re, glob, sys, win32event, win32api, winerror
from snap7 import Area
import snap7
from snap7.util import set_int,get_bool, set_bool

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()
# Establishing PLC Connection
client = snap7.client.Client()
try:
    client.connect('192.168.0.1', 0, 1)
    if client:
        print("Connected ")
except Exception as e:
    print("Error Occured Connecting to PLC: ", e)
read_type = []

color = "ON / OFF"

def execute_python_function():
    print("Executed")

db_number = 0
db_byteindex = 0
db_bitindex = 0

data_address = {'db_number':1, 'db_byteindex':1, 'db_bitindex':1}

def read_memory_byte(plc, byte_index):
    data = plc.read_area(Area.MK, 0, byte_index,1)
    # bitvalue = get_bool(data, 0)
    bytevalue=data[0]
    print(f"MB{byte_index} value: ", bytevalue)
    return bytevalue

def write_memory_byte(plc, byte_index, value):
    data = bytearray([value])
    plc.write_area(Area.MK, 0, byte_index, data)
    print(f"MB{byte_index} value set to: ", value)
    return str(value)

 
def render_page(statusColor):
    # print('The color is ', statusColor)
    html_page = f"""
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PLC and Python Snap7 Demo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 0;
        }}

        .navbar {{
            background-color: #114b8b;
            padding: 15px 30px;
            color: white;
            font-size: 20px;
            text-align: left;
            font-weight: bold;            
            position: fixed;
            width: 2000px;
        }}

        .container {{
            padding: 40px;
            max-width: 1000px;
            margin: auto;
        }}

        h1 {{
            text-align: center;
            color: #114b8b;
            margin: 80px;
            padding: 10;
        }}

        .form-section, .status-section {{
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            margin-top: 10px;
        }}

        select, input[type="time"], input[type="number"], input[type="text"]  {{
            padding: 8px;
            margin-top: 5px;
            width: 100%;
            max-width: 300px;
        }}

            input[type="text"]  {{
            padding: 8px;
            margin-top: 5px;
            width: 100%;
            max-width: 700px;
        }}
        
        .form-grid {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .half {{
            flex: 1;
            min-width: 300px;
        }}

        button {{
            margin-top: 20px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }}

        .stop-btn {{
            background-color: #d9534f;
        }}

        .file-upload {{
            margin-top: 20px;
        }}

        .current-time {{
            margin-top: 10px;
        }}

        .status-box {{
            background-color: #e9f2ff;
            padding: 15px;
            border-radius: 5px;
        }}
        #logContent {{
            white-space: pre-wrap;
            background: #222;
            color: #0f0;
            padding: 15px;
            border-radius: 5px;
            max-height: 500px;
            overflow-y: auto;
            }}
    </style>
</head>
<body>
    <div class="navbar">   Python Dashboard for PLC</div>
    <div class="container">
        <h1>Read and Write PLC Memory Bytes from Website with Python</h1>
        <div class="form-section">
            <form method="POST" action="/trigger">
                <div class="form-grid">
                    <div class="half">
                       
                        <label for="db_byteindex">Memory Byte Index </label><input id="db_byteindex" name="db_byteindex" value=1 required>
                        <label for="db_value">Memory Byte Value </label><input id="db_value" name="db_value" value=1 required>
                        <button type="submit">Trigger</button>
                    </div>
                </div>
            </form>
        </div>
        <div class="form-section">
            <form id="getstatus" method="POST" action="/get-status">
                <div class="form-grid">
                    <div class="half">
                        <p><b>MB{data_address["db_byteindex"]}</b> Status: </p><h1 id="db_bit_status">{statusColor}</h1>
                        <button type="submit">Get Status</button>
                    </div>
                </div>
            </form>
        </div>
       
    <script>
        function loadvalue(){{
            value = document.getElementById('db_bit_status').textContent
            console.log(value)
            if (value=='OFF'){{
                document.getElementById('db_bit_status').style.backgroundColor="Red";
                console.log(value)
            }}
            if (value=='ON'){{
                document.getElementById('db_bit_status').style.backgroundColor="Green";
            }}
        }}
        function autosubmittingform(){{
            document.getElementById('getstatus').submit()
        }}
        setInterval(loadvalue, 1000)
    </script>
</body>
</html>
    """
    return html_page

@app.route("/", methods=["GET"])
def home():
    return render_page(statusColor=color)

@app.route("/status", methods=["POST"])
def schedule():
    return render_page()

@app.route("/trigger", methods=["POST"])
def trigger():
    data_address["db_byteindex"] = request.form.get("db_byteindex")
    data_address["db_bitindex"] = request.form.get("db_bitindex")
    db_value = request.form.get("db_value")
    # print(db_number, db_byteindex, db_bitindex, db_value)
    try:
        write_memory_byte(plc=client, byte_index=int(data_address["db_byteindex"] ), value=int(db_value))
    except Exception as e:
        print("Error Occured while writing Values in DB: ", e)
    return render_page(statusColor=color)

@app.route("/get-status", methods=["POST"])
def get_log():
    # print(data_address["db_number"] , data_address["db_byteindex"], data_address["db_bitindex"])
    try:
        # read_db_bit(plc=client, db_number=db_number, db_byteindex=db_byteindex, db_bitindex=db_bitindex)
        status = read_memory_byte(plc=client, byte_index=int(data_address["db_byteindex"]))
        return render_page(statusColor=status)
    except Exception as e:
        error = "Error Occured while reading logs. Error: ", e
        # return status, 404, {'Content-Type': 'text/plain'}
        return render_page(statusColor="")
        

@app.route("/shutdown")
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        os.kill(os.getpid(), signal.SIGINT)
        # sys.exit(0)
    else:
        func()
    return "Server shutting down..."

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()  
    # if mac_address_check:
    
    scheduler.add_job(get_log, 'interval', seconds=5)  
    app.run(debug=False)
