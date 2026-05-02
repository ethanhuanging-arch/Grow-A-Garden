import turtle
import random
import time
import json
import os

# ============================================================
# ---------------------- GAME STATE ---------------------------
# ============================================================

money = 0
seeds = 3
plants = []  # each: {"x","y","planted_at","stage","rarity"}

GROW_TIME = 5
SELL_PRICE = 10
MAX_PLANTS = 500  # crash protection

RARITIES = {
    1: "Common",
    2: "Uncommon",
    3: "Rare",
    4: "Epic",
    5: "Legendary",
    6: "Mythic",
    7: "Secret",
    8: "Godly",
    9: "Event",
    10: "OG",
    11: "Owner"
}

SAVE_FILE = "garden_save.json"

# ============================================================
# ---------------------- SAVE / LOAD --------------------------
# ============================================================

def save_game():
    data = {
        "money": money,
        "seeds": seeds,
        "GROW_TIME": GROW_TIME,
        "SELL_PRICE": SELL_PRICE,
        "plants": plants
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global money, seeds, GROW_TIME, SELL_PRICE, plants

    if not os.path.exists(SAVE_FILE):
        return

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    money = data.get("money", 0)
    seeds = data.get("seeds", 0)
    GROW_TIME = data.get("GROW_TIME", 5)
    SELL_PRICE = data.get("SELL_PRICE", 10)
    plants = data.get("plants", [])

    # Fix old save files
    now = time.time()
    fixed = False

    for plant in plants:
        if "stage" not in plant:
            plant["stage"] = 3 if plant.get("grown", False) else 0
            fixed = True
        if "rarity" not in plant:
            plant["rarity"] = "Common"
            fixed = True
        if "planted_at" not in plant:
            plant["planted_at"] = now
            fixed = True
        if "grown" in plant:
            del plant["grown"]
            fixed = True

    # Trim if too many plants
    if len(plants) > MAX_PLANTS:
        plants = plants[:MAX_PLANTS]
        fixed = True

    if fixed:
        save_game()

def autosave_loop():
    save_game()
    screen.ontimer(autosave_loop, 5000)

# ============================================================
# ---------------------- UI CONSTANTS -------------------------
# ============================================================

SELL_X1, SELL_Y1 = -380, 150
SELL_W, SELL_H = 120, 40

SHOP_X1, SHOP_Y1 = -380, 90
SHOP_W, SHOP_H = 120, 40

GARDEN_X1, GARDEN_X2 = -200, 380
GARDEN_Y1, GARDEN_Y2 = -250, 250

# ============================================================
# ---------------------- SCREEN SETUP -------------------------
# ============================================================

screen = turtle.Screen()
screen.setup(800, 600)
screen.title("Grow A Garden - Organized Edition")
screen.tracer(0)

ui_t = turtle.Turtle(visible=False)
ui_t.penup()

plant_t = turtle.Turtle(visible=False)
plant_t.penup()

button_t = turtle.Turtle(visible=False)
button_t.penup()

# ============================================================
# ---------------------- DRAWING ------------------------------
# ============================================================

def draw_button(x, y, w, h, text):
    button_t.penup()
    button_t.goto(x, y)
    button_t.pendown()

    button_t.color("black")
    button_t.fillcolor("gray")

    button_t.begin_fill()
    for _ in range(2):
        button_t.forward(w)
        button_t.right(90)
        button_t.forward(h)
        button_t.right(90)
    button_t.end_fill()

    button_t.penup()
    cx = x + w/2
    cy = y - h/2 - 8
    button_t.goto(cx, cy)
    button_t.color("white")
    button_t.write(text, align="center", font=("Arial", 12, "bold"))

def draw_ui():
    ui_t.clear()
    ui_t.goto(-380, 250)
    ui_t.write(f"Money: ${money}", font=("Arial", 16))

    ui_t.goto(-380, 220)
    ui_t.write(f"Seeds: {seeds}", font=("Arial", 14))

    draw_button(SELL_X1, SELL_Y1, SELL_W, SELL_H, "SELL")
    draw_button(SHOP_X1, SHOP_Y1, SHOP_W, SHOP_H, "SHOP")

def rarity_color(r):
    colors = {
        "Common": "sienna",
        "Uncommon": "lightgreen",
        "Rare": "dodgerblue",
        "Epic": "violet",
        "Legendary": "gold",
        "Mythic": "red",
        "Secret": "black",
        "Godly": "midnight blue",
        "Event": "orange",
        "OG": "cyan",
        "Owner": "magenta"
    }
    return colors.get(r, "brown")

def draw_plants():
    plant_t.clear()

    for plant in plants:
        plant_t.goto(plant["x"], plant["y"])
        stage = plant["stage"]

        if stage == 0:
            plant_t.color("brown")
            plant_t.dot(8)
        elif stage == 1:
            plant_t.color("lightgreen")
            plant_t.dot(12)
        elif stage == 2:
            plant_t.color("green")
            plant_t.dot(16)
        elif stage == 3:
            plant_t.color(rarity_color(plant["rarity"]))
            plant_t.dot(22)

# ============================================================
# ---------------------- GAME LOGIC ---------------------------
# ============================================================

def grow_loop():
    now = time.time()
    changed = False

    for plant in plants:
        age = now - plant["planted_at"]

        if age >= GROW_TIME * 0.75 and plant["stage"] != 3:
            plant["stage"] = 3
            changed = True
        elif age >= GROW_TIME * 0.50 and plant["stage"] != 2:
            plant["stage"] = 2
            changed = True
        elif age >= GROW_TIME * 0.25 and plant["stage"] != 1:
            plant["stage"] = 1
            changed = True

    if changed:
        draw_plants()
        screen.update()

    screen.ontimer(grow_loop, 200)

def sell_plants():
    global money, plants
    new_list = []

    for plant in plants:
        if plant["stage"] == 3:
            money += SELL_PRICE
        else:
            new_list.append(plant)

    plants = new_list
    draw_ui()
    draw_plants()
    screen.update()

# ============================================================
# ---------------------- AUTO SELL ----------------------------
# ============================================================

def auto_sell_if_needed():
    if len(plants) >= 5:
        sell_plants()

# ============================================================
# ---------------------- SHOP SYSTEM --------------------------
# ============================================================

def open_seed_quantity_menu():
    global money, seeds

    ui_t.clear()
    ui_t.goto(-380, 250)
    ui_t.write(f"Money: ${money}", font=("Arial", 16))

    ui_t.goto(-380, 200)
    ui_t.write("BUY SEEDS", font=("Arial", 18, "bold"))

    ui_t.goto(-380, 160)
    ui_t.write("1) Buy 1 Seed ($1)", font=("Arial", 14))

    ui_t.goto(-380, 130)
    ui_t.write("2) Buy 10 Seeds ($5)", font=("Arial", 14))

    ui_t.goto(-380, 100)
    ui_t.write("3) Buy 50 Seeds ($20)", font=("Arial", 14))

    ui_t.goto(-380, 70)
    ui_t.write("4) Buy 100 Seeds ($35)", font=("Arial", 14))

    ui_t.goto(-380, 40)
    ui_t.write("5) Buy MAX Seeds", font=("Arial", 14))

    ui_t.goto(-380, 10)
    ui_t.write("6) Custom Amount", font=("Arial", 14))

    ui_t.goto(-380, -20)
    ui_t.write("Click an amount to buy", font=("Arial", 12, "italic"))

    buy1   = (-380, 380, 150, 180)
    buy10  = (-380, 380, 120, 150)
    buy50  = (-380, 380, 90, 120)
    buy100 = (-380, 380, 60, 90)
    buyMAX = (-380, 380, 30, 60)
    buyCUSTOM = (-380, 380, 0, 30)

    def quantity_click(x, y):
        global money, seeds

        # Buy 1
        if buy1[0] <= x <= buy1[1] and buy1[2] <= y <= buy1[3]:
            if money >= 1:
                money -= 1
                seeds += 1

        # Buy 10
        elif buy10[0] <= x <= buy10[1] and buy10[2] <= y <= buy10[3]:
            if money >= 5:
                money -= 5
                seeds += 10

        # Buy 50
        elif buy50[0] <= x <= buy50[1] and buy50[2] <= y <= buy50[3]:
            if money >= 20:
                money -= 20
                seeds += 50

        # Buy 100
        elif buy100[0] <= x <= buy100[1] and buy100[2] <= y <= buy100[3]:
            if money >= 35:
                money -= 35
                seeds += 100

        # Buy MAX (limited)
        elif buyMAX[0] <= x <= buyMAX[1] and buyMAX[2] <= y <= buyMAX[3]:
            if money >= 1:
                packs = money // 35
                max_seeds = int(packs * 100) + int((money - packs * 35))
                max_seeds = min(max_seeds, 5000)
                seeds += max_seeds
                money -= max_seeds

        # Custom amount
        elif buyCUSTOM[0] <= x <= buyCUSTOM[1] and buyCUSTOM[2] <= y <= buyCUSTOM[3]:
            amount = screen.textinput("Custom Amount", "How many seeds do you want to buy?")
            if amount and amount.isdigit():
                amount = int(amount)
                cost = amount * 1
                if money >= cost:
                    money -= cost
                    seeds += amount

        draw_ui()
        draw_plants()
        screen.update()
        screen.onclick(on_click)

    screen.onclick(quantity_click)

def open_shop():
    global money, seeds, GROW_TIME, SELL_PRICE

    ui_t.clear()
    ui_t.goto(-380, 250)
    ui_t.write(f"Money: ${money}", font=("Arial", 16))

    ui_t.goto(-380, 200)
    ui_t.write("SHOP MENU", font=("Arial", 18, "bold"))

    ui_t.goto(-380, 160)
    ui_t.write("1) Buy Seeds (choose amount)", font=("Arial", 14))

    ui_t.goto(-380, 130)
    ui_t.write("2) Fertilizer ($20) - Faster Growth", font=("Arial", 14))

    ui_t.goto(-380, 100)
    ui_t.write("3) Watering Can ($50) - Better Harvest", font=("Arial", 14))

    ui_t.goto(-380, 60)
    ui_t.write("Click an item to continue", font=("Arial", 12, "italic"))

    seed_area = (-380, 380, 150, 180)
    fert_area = (-380, 380, 120, 150)
    water_area = (-380, 380, 90, 120)

    def shop_click(x, y):
        global money, seeds, GROW_TIME, SELL_PRICE

        if seed_area[0] <= x <= seed_area[1] and seed_area[2] <= y <= seed_area[3]:
            open_seed_quantity_menu()
            return

        if fert_area[0] <= x <= fert_area[1] and fert_area[2] <= y <= fert_area[3]:
            if money >= 20:
                money -= 20
                GROW_TIME = max(1, GROW_TIME - 1)

        elif water_area[0] <= x <= water_area[1] and water_area[2] <= y <= water_area[3]:
            if money >= 50:
                money -= 50
                SELL_PRICE += 5

        draw_ui()
        draw_plants()
        screen.update()
        screen.onclick(on_click)

    screen.onclick(shop_click)

# ============================================================
# ---------------------- PLANTING -----------------------------
# ============================================================

def plant_seed(x, y):
    global seeds

    # Sell button
    if SELL_X1 <= x <= SELL_X1 + SELL_W and SELL_Y1 - SELL_H <= y <= SELL_Y1:
        sell_plants()
        return

    # Shop button
    if SHOP_X1 <= x <= SHOP_X1 + SHOP_W and SHOP_Y1 - SHOP_H <= y <= SHOP_Y1:
        open_shop()
        return

    # Garden bounds
    if not (GARDEN_X1 <= x <= GARDEN_X2 and GARDEN_Y1 <= y <= GARDEN_Y2):
        return

    if seeds <= 0:
        return

    if len(plants) >= MAX_PLANTS:
        return

    seeds -= 1

    rarity_roll = random.randint(1, 11)
    rarity = RARITIES[rarity_roll]

    plants.append({
        "x": x,
        "y": y,
        "planted_at": time.time(),
        "stage": 0,
        "rarity": rarity
    })

    auto_sell_if_needed()

    draw_ui()
    draw_plants()
    screen.update()

# ============================================================
# ---------------------- INPUT ROUTING ------------------------
# ============================================================

def on_click(x, y):
    plant_seed(x, y)

# ============================================================
# ---------------------- INIT --------------------------------
# ============================================================

load_game()
draw_ui()
draw_plants()

screen.onclick(on_click)
grow_loop()
autosave_loop()

screen.update()
screen.mainloop()
