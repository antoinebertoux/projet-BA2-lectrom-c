import turtle
import random

turtle.setup(500,500)
t = turtle.Turtle()
t.speed(3)
t.color('black')
t.hideturtle()

def drawCircle(position, diameter):
    t.setpos(position)
    t.pendown()
    t.begin_fill()
    t.circle(diameter)
    t.end_fill()
    t.penup()

def drawScotch():
    tube_list =[]
    t.right(90)
    t.pensize(1.6)
    for i in range(11):
        if i % 2 == 0:
            t.forward(20)
            tube_list.append(t.position())
            t.forward(50)
            tube_list.append(t.position())
            t.forward(20)
        else:
            t.forward(40)
        if i//2 % 2 == 0:
            t.left(90)
        else:
            t.right(90)
    t.penup()
    t.pensize(1)
    return tube_list

def drawTubes(tube_list):
    t.color('blue')
    lst = tube_list
    size_list = [3.2,3.2,4,4,5,5]
    for diameter in size_list:
        point = random.choice(lst)
        drawCircle(point, diameter)
        lst.remove(point)

def drawFrame():
    t.setpos(-58,19)
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
    
turtle.tracer(0, 0)
tube_list = drawScotch()
drawFrame()
drawTubes(tube_list)
turtle.update()
turtle.done()
