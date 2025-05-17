#!/usr/bin/env python3
import time

# File paths
input_file = "/home/pi/Desktop/server/input.txt"
final_file = "/home/pi/Desktop/server/final.txt"

# Function to clear file contents
def clear_file(file_path):
    with open(file_path, "w") as file:
        pass  # Opening in write mode without writing anything clears the file

# Clear input.txt
clear_file(input_file)
print(f"Cleared contents of {input_file}")

# Wait for 2 seconds
time.sleep(2)

# Clear final.txt
clear_file(final_file)
print(f"Cleared contents of {final_file}")
