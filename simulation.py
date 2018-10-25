import turtle
import random

t = turtle.Turtle()
t.speed(3)
t.color('black')
t.hideturtle()

def drawCircle(position, diameter):
    t.setpos(position)
    t.pendown()
    t.circle(diameter)
    t.penup()

def drawScotch():
    tube_list =[]
    t.right(90)
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
    return tube_list

def drawTubes(tube_list):
    lst = tube_list
    size_list = [3.2,3.2,4,4,5,5]
    for diameter in size_list:
        point = random.choice(lst)
        drawCircle(point, diameter)
        lst.remove(point)
        
turtle.tracer(0, 0)
tube_list = drawScotch()
drawTubes(tube_list)
turtle.update()
turtle.done()
