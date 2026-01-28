# # Exercise 14.11.2
# def subtract_time(t1, t2):
#     """Returns the interval between two Time objects in seconds."""
#     seconds1 = t1.hour * 3600 + t1.minute * 60 + t1.second
#     seconds2 = t2.hour * 3600 + t2.minute * 60 + t2.second

#     return abs(seconds2 - seconds1)

# t1 = make_time(3, 2, 1)
# t2 = make_time(3, 2, 0)

# print(subtract_time(t1, t2))  # 1


# # Exercise 14.11.3
# class Time:
#     def __init__(self, hour=0, minute=0, second=0):
#         self.hour = hour
#         self.minute = minute
#         self.second = second


# def make_time(hour, minute, second):
#     return Time(hour, minute, second)


# def is_after(t1, t2):
#     """Checks whether `t1` is after `t2`."""
#     seconds1 = t1.hour * 3600 + t1.minute * 60 + t1.second
#     seconds2 = t2.hour * 3600 + t2.minute * 60 + t2.second

#     return seconds1 > seconds2


# print(is_after(make_time(3, 2, 1), make_time(3, 2, 0)))  # True
# print(is_after(make_time(3, 2, 1), make_time(3, 2, 1)))  # False
# print(is_after(make_time(11, 12, 0), make_time(9, 40, 0)))  # True

# # Exercise 14.11.2


def time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second


def subtract_time(t1, t2):
    return time_to_seconds(t1) - time_to_seconds(t2)


class Time:
    def __init__(self, hour, minute, second):
        self.hour = hour
        self.minute = minute
        self.second = second


t1 = Time(10, 30, 0)
t2 = Time(10, 0, 0)

print(subtract_time(t1, t2))


# Exercise 14.11.3
def make_time(hour, minute, second):
    return Time(hour, minute, second)


def is_after(t1, t2):
    """Checks whether `t1` is after `t2`."""
    seconds1 = t1.hour * 3600 + t1.minute * 60 + t1.second
    seconds2 = t2.hour * 3600 + t2.minute * 60 + t2.second

    return seconds1 > seconds2


print(is_after(make_time(3, 2, 1), make_time(3, 2, 0)))  # True
print(is_after(make_time(3, 2, 1), make_time(3, 2, 1)))  # False
print(is_after(make_time(11, 12, 0), make_time(9, 40, 0)))  # True


# Exercise 14.11.4
class Date:
    """Represents a year, month, and day"""


def make_date(year, month, day):
    d = Date()
    d.year = year
    d.month = month
    d.day = day
    return d


def print_date(d):
    print(f"{d.year:04d}-{d.month:02d}-{d.day:02d}")


def date_to_tuple(d):
    return (d.year, d.month, d.day)


def is_after(d1, d2):
    return date_to_tuple(d1) > date_to_tuple(d2)


# June 22, 1933
date1 = make_date(1933, 6, 22)
print_date(date1)  # 1933-06-22

# September 17, 1933
date2 = make_date(1933, 9, 17)

print(is_after(date2, date1))  # True
