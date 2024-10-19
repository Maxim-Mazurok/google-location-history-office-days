import json
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
radius_km = 0.15

# Processing flags and temporary storage
in_range = False
start_time = None
record_count = 0

# Dictionary to store total time spent per day
time_spent_per_day = {}

# Sydney timezone
sydney_tz = pytz.timezone('Australia/Sydney')

# Check if the output file already exists
if not os.path.exists(output_file_path):
    # Read the entire JSON file
    with open(file_path, 'r') as file, open(output_file_path, 'w') as output_file:
        data = json.load(file)
        for record in data.get("locations", []):
            # Extract latitude, longitude, and timestamp from root
            latitude = record.get("latitudeE7")
            longitude = record.get("longitudeE7")
            timestamp_str = record.get("timestamp")

            # If timestamp is not found in the root, look for it in the activity field
            if timestamp_str is None and "activity" in record:
                activities = record["activity"]
                if activities:
                    # Assuming we take the first activity's timestamp if there are multiple
                    timestamp_str = activities[0].get("timestamp")

            # Continue only if latitude, longitude, and timestamp are all present
            if latitude is None or longitude is None or timestamp_str is None:
                print("Warning: Skipping record with missing data: ", record)
                continue

            # Convert values
            latitude = latitude / 1e7
            longitude = longitude / 1e7
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).astimezone(sydney_tz)
            record_count += 1

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
