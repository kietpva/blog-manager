import turtle


# Exercise 16.10.2
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Point({self.x}, {self.y})"


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return (self.start == other.start and self.end == other.end) or (
            self.start == other.end and self.end == other.start
        )

    def midpoint(self):
        x = (self.start.x + self.end.x) / 2
        y = (self.start.y + self.end.y) / 2
        return Point(x, y)

    def draw(self):
        turtle.penup()
        turtle.goto(self.start.x, self.start.y)
        turtle.pendown()
        turtle.goto(self.end.x, self.end.y)


start1 = Point(0, 0)
start2 = Point(0, 0)
end = Point(200, 100)

line_a = Line(start1, end)
line_b = Line(start2, end)
line_c = Line(end, start1)
line_d = Line(start1, start2)

print(line_a == line_b)  # True
print(line_a == line_c)  # True
print(line_b == line_c)  # True
print(line_a == line_d)  # False


# Exercise 16.10.3
def make_turtle():
    turtle.setworldcoordinates(-50, -50, 350, 200)
    turtle.speed(0)


start = Point(0, 0)
end1 = Point(300, 0)
end2 = Point(0, 150)

line1 = Line(start, end1)
line2 = Line(start, end2)

mid1 = line1.midpoint()
print(mid1)  # Point(150.0, 0.0)

mid2 = line2.midpoint()
print(mid2)  # Point(0.0, 75.0)

line3 = Line(mid1, mid2)

make_turtle()

for shape in [line1, line2, line3]:
    shape.draw()

turtle.done()


# Exercise 16.10.4
class Rectangle:
    def __init__(self, width, height, corner):
        self.width = width
        self.height = height
        self.corner = corner  # bottom-left corner (Point)

    def make_lines(self):
        x = self.corner.x
        y = self.corner.y

        p1 = self.corner
        p2 = Point(x + self.width, y)
        p3 = Point(x + self.width, y + self.height)
        p4 = Point(x, y + self.height)

        return [
            Line(p1, p2),  # bottom
            Line(p2, p3),  # right
            Line(p3, p4),  # top
            Line(p4, p1),  # left
        ]

    def make_cross(self):
        lines = self.make_lines()

        # midpoints of each side
        midpoints = [line.midpoint() for line in lines]

        # opposite midpoints
        horizontal = Line(midpoints[3], midpoints[1])  # left ↔ right
        vertical = Line(midpoints[0], midpoints[2])  # bottom ↔ top

        return [horizontal, vertical]

    def midpoint(self):
        x = self.corner.x + self.width / 2
        y = self.corner.y + self.height / 2
        return Point(x, y)

    def draw(self):
        turtle.penup()
        turtle.goto(self.corner.x, self.corner.y)
        turtle.pendown()

        turtle.goto(self.corner.x + self.width, self.corner.y)
        turtle.goto(self.corner.x + self.width, self.corner.y + self.height)
        turtle.goto(self.corner.x, self.corner.y + self.height)
        turtle.goto(self.corner.x, self.corner.y)

    def draw2(self):
        for line in self.make_lines():
            line.draw()


def make_turtle():
    turtle.setup(800, 500)
    turtle.setworldcoordinates(0, 0, 200, 150)
    turtle.speed(0)
    turtle.hideturtle()


corner = Point(30, 20)
rectangle = Rectangle(100, 80, corner)

mid = rectangle.midpoint()
print(mid)  # Point(80.0, 60.0)

diagonal = Line(corner, mid)

make_turtle()

for shape in [rectangle, diagonal]:
    shape.draw()

turtle.done()


# Exercise 16.10.5
def make_turtle():
    turtle.setup(800, 500)
    turtle.setworldcoordinates(0, 0, 200, 150)
    turtle.speed(0)
    turtle.hideturtle()


corner = Point(30, 20)
rectangle = Rectangle(100, 80, corner)

lines = rectangle.make_cross()

make_turtle()

rectangle.draw()
for line in lines:
    line.draw()

turtle.done()
