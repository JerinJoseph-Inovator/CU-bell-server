#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import threading
import digitalio
import board
from adafruit_character_lcd.character_lcd import Character_LCD_Mono

# === GPIO Pin Configuration ===
LCD_RS = board.D17      # GPIO17 (Pin 11)
LCD_E = board.D27       # GPIO27 (Pin 13)
LCD_D4 = board.D22      # GPIO22 (Pin 15)
LCD_D5 = board.D23      # GPIO23 (Pin 16)
LCD_D6 = board.D24      # GPIO24 (Pin 18)
LCD_D7 = board.D25      # GPIO25 (Pin 22)
LCD_COLUMNS = 16
LCD_ROWS = 2

ROW = [board.D5, board.D6, board.D13, board.D19]  # GPIO5, GPIO6, GPIO13, GPIO19 (Pins 29, 31, 33, 35)
COL = [board.D12, board.D16, board.D20, board.D21]  # GPIO12, GPIO16, GPIO20, GPIO21 (Pins 32, 36, 38, 40)



# === System Variables ===
schedule_list = []  # Stores scheduled times
temp_time = None    # Temporarily holds entered time
lcd_updating = True # Controls whether the LCD updates in real-time
last_lcd_message = ""  # Variable to track the last LCD message
show_rtc = True  # Controls if real-time clock is shown
last_input_time = time.time()  # Track the last input time to handle inactivity
 
GPIO.setmode(GPIO.BCM)
relay_pin=4
GPIO.setup(relay_pin,GPIO.OUT)
# === GPIO Setup ===
lcd_rs = digitalio.DigitalInOut(LCD_RS)
lcd_rs.direction = digitalio.Direction.OUTPUT

lcd_e = digitalio.DigitalInOut(LCD_E)
lcd_e.direction = digitalio.Direction.OUTPUT

lcd_d4 = digitalio.DigitalInOut(LCD_D4)
lcd_d4.direction = digitalio.Direction.OUTPUT

lcd_d5 = digitalio.DigitalInOut(LCD_D5)
lcd_d5.direction = digitalio.Direction.OUTPUT

lcd_d6 = digitalio.DigitalInOut(LCD_D6)
lcd_d6.direction = digitalio.Direction.OUTPUT

lcd_d7 = digitalio.DigitalInOut(LCD_D7)
lcd_d7.direction = digitalio.Direction.OUTPUT

keypad_row = []
keypad_col = []

for pin in ROW:
    row = digitalio.DigitalInOut(pin)
    row.direction = digitalio.Direction.OUTPUT
    row.value = False
    keypad_row.append(row)

for pin in COL:
    col = digitalio.DigitalInOut(pin)
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.DOWN
    keypad_col.append(col)

lcd = Character_LCD_Mono(lcd_rs, lcd_e, lcd_d4, lcd_d5, lcd_d6, lcd_d7, LCD_COLUMNS, LCD_ROWS)

KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# === Functions ===
def update_lcd(text):
    """
    Updates the LCD with the given text only if the content has changed.
    """
    global last_lcd_message
    if text != last_lcd_message:
        lcd.clear()  # Clear LCD only if the content changes
        lcd.message = text
        last_lcd_message = text

def read_keypad():
    """
    Scans the keypad and returns the pressed key. Returns None if no key is pressed.
    """
    for i, row_pin in enumerate(keypad_row):
        row_pin.value = True
        for j, col_pin in enumerate(keypad_col):
            if col_pin.value:
                row_pin.value = False
                return KEYPAD[i][j]
        row_pin.value = False
    return None

def real_time_clock():
    """
    Continuously updates the LCD with the current time, if the real-time clock is enabled.
    """
    global show_rtc
    while lcd_updating:
        if show_rtc:
            current_time = datetime.now()
            update_lcd(current_time.strftime("%H:%M:%S\n%d-%m-%Y"))
        time.sleep(1)

