from time_utils import time_to_seconds, seconds_to_time, seconds_to_float_hours, multiply_time, calculate_time_expression, calculate_vacation_days

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

print("\nTest sumowania/odejmowania:")

times = ["01:30:00", "07:00:00", "06:00:00", "00:30:00"]
operators = ["+", "-", "+"]

time_result, float_result = calculate_time_expression(times, operators)

print("HH:MM:SS:", time_result)
print("Godziny (float):", float_result)

print("\nTest urlopu:")

vacation_days = calculate_vacation_days("13:00:00", "07:35:00")
print("Dni urlopu:", vacation_days)






