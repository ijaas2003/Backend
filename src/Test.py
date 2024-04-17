from datetime import datetime, timedelta

# Get the current system time
systime = datetime.now()

# Add 30 minutes to the current system time
new_time = systime + timedelta(minutes=30)

print("Current System Time:", systime)
print("New Time after adding 30 minutes:", new_time)
