#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import csv

def parse_event_line(line):
    parts = line.strip().split(',')
    event_type = int(parts[0])
   
    if event_type in (1, 2):  # Mid-semester or End-semester
        slot = int(parts[1])
        start_date = datetime.strptime(parts[2], "%d-%m-%Y")
       
        if len(parts) > 4:
            end_date = datetime.strptime(parts[3], "%d-%m-%Y")
            event_time = datetime.strptime(parts[4], "%H:%M:%S").time()
        elif len(parts) > 3:
            try:
                end_date = datetime.strptime(parts[3], "%d-%m-%Y")
                event_time = None
            except ValueError:
                end_date = start_date
                event_time = datetime.strptime(parts[3], "%H:%M:%S").time()
        else:
            end_date = start_date
            event_time = None
       
        return event_type, slot, start_date, end_date, event_time
   
    else:  # Holiday
        start_date = datetime.strptime(parts[1], "%d-%m-%Y")
        end_date = datetime.strptime(parts[2], "%d-%m-%Y") if len(parts) > 2 else start_date
        return event_type, None, start_date, end_date, None

def read_and_process_events(input_file, log_file):
    event_dict = {}
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # Create a new list to store valid lines
        valid_lines = []

        for line in lines:
            try:
                event_type, slot, start_date, end_date, event_time = parse_event_line(line)
                for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
                    if event_type == 0:  # Holiday, override all events on this date
                        event_dict[single_date] = {None: (event_type, None)}
                    else:
                        # If the date already has a holiday, skip adding other events
                        if single_date not in event_dict or None not in event_dict[single_date]:
                            if single_date not in event_dict:
                                event_dict[single_date] = {}
                            event_dict[single_date][slot] = (event_type, event_time)
                valid_lines.append(line)  # Only add valid lines to the list
            except Exception as e:
                print(f"Error parsing line '{line}': {e}")
                # Log the error to the log file
                with open(log_file, 'a') as log:
                    log.write(f"Error parsing line: {line}Error: {e}\n")
                # Skip the problematic line, effectively deleting it from the file
                continue

        # Rewrite the file with valid lines only (no errors)
        with open(input_file, 'w') as file:
            file.writelines(valid_lines)

    except Exception as e:
        print(f"Error reading file {input_file}: {e}")

    return event_dict


def write_latest_events(event_dict, output_file):
    try:
        with open(output_file, 'w') as file:
            for date in sorted(event_dict.keys()):
                events = event_dict[date]
                if None in events:
                    event_type, _ = events[None]
                    file.write(f"{event_type},{date.strftime('%d-%m-%Y')}\n")
                else:
                    for slot, (event_type, event_time) in sorted(events.items()):
                        if event_type in (1, 2):
                            file.write(f"{event_type},{slot},{date.strftime('%d-%m-%Y')},{event_time.strftime('%H:%M:%S') if event_time else ''}\n")
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")

def calculate_bell_times(base_time, offsets):
    return [base_time + offset for offset in offsets]

def write_to_csv(event_dict, csv_file):
    try:
        with open(csv_file, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(["Type", "Date", "Timings"])  # CSV header

            mid_offsets = [timedelta(minutes=15), timedelta(minutes=30), timedelta(hours=2, minutes=15), timedelta(hours=2, minutes=30)]
            end_offsets = [timedelta(minutes=15), timedelta(minutes=30), timedelta(hours=3), timedelta(hours=3, minutes=30)]

            for date, events in sorted(event_dict.items()):
                date_str = date.strftime('%d-%m-%Y')
                if None in events:
                    csv_writer.writerow(["Holiday", date_str, "No bell ringing"])
                else:
                    for slot, (event_type, event_time) in events.items():
                        if event_time:
                            base_time = datetime.combine(date, event_time)
                            if event_type == 1:
                                all_timings = [base_time.strftime('%H:%M:%S')] + [t.strftime('%H:%M:%S') for t in calculate_bell_times(base_time, mid_offsets)]
                                csv_writer.writerow([ "Midsem", date_str, ", ".join(all_timings)])
                            elif event_type == 2:
                                all_timings = [base_time.strftime('%H:%M:%S')] + [t.strftime('%H:%M:%S') for t in calculate_bell_times(base_time, end_offsets)]
                                csv_writer.writerow([ "Endsem", date_str, ", ".join(all_timings)])
    except Exception as e:
        print(f"Error writing to CSV file {csv_file}: {e}")


input_file = "/home/pi/Desktop/server/input.txt"
output_file = "/home/pi/Desktop/server/final.txt"
csv_file = "/home/pi/Desktop/server/bell_events.csv"
log_file = "/home/pi/Desktop/server/log_txt.txt"  # Path to the log file
event_dict = read_and_process_events(input_file, log_file)
# Saving in CSV instead of Excel

write_latest_events(event_dict, output_file)
write_to_csv(event_dict, csv_file)  # Writing the event data to CSV