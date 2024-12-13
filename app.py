import RPi.GPIO as GPIO
import time
import pandas as pd  # For handling Excel files
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(12, GPIO.OUT)  # Set pin 14 as output for relay
def relay_trigger():
    # Trigger the relay for 5 seconds
    GPIO.output(12, GPIO.HIGH)  # Turn the relay on
    time.sleep(5)  # Keep the relay on for 5 seconds
    GPIO.output(12, GPIO.LOW)  # Turn the relay off

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to log data to a file
def log_to_file(filename, data):
    with open(filename, 'a') as file:
        file.write(data + '\n')

# Function to format received data
def format_data(data):
    if isinstance(data, dict) and "mode" in data:
        mode = data.get("mode")

        # Case 1: {mode: '0', date: 'dd/mm/yyyy'}
        if mode == '0' and "date" in data:
            date_str = data.get("date")
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            formatted_date = date_obj.strftime("%d-%m-%Y")
            return f"{mode},{formatted_date}"

        # **Fixed Case 2**: {mode: '0', startDate: 'dd/mm/yyyy', endDate: 'dd/mm/yyyy'}
        elif mode == '0' and "startDate" in data and "endDate" in data:
            start_date_str = data.get("startDate")
            end_date_str = data.get("endDate")
            start_date_obj = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date_obj = datetime.strptime(end_date_str, "%d/%m/%Y")
            formatted_start_date = start_date_obj.strftime("%d-%m-%Y")
            formatted_end_date = end_date_obj.strftime("%d-%m-%Y")
            return f"{mode},{formatted_start_date},{formatted_end_date}"

        # Case 3: {mode: '1', slot: 'X', start date: 'dd/mm/yyyy', end date: 'dd/mm/yyyy', start_time: 'hh:mm:ss'}
        elif mode == '1' and "slot" in data and "start date" in data and "end date" in data and "start_time" in data:
            slot = data.get("slot")
            start_date_str = data.get("start date")
            end_date_str = data.get("end date")
            start_time_str = data.get("start_time")
            start_date_obj = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date_obj = datetime.strptime(end_date_str, "%d/%m/%Y")
            start_time_obj = datetime.strptime(start_time_str, "%H:%M:%S")
            formatted_start_date = start_date_obj.strftime("%d-%m-%Y")
            formatted_end_date = end_date_obj.strftime("%d-%m-%Y")
            formatted_start_time = start_time_obj.strftime("%H:%M:%S")
            return f"{mode},{slot},{formatted_start_date},{formatted_end_date},{formatted_start_time}"

        # **Fixed Case 4**: {mode: '2', slot: 'X', date: {list of 'dd/mm/yyyy'}, start_time: 'hh:mm:ss'}
        elif mode == '2' and "slot" in data and "date" in data and "start_time" in data:
            slot = data.get("slot")
            date_field = data.get("date")
            start_time_str = data.get("start_time")

            # Extract and format dates from dictionary or list
            if isinstance(date_field, dict):
                dates = list(date_field.keys())  # Extract dictionary keys as a list
            elif isinstance(date_field, list):
                dates = date_field  # Use directly if list
            else:
                return None  # Invalid format

            # Format all dates and sort them
            formatted_dates = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, "%d/%m/%y")  # Adjust for two-digit year
                formatted_dates.append(date_obj.strftime("%d-%m-%Y"))

            # Sort dates for consistent order and join with commas
            formatted_dates_str = ",".join(sorted(formatted_dates))
            start_time_obj = datetime.strptime(start_time_str, "%H:%M:%S")
            formatted_start_time = start_time_obj.strftime("%H:%M:%S")
            return f"{mode},{slot},{formatted_dates_str},{formatted_start_time}"

    # Return None if the format is not recognized
    return None

@app.route('/holiday', methods=['GET', 'POST'])
def handle_holiday():
    data = request.json
    print('Holiday Data Received:', data)
    formatted_data = format_data(data)
    if formatted_data:
        log_to_file('input.txt', formatted_data)
    else:
        log_to_file('input.txt', str(data))
    return jsonify({"status": "success", "message": "Holiday data received"}), 200

@app.route('/midsem', methods=['GET', 'POST'])
def handle_midsem():
    data = request.json
    print('Midsem Data Received:', data)
    formatted_data = format_data(data)
    if formatted_data:
        log_to_file('input.txt', formatted_data)
    else:
        log_to_file('input.txt', str(data))
    return jsonify({"status": "success", "message": "Midsem data received"}), 200

@app.route('/endsem', methods=['GET', 'POST'])
def handle_endsem():
    data = request.json
    print('Endsem Data Received:', data)
    formatted_data = format_data(data)
    if formatted_data:
        log_to_file('input.txt', formatted_data)
    else:
        log_to_file('input.txt', str(data))
    return jsonify({"status": "success", "message": "Endsem data received"}), 200

@app.route('/emergency', methods=['GET', 'POST'])
def handle_emergency():
    data = request.json
    print('Emergency Signal Received:', data)
    formatted_data = format_data(data)
    if formatted_data:
        log_to_file('input.txt', formatted_data)
    else:
        log_to_file('input.txt', str(data))

    relay_trigger()

    return jsonify({"status": "success", "message": "Emergency signal received"}), 200

@app.route('/display', methods=['GET', 'POST'])
def display_data():
    try:
        # Define the file path to the CSV
        file_path = "bell_events.csv"

        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Check if required columns exist
        required_columns = ["Type", "Date", "Timings for bell"]
        for column in required_columns:
            if column not in df.columns:
                return jsonify({"status": "error", "message": f"Missing column: {column}"}), 500

        # Convert the DataFrame to a list of dictionaries
        data_json = []
        for _, row in df.iterrows():
            # Format the 'Date' column to ensure consistency
            try:
                date_value = datetime.strptime(row["Date"], "%d-%m-%Y").strftime("%d-%m-%Y")
            except ValueError:
                date_value = row["Date"]  # Keep original value if formatting fails

            # Append each row as a dictionary
            event = {
                "type": row["Type"],
                "date": date_value,
                "slot_times": row["Timings"]
            }
            data_json.append(event)
        # print(data_json)

        # Return the JSON response
        return jsonify(data_json), 200
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "CSV file not found"}), 500
    except pd.errors.EmptyDataError:
        return jsonify({"status": "error", "message": "CSV file is empty"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/schedule', methods=['GET', 'POST'])
def handle_schedule():
    data = request.json
    print('Schedule Data Received:', data)

    # Ensure the data is in the expected format (a single integer representing minutes)
    if isinstance(data, dict) and len(data) == 1 and isinstance(list(data.values())[0], int):
        minutes = list(data.values())[0]
        
        # Format the data to Seconds  (no need for complex date parsing)
        time_in_seconds = minutes * 60

        # Use a background thread to handle the delay
        import threading
        threading.Thread(target=lambda: (time.sleep(time_in_seconds), relay_trigger())).start()

        # Log the formatted data
        # log_to_file('input.txt', formatted_data)

        return jsonify({"status": "success", "message": "Schedule data received"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid data format for schedule"}), 400

@app.route('/', methods=['GET', 'POST'])
def display_msg():
    return jsonify({"message": "Server is running..."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=("selfsigned.pem", "selfsigned.pem"))
