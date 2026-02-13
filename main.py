from time_utils import time_to_seconds, seconds_to_time, seconds_to_float_hours, multiply_time

test_time = "07:35:00"

seconds = time_to_seconds(test_time)
print("Sekundy:", seconds)

converted_back = seconds_to_time(seconds)
print("Z powrotem:", converted_back)

print("Godziny (float):", seconds_to_float_hours(seconds))

print("\nTest mnożenia:")
time_result, float_result = multiply_time("07:35:00", 8)

print("HH:MM:SS:", time_result)
print("Godziny (float):", float_result)





