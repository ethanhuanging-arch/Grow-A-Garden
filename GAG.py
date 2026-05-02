import turtle
import time

money = 0
seeds = 3
plants = []

GROW_TIME = 5
SELL_PRICE = 10
SEED_COST = 5

screen = turtle.Screen()
screen.title("Grow A Garden - Turtle Edition")
screen.setup(800, 600)

ui_pen = turtle.Turtle()
ui_pen.hideturtle()
ui_pen.penup()

plant_pen = turtle.Turtle()
plant_pen.hideturtle()
plant_pen.penup()

button_pen = turtle.Turtle()
button_pen.hideturtle()
button_pen.penup()

def draw_button(x, y, w, h, text):
    button_pen.goto(x, y)
    button_pen.color("black")
    button_pen.begin_fill()
    for _ in range(2):
        button_pen.forward(w)
        button_pen.right(90)
        button_pen.forward(h)
        button_pen.right(90)
    button_pen.end_fill()

    button_pen.color("white")
    button_pen.goto(x + w/2, y - h/2 - 8)
    button_pen.write(text, align="center", font=("Arial", 14, "bold"))

def draw_ui():
    ui_pen.clear()
    ui_pen.goto(-380, 250)
    ui_pen.write(f"Money: ${money}", font=("Arial", 16, "bold"))

    ui_pen.goto(-380, 220)
    ui_pen.write(f"Seeds: {seeds}", font=("Arial", 16, "bold"))

    draw_button(-380, 150, 120, 40, "SELL")
    draw_button(-380, 90, 120, 40, "SHOP")

def draw_plants():
    plant_pen.clear()
    for plant in plants:
        plant_pen.goto(plant["x"], plant["y"])
        if plant["grown"]:
            plant_pen.color("green")
            plant_pen.dot(20)
        else:
            plant_pen.color("brown")
            plant_pen.dot(10)

def plant_seed(x, y):
    global seeds

    if -380 <= x <= -260 and 110 <= y <= 150:
        sell_plants()
        return

    if -380 <= x <= -260 and 50 <= y <= 90:
        open_shop()
        return

    if seeds <= 0:
        return

    seeds -= 1
    plants.append({
        "x": x,
        "y": y,
        "planted_at": time.time(),
        "grown": False
    })

    draw_ui()
    draw_plants()

def grow_loop():
    changed = False
    for plant in plants:
        if not plant["grown"] and time.time() - plant["planted_at"] >= GROW_TIME:
            plant["grown"] = True
            changed = True

    if changed:
        draw_plants()

    screen.ontimer(grow_loop, 500)

def sell_plants():
    global money, plants
    new_list = []
    harvested = 0

    for plant in plants:
        if plant["grown"]:
            harvested += 1
            money += SELL_PRICE
        else:
            new_list.append(plant)

    plants = new_list
    draw_ui()
    draw_plants()

def open_shop():
    global money, seeds

    ui_pen.goto(-380, 0)
    ui_pen.write("SHOP: Click to buy seed ($5)", font=("Arial", 14, "bold"))

    def buy_seed(x, y):
        nonlocal money, seeds
        if money >= SEED_COST:
            money -= SEED_COST
            seeds += 1
        draw_ui()
        screen.onclick(plant_seed)

    screen.onclick(buy_seed)

screen.onclick(plant_seed)

draw_ui()
draw_plants()
grow_loop()

screen.mainloop()
