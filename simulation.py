import turtle
import random
import time

class Tube:
    def __init__(self, position, diameter):
        self.turt = turtle.Turtle()
        self.position = position
        self.diameter = diameter
        self.turt.hideturtle()  
        self.turt.color('blue')
        self.draw()
    def draw(self):
        self.turt.clear()
        drawCircle(self.position, self.diameter, self.turt)
    def setPosition(self, pos):
        self.position = pos
        self.draw()

class Car:
    def __init__(self, position, diameter):
        self.turt = turtle.Turtle()
        self.position = position
        self.diameter = diameter
        self.turt.hideturtle()
        self.turt.color('red')
        self.draw()
    def draw(self):
        self.turt.clear()
        drawCircle(self.position, self.diameter, self.turt)
    def setPosition(self, pos):
        self.position = pos
        self.draw()

def drawCircle(position, diameter, t):
    t.penup()
    t.setheading(0)
    t.setpos(position)
    t.pendown()
    t.begin_fill()
    t.circle(diameter)
    t.end_fill()
    t.penup()

def drawScotch():
    t.setpos(0,0)
    t.setheading(-90)
    tube_position_list =[]
    t.pensize(1.6)
    for i in range(11):
        if i % 2 == 0:
            t.forward(20)
            tube_position_list.append(t.position())
            t.forward(50)
            tube_position_list.append(t.position())
            t.forward(20)
        else:
            t.forward(40)
        if i//2 % 2 == 0:
            t.left(90)
        else:
            t.right(90)
    t.penup()
    t.pensize(1)
    return tube_position_list

def drawTubes(tube_position_list):
    lst = tube_position_list
    size_list = [3.2,3.2,4,4,5,5]
    tube_list = []
    for diameter in size_list:
        point = random.choice(lst)
        tube_list.append(Tube(point, diameter))
        lst.remove(point)
    return tube_list
    
def drawFrame():
    t.setpos(-58,19)
    t.setheading(0)
    t.pendown()
    t.forward(265)
    t.right(90)
    t.forward(132)
    t.right(90)
    t.forward(265)
    t.right(90)
    t.forward(132)
    t.right(90)
    t.penup()
    t.setpos(0,0)


turtle.setup(500,500)
t = turtle.Turtle()
t.speed(3)
t.color('black')
t.hideturtle()  
turtle.tracer(0, 0)
tube_position_list = drawScotch()
drawFrame()
tube_list = drawTubes(tube_position_list)
car = Car((0,0),10)
x =0
while True:
    car.setPosition((x,100))
    x+=3
    time.sleep(.1)
    turtle.update()
    
turtle.done()
