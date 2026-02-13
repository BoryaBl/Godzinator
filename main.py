from time_utils import time_to_seconds, seconds_to_time

test_time = "07:35:00"

seconds = time_to_seconds(test_time)
print("Sekundy:", seconds)

converted_back = seconds_to_time(seconds)
print("Z powrotem:", converted_back)