def ring_bell():
    GPIO.output(relay_pin,GPIO.HIGH)
    time.sleep(5)
    GPIO.output(relay_pin,GPIO.LOW)


def check_schedule():
    """
    Checks the schedule list every second and rings the bell
    if the current time matches any scheduled time.
    """
    global schedule_list
    while lcd_updating:
        # Get current time with seconds
        current_time = datetime.now().strftime("%H:%M:%S")
        
        for scheduled_time in schedule_list[:]:  # Iterate over a copy of the list
            if scheduled_time.strftime("%H:%M:%S") == current_time:
                update_lcd(f"Bell Ringing\n{current_time}")
                ring_bell()
                schedule_list.remove(scheduled_time)  # Remove the matched time
        
        time.sleep(1)  # Check every second

def handle_mode_selection():
    """
    Handles the modes displayed when 'A' is pressed.
    """
    global show_rtc
    while True:
        update_lcd("1:Enter Time\nB:Confirm\nC:Clear Schedule")
        key = read_keypad()
        if key == '1':
            enter_time_mode()
        elif key == 'B':
            confirm_schedule()
        elif key == 'C':
            clear_schedule()
        elif key == "4":
            show_rtc = True
        elif key == "D":
            ring_bell()
        elif key == '*':  # Exit modes
            update_lcd("Exiting Modes")
            time.sleep(2)
            show_rtc = True  # Show real-time clock again after exiting modes
            break
        

def enter_time_mode():
    """
    Mode to input time via the keypad.
    """
    global show_rtc, temp_time
    show_rtc = False  # Hide real-time clock when entering time
    update_lcd("Enter time (min):")
    input_time = ''
    while True:
        key = read_keypad()
        if key is None:
            continue
        if key == '#':  # Confirm input
            break
        elif key == '*':  # Cancel input
            input_time = input_time[:-1]
            update_lcd(f"Time {input_time} min")
            time.sleep(0.5)
            
        elif key.isdigit():  # Append digits to input
            input_time += key
            update_lcd(f"Time: {input_time} min")
            time.sleep(0.5)
    
    if input_time.isdigit() and int(input_time) > 0:
        temp_time = int(input_time)
        update_lcd("Press B to confirm")
    else:
        update_lcd("Invalid Time")
        temp_time = None
        time.sleep(2)

def confirm_schedule():
    """
    Confirms and saves the entered time to the schedule.
    """
    global temp_time
    if temp_time is not None:
        future_time = datetime.now() + timedelta(minutes=temp_time)
        schedule_list.append(future_time)
        update_lcd(f"Set for: {future_time.strftime('%H:%M')}")
        temp_time = None
    else:
        update_lcd("No Time Entered!")
    time.sleep(2)

def clear_schedule():
    """
    Clears all scheduled tasks.
    """
    global schedule_list
    schedule_list.clear()
    update_lcd("Schedule Cleared")
    time.sleep(2)

# === Main Program ===
def main():
    global lcd_updating, show_rtc, last_input_time
    # Start real-time clock and schedule checking threads
    threading.Thread(target=real_time_clock, daemon=True).start()
    threading.Thread(target=check_schedule, daemon=True).start()

    # Ensure LCD is initialized with a short delay
    time.sleep(2)

    try:
        while True:
            # Check if 30 seconds have passed since last keypress
            current_time = time.time()


            # Show RTC or handle keypresses
            if show_rtc:
                key = read_keypad()
                if key == 'A':
                    show_rtc = False  # Hide RTC and show modes
                    handle_mode_selection()
                elif key == '*':
                    update_lcd("Goodbye!")
                    break
                elif key:  # Any key press updates the last input time
                    last_input_time = current_time
                    break
                elif key == 'D':
                    ring_bell()
                    break
                 

            time.sleep(0.1)  # Prevent busy-wait loop
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        # Cleanup and stop LCD updates
        lcd_updating = False
        lcd.clear()
        print("Program Exiting")

# Run the main function
if __name__=="__main__":
    while True:
        main()
        time.sleep(2)

