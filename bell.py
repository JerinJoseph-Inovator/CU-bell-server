#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os

relay_pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)

# Function to simulate ringing the bell
def ring_bell(duration):
    GPIO.output(relay_pin, GPIO.HIGH)
    print(f"Bell ringing for {duration} seconds", flush=True)
    time.sleep(duration)
    print("Bell stopped", flush=True)
    GPIO.output(relay_pin, GPIO.LOW)

saturday_timings = [
    "08:55:00", "09:00:00", "09:55:00", "10:00:00", "10:55:00", "11:00:00",
    "11:55:00", "12:00:00", "12:55:00"
]
weekday_timings = [
    "08:55:00", "09:00:00", "09:55:00", "10:00:00", "10:55:00", "11:00:00",
    "11:55:00", "12:00:00", "12:55:00", "13:00:00", "13:55:00", "14:00:00",
    "14:55:00", "15:00:00", "15:55:00"
]
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Function to process the latest events file
def process_latest_events(input_file):
    date_events = {}
    immediate_ring = False
    specific_time_event = None

    with open(input_file, 'r') as infile:
        for line in infile:
            line = line.strip()
            if line:
                parts = line.split(',')
                event_type = int(parts[0])

                if event_type == 0:
                    if len(parts) == 2:
                        # Single-day holiday
                        date_str = parts[1]
                        date_events[date_str] = {'event': (event_type, None, None)}
                    elif len(parts) == 3:
                        # Range-based holiday
                        try:
                            start_date = datetime.strptime(parts[1], "%d-%m-%Y")
                            end_date = datetime.strptime(parts[2], "%d-%m-%Y")
                            current = start_date
                            while current <= end_date:
                                date_str = current.strftime("%d-%m-%Y")
                                date_events[date_str] = {'event': (event_type, None, None)}
                                current += timedelta(days=1)
                        except ValueError as ve:
                            print(f"Invalid date format in line: {line} -> {ve}")
                    else:
                        print(f"Invalid holiday line format: {line}")
                elif event_type in (1, 2):  # MID SEM or END SEM
                    slot = int(parts[1])
                    date_str = parts[2]
                    event_time = parts[3] if len(parts) > 3 else None
                    print(f"Detected event: Type {event_type}, Slot {slot}, Date {date_str}, Time {event_time}")

                    if date_str not in date_events or date_events[date_str].get('event', (None,))[0] != 0:
                        if date_str not in date_events:
                            date_events[date_str] = {}
                        date_events[date_str][slot] = (event_type, event_time)
                elif event_type == 3:
                    specific_time_event = parts[1]
                    immediate_ring = True

    return date_events, immediate_ring, specific_time_event

# Offsets for MID SEM and END SEM
midsem_offsets = {
    1: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=2, minutes=5), timedelta(hours=2, minutes=15)],
    2: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=2, minutes=5), timedelta(hours=2, minutes=15)],
    3: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=2, minutes=5), timedelta(hours=2, minutes=15)]
}

endsem_offsets = {
    1: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=3, minutes=5), timedelta(hours=3, minutes=15)],
    2: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=3, minutes=5), timedelta(hours=3, minutes=15)],
    3: [timedelta(minutes=0), timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=3, minutes=5), timedelta(hours=3, minutes=15)]
}

# Function to calculate bell times
def calculate_bell_times(base_time_str, offsets):
    base_time = datetime.strptime(base_time_str, "%H:%M:%S")
    return [(base_time + offset).strftime("%H:%M:%S") for offset in offsets]

# Main loop
def main_loop():
    print("Starting the main loop...")

    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M:%S")
        current_date = now.strftime("%d-%m-%Y")
        current_weekday = now.strftime("%A")

        print(f"Checking events at {current_time_str} on {current_date} ({current_weekday})")

        date_events, immediate_ring, specific_time_event = process_latest_events("/home/pi/Desktop/server/final.txt")

        
        if immediate_ring:
            print(f"Immediate bell ring triggered at {current_time_str}")
            ring_bell(3)

        is_special_day = current_date in date_events and any(
            isinstance(slot_data, tuple) and slot_data[0] in (1, 2)
            for slot_data in date_events[current_date].values()
        )
        print(f"specialday value ={is_special_day}")
        if current_date in date_events and 'event' in date_events[current_date] and date_events[current_date]['event'][0] == 0:
            print(f"Today ({current_date}) is a holiday. No bells will ring.")
        if not is_special_day:
            if current_weekday == "Sunday":
                time.sleep(60)
                continue

            if current_weekday == "Saturday" and current_time_str in saturday_timings:
                ring_bell(3)

            if current_weekday in weekdays and current_time_str in weekday_timings:
                ring_bell(3)

        if current_date in date_events and ('event' not in date_events[current_date] or date_events[current_date]['event'][0] != 0):
            
        
            for slot, (event_type, event_time) in date_events[current_date].items():
                if event_time:
                    if event_type == 1:
                        offsets = midsem_offsets
                    elif event_type == 2:
                        offsets = endsem_offsets
                        
                    elif event_type == 0:
                        time.sleep(1)
                    else:
                        continue  # Ignore unknown event types

                    print(f"Processing Slot: {slot}, Base Time: {event_time}")
                    result_times = calculate_bell_times(event_time, offsets.get(slot, []))
                    print(f"Computed Bell Times: {result_times}")

                    if current_time_str in result_times:
                        ring_bell(3)

        time.sleep(1)

# Run the main loop
main_loop()
 
