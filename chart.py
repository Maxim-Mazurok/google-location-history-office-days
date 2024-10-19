import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import calendar
import pytz
from datetime import timedelta, datetime

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

# Create a list of days with attendance data
days = sorted(time_spent_per_day.keys())
days_set = set(days)

# Determine the range of dates to display
start_date = min(days)
end_date = max(days)

# Adjust start_date to the previous Monday to align the matrix
start_date -= timedelta(days=start_date.weekday())

# Adjust end_date to the next Sunday to align the matrix
end_date += timedelta(days=(6 - end_date.weekday()))

current_date = start_date

# Calculate the matrix of weeks (7 columns per week)
attendance_matrix = []
week = [0] * 7  # Initialize a week with no attendance

while current_date <= end_date:
    weekday = current_date.weekday()
    if current_date in days_set:
        # Store the attendance duration in hours
        week[weekday] = time_spent_per_day[current_date]
    else:
        week[weekday] = 0  # No attendance

    if weekday == 6:  # End of the week (Sunday)
        attendance_matrix.append(week)
        week = [0] * 7  # Reset for the next week

    current_date += timedelta(days=1)

# Append the last week if not yet added
if any(week):
    attendance_matrix.append(week)

# Visualization
fig, ax = plt.subplots(figsize=(21, 12))  # Increase the figure size to make cells bigger

# Define the static color scale
color_scale = {
    0: '#ebedf0',     # wasn't there
    2: '#9be9a8',     # >= 2h
    4: '#40c463',     # >= 4h
    6: '#30a14e',     # >= 6h
    8: '#216e39'      # >= 8h
}

# Create a horizontal calendar-like grid
cols = len(attendance_matrix)  # Now the weeks are columns
rows = 7  # 7 days per week

for i, week in enumerate(attendance_matrix):
    for j, hours in enumerate(week):
        # Determine the color based on hours attended
        if hours >= 8:
            color = color_scale[8]
        elif hours >= 6:
            color = color_scale[6]
        elif hours >= 4:
            color = color_scale[4]
        elif hours >= 2:
            color = color_scale[2]
        else:
            color = color_scale[0]
        
        rect = patches.Rectangle((i, rows - j - 1), 1, 1, facecolor=color)  # Make cells bigger by increasing size
        ax.add_patch(rect)

# Set day names on y-axis
ax.set_yticks([rows - i for i in range(7)], minor=False)
ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], color='black')

# Set the month name and weeks on x-axis
x_labels = []
current_label_date = start_date
for _ in range(cols):
    month_name = calendar.month_abbr[current_label_date.month]
    day_number = current_label_date.day
    if current_label_date.day <= 7:
        x_labels.append(f"{month_name} {current_label_date.year % 100}")
    else:
        if current_label_date.day <= 7 and current_label_date.weekday() == 0:
            x_labels.append(f"{month_name} {current_label_date.year % 100}")
        else:
            x_labels.append("")
    current_label_date += timedelta(days=7)

ax.set_xticks(range(cols), minor=False)
ax.set_xticklabels(x_labels, rotation=45, ha='right', color='black', fontsize=10)

# Hide the axes and set limits
ax.set_xlim(0, cols)
ax.set_ylim(0, rows)
ax.set_aspect('equal')
ax.grid(True, which='major', color='white', linewidth=1)  # Increased linewidth to make grid lines larger

plt.show()
