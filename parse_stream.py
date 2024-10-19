import re
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import numpy as np
from math import radians, sin, cos, sqrt, asin
import os

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # haversine formula
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# File paths
file_path = "data/Records.json"
output_file_path = "data/arrivals_departures.txt"

# Coordinates and radius to compare
target_latitude = -33.1234
target_longitude = 151.1234
radius_km = 1

# Regular expressions to match lines for latitude, longitude, and timestamp
lat_regex = re.compile(r'"latitudeE7":\s*(-?\d+)', re.IGNORECASE)
lon_regex = re.compile(r'"longitudeE7":\s*(-?\d+)', re.IGNORECASE)
timestamp_regex = re.compile(r'"timestamp":\s*"([^"]+)"', re.IGNORECASE)

# Processing flags and temporary storage
latitude = None
longitude = None
in_range = False
start_time = None
record_count = 0

# Dictionary to store total time spent per day
time_spent_per_day = {}

# Sydney timezone
sydney_tz = pytz.timezone('Australia/Sydney')

# Check if the output file already exists
if not os.path.exists(output_file_path):
    # Process JSON file line by line
    with open(file_path, 'r') as file, open(output_file_path, 'w') as output_file:
        for line in file:
            # Try to find latitude, longitude, and timestamp
            lat_match = lat_regex.search(line)
            if lat_match:
                latitude = int(lat_match.group(1)) / 1e7
                continue

            lon_match = lon_regex.search(line)
            if lon_match:
                longitude = int(lon_match.group(1)) / 1e7
                continue

            timestamp_match = timestamp_regex.search(line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).astimezone(sydney_tz)
                record_count += 1

                if latitude is not None and longitude is not None:
                    # Calculate distance using the Haversine formula
                    distance = haversine(target_latitude, target_longitude, latitude, longitude)

                    if distance <= radius_km:
                        if not in_range:
                            in_range = True
                            start_time = timestamp
                            output_file.write(f"Arrived at {start_time}\n")
                    else:
                        if in_range:
                            in_range = False
                            end_time = timestamp
                            output_file.write(f"Left at {end_time}\n")

                            # Calculate duration and add to the corresponding day
                            duration = (end_time - start_time).total_seconds() / 3600  # in hours
                            day = start_time.date()
                            if day not in time_spent_per_day:
                                time_spent_per_day[day] = 0
                            time_spent_per_day[day] += duration

                # Reset latitude and longitude for the next record
                latitude = None
                longitude = None

                # Log progress every 1000 records
                if record_count % 1000 == 0:
                    print(f"Processed {record_count} records...")

    # If still in range by the end of the file
    if in_range:
        end_time = datetime.now(sydney_tz)
        output_file.write(f"Left at end of file ({end_time})\n")
        # Calculate duration and add to the corresponding day
        duration = (end_time - start_time).total_seconds() / 3600  # in hours
        day = start_time.date()
        if day not in time_spent_per_day:
            time_spent_per_day[day] = 0
        time_spent_per_day[day] += duration
else:
    print(f"Output file '{output_file_path}' already exists. Skipping processing...")
