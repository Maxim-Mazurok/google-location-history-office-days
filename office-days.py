import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import calendar
import pytz
from datetime import timedelta, datetime, date

# File containing arrival and departure logs
output_file_path = "data/arrivals_departures.txt"

# Initialize timezone and data structures
sydney_tz = pytz.timezone('Australia/Sydney')
time_spent_per_day = {}

# Parse the attendance data from the file
with open(output_file_path, 'r') as output_file:
    for line in output_file:
        if "Arrived at" in line:
            start_time = datetime.fromisoformat(line.strip().split("Arrived at ")[1]).astimezone(sydney_tz)
        elif "Left at" in line:
            end_time = datetime.fromisoformat(line.strip().split("Left at ")[1]).astimezone(sydney_tz)
            # Calculate duration and add to the corresponding day
            duration = (end_time - start_time).total_seconds() / 3600  # in hours
            day = start_time.date()
            if day not in time_spent_per_day:
                time_spent_per_day[day] = 0
            time_spent_per_day[day] += duration

# Define the start and end dates of the fiscal year FY23-24
fy_start_date = date(2023, 7, 1)
fy_end_date = date(2024, 6, 30)

# Count the number of days with attendance greater than 2 hours during the FY23-24
days_at_office_more_than_2h = sum(
    1 for day, hours in time_spent_per_day.items()
    if fy_start_date <= day <= fy_end_date and hours > 2
)

# Calculate the total hours spent in the office during FY23-24
total_hours_at_office = sum(
    hours for day, hours in time_spent_per_day.items()
    if fy_start_date <= day <= fy_end_date
)

print(f"Number of days at the office >2h in FY23-24: {days_at_office_more_than_2h}")
print(f"Total hours spent at the office in FY23-24: {total_hours_at_office}")
