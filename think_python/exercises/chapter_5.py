# Exercise 5.14.2
import time

# the total number of seconds since the Unix epoch until now.
total_seconds = int(time.time())

# the total number of seconds in a day
seconds_per_day = 24 * 60 * 60

# the remaining number of seconds in the current day
days = total_seconds // seconds_per_day

# the remaining number of seconds in the current day
remaining_seconds = total_seconds % seconds_per_day

# current time
hours = remaining_seconds // 3600
remaining_seconds = remaining_seconds % 3600

minutes = remaining_seconds // 60
seconds = remaining_seconds % 60

print("Days since Jan 1, 1970:", days)
print("Current time (UTC):", hours, ":", minutes, ":", seconds)


# Exercise 5.14.3
def is_triangle(a, b, c):
    if a > b + c or b > a + c or c > a + b:
        print("No")
    else:
        print("Yes")


is_triangle(3, 4, 5)
# Yes

is_triangle(1, 1, 12)
# No

is_triangle(2, 3, 5)
# Yes


# Exercise 5.14.4
# recurse(n=0, s=6)   ← is running print(s)
# recurse(n=1, s=5)
# recurse(n=2, s=3)
# recurse(n=3, s=0)
