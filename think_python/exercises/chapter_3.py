# Exercise 3.11.2
def print_right(text):
    """
    Write a function named print_right that takes a string named text as a parameter and prints the string with enough leading spaces that the last letter of the string is in the 40th column of the display.

    Hint: Use the len function, the string concatenation operator (+) and the string repetition operator (*).
    """
    spaces = 40 - len(text)
    print(" " * spaces + text)


print_right("Monty")
print_right("Python's")
print_right("Flying Circus")


# Exercise 3.11.3
def triangle(text, height):
    """
    Here's an example of a pyramid with 5 levels, using the string 'L'.

    L
    LL
    LLL
    LLLL
    LLLLL
    """
    for i in range(1, height + 1):
        print(text * i)


triangle("L", 5)
triangle("N", 7)


# Exercise 3.11.4
def rectangle(text, width, height):
    """
    Here's an example of a rectangle with width 5 and height 4, made up of the string 'H'.

    HHHHH
    HHHHH
    HHHHH
    HHHHH
    """
    for _ in range(1, height + 1):
        print(text * width)


rectangle("H", 5, 4)


# Exercise 3.11.5
def print_bottles(n, end):
    if n == 1:
        print(f"{n} bottle of beer {end}")
    else:
        print(f"{n} bottles of beer {end}")


def bottle_verse(n):
    print_bottles(n, "on the wall")
    print_bottles(n, "")
    print("Take one down, pass it around")
    print_bottles(n - 1, "on the wall")


for n in range(99, 0, -1):
    bottle_verse(n)
