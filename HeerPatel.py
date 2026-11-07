"""
ShopImpact - Conscious Shopping Dashboard (Year 1 Python Programming SA, Scenario 1)

A friendly companion that turns everyday shopping into an eco-conscious habit:
  * Onboarding flow that personalises the app (name, city, profession, meal prep yes/no)
  * Grocery list (to-do style) with buying advice and timed pop-up reminders
  * Meal-prep planner that pushes ingredients into the grocery list
  * CO2 impact dashboard, greener alternatives, badges and animated "turtle" drawings

Run with:  streamlit run app.py
All CO2 figures are SIMPLIFIED ESTIMATES for learning purposes, not scientific values.
"""
from __future__ import annotations

import html
import inspect
import json
import random
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from math import atan2, cos, pi, radians, sin

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ShopImpact", page_icon="🌿", layout="wide")
ss = st.session_state

# =============================================================================
# 1. STATIC DATA (dictionaries and lists)
# =============================================================================
LOW_MULT, HIGH_MULT = 0.8, 2.0   # <= LOW is "low impact", >= HIGH is "high impact"
MONTH_LIMIT = 30.0               # kg CO2 per month for the "Eco Saver" badge
SERVINGS = 2                     # every recipe is prepped as a batch of 2 servings
BEEF_BASELINE = 3.4              # kg CO2 per serving of a typical beef dinner

# product type -> (kg CO2e per currency unit spent, category).
# Simplified learning estimates: animal products and long-lived goods score high,
# plants, local produce, reusable and second-hand goods score low.
PRODUCTS = {
    "Beef": (5.5, "Food"), "Lamb": (4.8, "Food"), "Cheese": (3.0, "Food"),
    "Butter": (2.6, "Food"), "Pork": (2.4, "Food"), "Fish": (2.2, "Food"),
    "Chicken": (2.0, "Food"), "Ready meals": (1.7, "Food"), "Dairy milk": (1.6, "Food"),
    "Rice": (1.5, "Food"), "Eggs": (1.4, "Food"), "Coffee & tea": (1.8, "Food"),
    "Snacks & sweets": (1.2, "Food"), "Bread & pasta": (0.9, "Food"),
    "Plant milk": (0.6, "Food"), "Fruit": (0.6, "Food"), "Vegetables": (0.5, "Food"),
    "Legumes & tofu": (0.5, "Food"),
    "Plastic goods": (1.8, "Household"), "Paper & tissue": (1.1, "Household"),
    "Cleaning products": (0.9, "Household"), "Reusable & zero-waste items": (0.4, "Household"),
    "Small electronics": (2.8, "Household"),
    "Leather shoes": (4.0, "Clothing"), "Fast fashion": (2.5, "Clothing"),
    "Synthetic sportswear": (2.2, "Clothing"), "Cotton basics": (1.6, "Clothing"),
    "Second-hand clothes": (0.2, "Clothing"),
}
PLANT_BASED = {"Vegetables", "Fruit", "Legumes & tofu", "Plant milk", "Rice", "Bread & pasta"}
PERISHABLE = {"Vegetables", "Fruit", "Dairy milk", "Plant milk", "Eggs", "Bread & pasta", "Fish", "Chicken"}

# product type -> [(greener option, estimated multiplier of that option)]
ALTS = {
    "Beef": [("Lentil or bean mince", 0.5), ("Chicken instead of beef", 2.0)],
    "Lamb": [("Chickpea stew", 0.5), ("Chicken or pork", 2.0)],
    "Cheese": [("Hummus or tofu spread", 0.6), ("Smaller amount of local cheese", 2.2)],
    "Butter": [("Plant-based spread", 0.9)], "Pork": [("Tofu or tempeh", 0.5)],
    "Fish": [("Seasonal veg bowl", 0.5)], "Chicken": [("Tofu or beans", 0.5)],
    "Dairy milk": [("Oat, soy or almond milk", 0.6)], "Eggs": [("Tofu scramble", 0.5)],
    "Ready meals": [("Batch-cooked home meals", 0.7)], "Coffee & tea": [("Fair-trade loose-leaf tea", 1.0)],
    "Snacks & sweets": [("Fruit or bulk-bin nuts", 0.6)],
    "Plastic goods": [("Glass or steel reusables", 0.4)], "Paper & tissue": [("Recycled paper", 0.7)],
    "Small electronics": [("Refurbished device", 0.9)],
    "Leather shoes": [("Second-hand or recycled-material shoes", 0.5)],
    "Fast fashion": [("Second-hand or clothes swap", 0.2), ("Organic cotton basics", 1.2)],
    "Synthetic sportswear": [("Recycled-fibre sportswear", 1.4), ("Second-hand kit", 0.2)],
    "Cotton basics": [("Second-hand basics", 0.2)],
}

# Greener options for EVERY product type (the brief asks for suggestions per type).
BRAND_IDEAS = {
    "Beef": "Plant-based mince brands, or locally raised grass-fed beef in small amounts",
    "Lamb": "Chickpea or lentil stews, or occasional local pasture-raised lamb",
    "Cheese": "Smaller portions of local cheese, or hummus and tofu spreads",
    "Butter": "Plant-based spreads or olive oil from fair-trade co-ops",
    "Pork": "Tofu, tempeh or beans; choose local farms when you do buy pork",
    "Fish": "Seasonal veg bowls, or fish with a sustainable-fishing label (e.g. MSC)",
    "Chicken": "Tofu or beans, or free-range local poultry",
    "Ready meals": "Batch-cooked home meals, or meals from a local zero-waste deli",
    "Dairy milk": "Oat, soy or pea milk, or milk in returnable glass bottles",
    "Rice": "Local grains such as millet or barley, or organic fair-trade rice",
    "Eggs": "Local free-range eggs from a market, or a tofu scramble",
    "Coffee & tea": "Fair-trade or Rainforest Alliance loose-leaf tea and beans",
    "Snacks & sweets": "Fruit, bulk-bin nuts, or fair-trade chocolate brands",
    "Bread & pasta": "Local bakeries and whole-grain or organic brands",
    "Plant milk": "Already a great pick. Choose cartons with FSC certification",
    "Fruit": "Seasonal, local or farmers'-market fruit with no plastic wrap",
    "Vegetables": "Seasonal local produce, veg boxes or community-supported farms",
    "Legumes & tofu": "Already a great pick. Buy dried and in bulk to cut packaging",
    "Plastic goods": "Glass, steel or bamboo reusables and refill stores",
    "Paper & tissue": "Recycled, FSC-certified or bamboo paper brands",
    "Cleaning products": "Refill and concentrate brands, or plain soda and vinegar",
    "Reusable & zero-waste items": "Already a great pick. Repair, reuse and share them as long as you can",
    "Small electronics": "Refurbished devices and repair-friendly brands",
    "Leather shoes": "Second-hand, resoled or recycled-material shoes",
    "Fast fashion": "Second-hand shops, clothes swaps or organic cotton labels",
    "Synthetic sportswear": "Recycled-fibre sportswear or second-hand kit",
    "Cotton basics": "Organic or second-hand cotton basics",
    "Second-hand clothes": "Already a great pick. Charity shops and swaps are the greenest of all",
}
# Brands the app recognises as local/ethical (curated for this learning project, not an endorsement).
ETHICAL_BRANDS = {"patagonia", "oatly", "who gives a crap", "seventh generation", "ecover",
                  "tony's chocolonely", "veja", "oxfam", "thrift+"}

# Typical weekly amount per person (units) used for buying advice.
TYPICAL_WEEKLY = {"Dairy milk": 2, "Plant milk": 2, "Eggs": 6, "Bread & pasta": 2, "Vegetables": 7,
                  "Fruit": 7, "Chicken": 1, "Beef": 1, "Fish": 1, "Cheese": 1, "Rice": 1,
                  "Legumes & tofu": 2, "Snacks & sweets": 2, "Coffee & tea": 1, "Ready meals": 2}
NAME_RULES = {"banana": 6, "apple": 5, "milk": 2, "egg": 6, "bread": 2, "tomato": 5, "carrot": 6}

# (label, new product type, price, product type it replaces) for people who skip meal prep
GRAB_AND_GO = [
    ("Oat-milk latte instead of a dairy latte", "Plant milk", 3.0, "Dairy milk"),
    ("Bean & veg wrap instead of a ham sandwich", "Legumes & tofu", 4.0, "Pork"),
    ("Fresh fruit instead of a candy bar", "Fruit", 1.5, "Snacks & sweets"),
    ("Refillable bottle instead of bottled water", "Reusable & zero-waste items", 6.0, "Plastic goods"),
    ("Falafel box instead of a chicken meal", "Vegetables", 5.0, "Chicken"),
]

BADGES = {  # name -> (icon, how to earn it)
    "Eco Saver of the Month": ("🌱", f"Log 3+ purchases in a month with under {MONTH_LIMIT:.0f} kg CO₂ in total"),
    "Low Impact Shopper": ("🍃", "Make 3+ purchases where at least 60% are low-impact"),
    "Plant Powered": ("🥦", "Log 3 plant-based purchases"),
    "Smart Planner": ("🗓️", "Tick off a full list of 3+ items without any overbuying"),
    "Meal Prep Master": ("🍱", "Add a plan of 5+ recipes to your grocery list"),
    "Second-Hand Hero": ("👕", "Log a second-hand clothes purchase"),
    "Local Legend": ("🏡", "Log 2 purchases from local or ethical brands"),
    "Zero Waste Streak": ("♻️", "Log 2 reusable or zero-waste purchases"),
    "Challenge Champion": ("🏆", "Complete 2 weekly challenges"),
}
CAT_ICONS = {"Food": "", "Household": "", "Clothing": ""}

TIPS = [
    "Swapping beef for beans just twice a week can cut your food footprint noticeably.",
    "Seasonal fruit travels less, so it usually carries a smaller footprint.",
    "Plan meals before you shop: wasted food is wasted CO₂.",
    "A reusable bag used often beats a stack of single-use ones.",
    "Second-hand clothes avoid almost all of the manufacturing footprint.",
    "Buying loose produce can save a surprising amount of plastic.",
    "Cooking in batches uses less energy than cooking many small meals.",
    "Oat, soy and pea milks usually have a lower footprint than dairy milk.",
    "Frozen veg is often as nutritious as fresh and wastes less.",
    "Repairing shoes is greener than replacing them.",
    "A shopping list is your best defence against impulse buys.",
    "Choose refills for cleaning products when you can.",
    "Local markets often mean fewer food miles.",
    "Leftovers make a great next-day lunch. Zero waste, zero stress!",
    "Lentils are cheap, filling and one of the lowest-CO₂ proteins.",
    "Small steps count. Every green choice adds up.",
    "Try one meat-free day this week. You've got this!",
    "Buy only what you will eat this week and your bin (and the planet) will thank you.",
    "Check the label for recycled materials when buying paper goods.",
    "Share big purchases with friends or borrow instead of buying.",
    "Refurbished electronics can cut a device's footprint a lot.",
    "Being mindful is progress, not perfection. Well done!",
]

PERSONA_TIPS = {
    "student": "Student mode: budget-friendly greens first. Lentils, oats and seasonal veg are cheap AND low-CO₂.",
    "busy": "Busy-schedule mode: quick recipes are shown first and swaps are grab-and-go friendly.",
    "balanced": "Balanced mode: plan a calm weekly shop and mix in a few new plant-based meals.",
}

# name, meal, minutes, kg CO2 per serving, cost per serving, tags, ingredients [(name, qty, type)], swap tip
RECIPES = [
    ("Lentil Bolognese", "Dinner", 35, 0.6, 2.0, ["vegan", "vegetarian", "budget", "high-protein"],
     [("Red lentils", 2, "Legumes & tofu"), ("Tomato passata", 2, "Vegetables"), ("Pasta", 1, "Bread & pasta"), ("Onions", 2, "Vegetables")],
     "Swap beef mince for lentils and save 2.1 kg CO₂ per serving."),
    ("Chickpea Coconut Curry", "Dinner", 30, 0.7, 2.2, ["vegan", "vegetarian", "budget", "high-protein"],
     [("Chickpeas", 2, "Legumes & tofu"), ("Coconut milk", 1, "Plant milk"), ("Rice", 1, "Rice"), ("Spinach", 2, "Vegetables")],
     "Swap chicken for chickpeas and save 1.0 kg CO₂ per serving."),
    ("Veggie Fried Rice", "Lunch", 15, 0.6, 1.8, ["vegan", "vegetarian", "budget", "quick"],
     [("Rice", 1, "Rice"), ("Mixed vegetables", 3, "Vegetables"), ("Tofu", 1, "Legumes & tofu")],
     "Swap egg for tofu cubes to make it fully vegan."),
    ("Overnight Oats", "Breakfast", 10, 0.4, 1.2, ["vegan", "vegetarian", "budget", "quick"],
     [("Rolled oats", 1, "Bread & pasta"), ("Oat milk", 1, "Plant milk"), ("Bananas", 3, "Fruit")],
     "Oat milk instead of dairy saves about 0.3 kg CO₂ per serving."),
    ("Tofu Veggie Stir-fry", "Dinner", 20, 0.7, 2.5, ["vegan", "vegetarian", "high-protein", "quick"],
     [("Firm tofu", 2, "Legumes & tofu"), ("Stir-fry vegetables", 3, "Vegetables"), ("Rice", 1, "Rice")],
     "Swap chicken for tofu and save 1.2 kg CO₂ per serving."),
    ("Black Bean Burrito Bowl", "Lunch", 25, 0.8, 2.4, ["vegan", "vegetarian", "budget", "high-protein"],
     [("Black beans", 2, "Legumes & tofu"), ("Rice", 1, "Rice"), ("Peppers", 2, "Vegetables"), ("Avocado", 1, "Fruit")],
     "Swap beef for black beans and save 2.0 kg CO₂ per serving."),
    ("Mediterranean Tray Bake", "Dinner", 40, 0.6, 2.6, ["vegan", "vegetarian"],
     [("Courgettes", 2, "Vegetables"), ("Aubergine", 1, "Vegetables"), ("Cherry tomatoes", 2, "Vegetables"), ("Chickpeas", 1, "Legumes & tofu")],
     "Already a low-CO₂ star. Add olives for extra flavour."),
    ("Egg Muffin Cups", "Breakfast", 25, 0.9, 1.6, ["vegetarian", "high-protein", "budget"],
     [("Eggs", 6, "Eggs"), ("Spinach", 2, "Vegetables"), ("Peppers", 1, "Vegetables")],
     "Try tofu scramble muffins to save about 0.4 kg CO₂."),
    ("Chicken & Veg Rice Bowl", "Lunch", 30, 1.6, 3.2, ["high-protein"],
     [("Chicken breast", 2, "Chicken"), ("Rice", 1, "Rice"), ("Broccoli", 2, "Vegetables")],
     "Swap chicken for tofu and save 0.9 kg CO₂ per serving."),
    ("Baked Fish & Potatoes", "Dinner", 35, 2.0, 4.0, ["high-protein"],
     [("White fish fillets", 2, "Fish"), ("Potatoes", 3, "Vegetables"), ("Green beans", 2, "Vegetables")],
     "Swap fish for a bean and veg bake and save 1.4 kg CO₂ per serving."),
    ("Minestrone Soup", "Lunch", 30, 0.4, 1.5, ["vegan", "vegetarian", "budget"],
     [("Mixed beans", 1, "Legumes & tofu"), ("Soup vegetables", 3, "Vegetables"), ("Small pasta", 1, "Bread & pasta")],
     "Already super low. Freeze portions for busy days!"),
    ("Peanut Noodle Salad", "Lunch", 15, 0.7, 2.1, ["vegan", "vegetarian", "quick"],
     [("Noodles", 1, "Bread & pasta"), ("Peanut butter", 1, "Legumes & tofu"), ("Cabbage & carrots", 3, "Vegetables")],
     "Add edamame for extra protein at tiny CO₂ cost."),
    ("Cheesy Veg Quesadillas", "Dinner", 20, 1.3, 2.3, ["vegetarian", "quick"],
     [("Tortillas", 1, "Bread & pasta"), ("Cheese", 1, "Cheese"), ("Peppers", 2, "Vegetables"), ("Sweetcorn", 1, "Vegetables")],
     "Use half the cheese plus beans and save 0.5 kg CO₂."),
    ("Red Lentil Dal & Rice", "Dinner", 30, 0.5, 1.4, ["vegan", "vegetarian", "budget", "high-protein"],
     [("Red lentils", 2, "Legumes & tofu"), ("Rice", 1, "Rice"), ("Onions", 2, "Vegetables")],
     "A budget champion: roughly 1.5 kg CO₂ cheaper than a lamb curry."),
    ("Banana Oat Pancakes", "Breakfast", 20, 0.6, 1.3, ["vegetarian", "budget", "quick"],
     [("Bananas", 3, "Fruit"), ("Rolled oats", 1, "Bread & pasta"), ("Eggs", 2, "Eggs")],
     "Use a flax egg and plant milk to make them vegan."),
    ("Beef Chili", "Dinner", 45, 3.4, 3.8, ["high-protein"],
     [("Beef mince", 2, "Beef"), ("Kidney beans", 2, "Legumes & tofu"), ("Tomatoes", 3, "Vegetables")],
     "Swap beef for extra beans and save 2.9 kg CO₂ per serving."),
]


@st.cache_data
def get_recipes() -> list[dict]:
    """Convert the compact RECIPES tuples into a list of dictionaries (cached, static data)."""
    keys = ("name", "meal", "mins", "co2", "cost", "tags", "ingredients", "swap")
    return [dict(zip(keys, r)) for r in RECIPES]


@st.cache_data
def multiplier_table() -> pd.DataFrame:
    """Table of all multipliers for the 'How is CO2 estimated?' explainer."""
    rows = [{"Product type": k, "Category": v[1], "kg CO₂e per $": v[0]} for k, v in PRODUCTS.items()]
    return pd.DataFrame(rows).sort_values("kg CO₂e per $", ascending=False)


SAMPLE = [  # (type, brand, price, local/ethical) used by the test plan and "Load sample data"
    ("Vegetables", "Farm Fresh", 6.0, False), ("Legumes & tofu", "GreenBean", 5.0, False),
    ("Fruit", "Orchard Co", 4.0, False), ("Second-hand clothes", "ThriftHub", 15.0, False),
    ("Plant milk", "OatCo", 3.5, True), ("Reusable & zero-waste items", "RefillCo", 8.0, True),
    ("Reusable & zero-waste items", "RefillCo", 12.0, False), ("Beef", "Prime Cuts", 20.0, False),
    ("Leather shoes", "StepRight", 80.0, False), ("Cheese", "DairyBest", 10.0, False),
    ("Chicken", "FarmBird", 9.0, False), ("Fast fashion", "QuickWear", 25.0, False),
    ("Rice", "GrainCo", 4.5, False),
]

# =============================================================================
# 2. TURTLE-STYLE DRAWING ENGINE
# (Mimics Python's `turtle` module in pure Python because the real turtle needs a
#  desktop window and cannot run on Streamlit Cloud. Drawings are recorded as paths
#  and rendered as an SVG that "draws itself" with a CSS stroke-dashoffset animation.)
# =============================================================================
class MiniTurtle:
    """A tiny turtle-like class: forward/left/right/penup/pendown/color/begin_fill/end_fill.
    Everything drawn is recorded in order, so later shapes paint over earlier ones (like real turtle)."""

    def __init__(self) -> None:
        self.x, self.y, self.heading = 0.0, 0.0, 90.0
        self.pen_down, self.pen_color, self.fill_color, self.width = True, "#2D4A3E", "#6B8F5E", 3.0
        self.items: list[list] = []  # ["stroke", pts, color, width] | ["fill", pts, color] | ["dot", x, y, r, color]
        self._cur: list | None = None
        self._fill_item: list | None = None

    def penup(self) -> None:
        self.pen_down, self._cur = False, None

    def pendown(self) -> None:
        self.pen_down = True

    def color(self, pen: str, fill: str | None = None) -> None:
        self.pen_color, self.fill_color = pen, fill or self.fill_color
        self._cur = None  # a new colour starts a new stroke

    def pensize(self, width: float) -> None:
        self.width, self._cur = width, None

    def setheading(self, angle: float) -> None:
        self.heading = angle

    def goto(self, x: float, y: float) -> None:
        if self.pen_down:
            if self._cur is None:
                self._cur = [(self.x, self.y)]
                self.items.append(["stroke", self._cur, self.pen_color, self.width])
            self._cur.append((x, y))
        self.x, self.y = x, y
        if self._fill_item is not None:
            self._fill_item[1].append((x, y))

    def forward(self, dist: float) -> None:
        self.goto(self.x + dist * cos(radians(self.heading)), self.y + dist * sin(radians(self.heading)))

    def left(self, angle: float) -> None:
        self.heading += angle

    def right(self, angle: float) -> None:
        self.heading -= angle

    def circle(self, radius: float, extent: float = 360, steps: int = 30) -> None:
        """Approximate an arc with many short forward/left moves (like turtle.circle)."""
        step_angle = extent / steps
        step_len = 2 * abs(radius) * sin(radians(step_angle / 2))
        for _ in range(steps):
            self.left(step_angle / 2)
            self.forward(step_len)
            self.left(step_angle / 2)

    def begin_fill(self) -> None:
        self._fill_item = ["fill", [(self.x, self.y)], None]  # reserve its place so outlines paint on top
        self.items.append(self._fill_item)

    def end_fill(self) -> None:
        if self._fill_item is not None:
            self._fill_item[2] = self.fill_color
        self._fill_item = None

    def dot(self, size: float) -> None:
        self.items.append(["dot", self.x, self.y, size / 2, self.fill_color])

    def to_svg(self, width: int = 150, label: str = "Eco drawing", animate: bool = True) -> str:
        """Render everything that was drawn as an SVG string (self-drawing when animate=True)."""
        pts = []
        for it in self.items:
            if it[0] == "dot":
                pts += [(it[1] - it[3], it[2] - it[3]), (it[1] + it[3], it[2] + it[3])]
            else:
                pts += it[1]
        if not pts:
            return ""
        x0, x1 = min(p[0] for p in pts) - 8, max(p[0] for p in pts) + 8
        y0, y1 = min(p[1] for p in pts) - 8, max(p[1] for p in pts) + 8
        path = lambda ps, close="": "M" + " L".join(f"{x:.1f} {-y:.1f}" for x, y in ps) + close  # SVG y points down
        parts = [f'<svg class="tl-svg" role="img" aria-label="{html.escape(label)}" xmlns="http://www.w3.org/2000/svg" '
                 f'width="{width}" viewBox="{x0:.1f} {-y1:.1f} {x1 - x0:.1f} {y1 - y0:.1f}">']
        fill_cls, stroke_cls, n = ("tl-fill", "tl-path", 0) if animate else ("tl-static", "tl-static", 0)
        for it in self.items:
            if it[0] == "fill" and it[2]:
                parts.append(f'<path class="{fill_cls}" d="{path(it[1], "Z")}" fill="{it[2]}"/>')
            elif it[0] == "dot":
                parts.append(f'<circle class="{fill_cls}" cx="{it[1]:.1f}" cy="{-it[2]:.1f}" r="{it[3]:.1f}" fill="{it[4]}"/>')
            elif it[0] == "stroke":
                parts.append(f'<path class="{stroke_cls}" pathLength="1" d="{path(it[1])}" stroke="{it[2]}" fill="none" '
                             f'stroke-width="{it[3]}" stroke-linecap="round" stroke-linejoin="round" '
                             f'style="animation-delay:{n * 0.35:.2f}s"/>')
                n += 1
        return "".join(parts) + "</svg>"


def draw_leaf_svg() -> str:
    """Draw a leaf (two arcs, a midrib, side veins and a stem) with the mini turtle."""
    t = MiniTurtle()
    t.color("#2D4A3E", "#8FB57A")
    t.penup(); t.goto(0, -60); t.setheading(45); t.pendown()
    t.begin_fill(); t.circle(85, 90); t.left(90); t.circle(85, 90); t.end_fill()
    t.penup(); t.goto(0, -60); t.setheading(270); t.pendown(); t.forward(22)  # stem
    t.penup(); t.goto(0, -60); t.setheading(90); t.pendown(); t.forward(120)  # midrib
    for k in (1, 2, 3):
        for ang in (45, 135):
            t.penup(); t.goto(0, -60 + k * 28); t.setheading(ang); t.pendown(); t.forward(24)
    return t.to_svg(label="A green leaf drawn to celebrate a low-impact choice")


def draw_mascot_svg(mood: str = "happy", width: int = 120) -> str:
    """Carty, the ShopImpact shopping cart, drawn with the mini turtle: a realistic side-view metal trolley with a
    wire basket (near and far wall for depth), chrome frame, green grip, lower shelf and four rubber wheels.
    Moods change what is in the cart: happy, cheer, calm."""
    t = MiniTurtle()
    ink, steel, steel_hi, wire = "#26322E", "#B4C0BC", "#FFFFFF", "#6B7A75"
    green, green_dk = "url(#cy-green)", "#2B5240"
    d = (11, 8)                                                         # far-wall offset gives the basket depth

    def fillpoly(pts, color):
        t.color(ink, color); t.penup(); t.goto(*pts[0]); t.begin_fill()
        for p in pts[1:] + [pts[0]]:
            t.goto(*p)
        t.end_fill(); t.penup()

    def stroke(pts, color=ink, w=3, close=False):
        t.color(color); t.pensize(w); t.penup(); t.goto(*pts[0]); t.pendown()
        for p in pts[1:] + ([pts[0]] if close else []):
            t.goto(*p)
        t.penup(); t.pensize(3)

    def tube(pts, w=5.5):                                               # chrome tube: dark edge, steel body, specular line
        stroke(pts, ink, w); stroke(pts, steel, w - 2.2)
        stroke([(x - 0.7, y + 1.0) for x, y in pts], steel_hi, 1.0)

    def blob(cx, cy, rx, ry, color):
        fillpoly([(cx + rx * cos(radians(a)), cy + ry * sin(radians(a))) for a in range(0, 361, 10)], color)

    def disc(x, y, r, color, edge=None, w=2.5):
        if edge:
            t.color(edge, edge); t.penup(); t.goto(x, y); t.dot(2 * r + w)
        t.color(color, color); t.penup(); t.goto(x, y); t.dot(2 * r)

    def capsule(p0, p1, r, color, edge=ink, w=2.6):
        a = atan2(p1[1] - p0[1], p1[0] - p0[0])
        pts = [(p1[0] + r * cos(a + radians(k)), p1[1] + r * sin(a + radians(k))) for k in range(-90, 91, 15)]
        pts += [(p0[0] + r * cos(a + radians(k)), p0[1] + r * sin(a + radians(k))) for k in range(90, 271, 15)]
        fillpoly(pts, color); stroke(pts, edge, w, True)

    def leaf(x, y, length, ang, color, wide=7):
        a = radians(ang); ca, sa = cos(a), sin(a)
        top = [(length * s / 14, wide * sin(pi * s / 14)) for s in range(15)]
        pts = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in top + [(px, -py) for px, py in reversed(top)]]
        fillpoly(pts, color); stroke(pts, ink, 1.8, True)
        stroke([(x, y), (x + length * 0.85 * ca, y + length * 0.85 * sa)], "#E9F2DC", 1.2)

    def sparkle(x, y, r, color="#E4B94F"):
        fillpoly([(x + (r if k % 2 == 0 else r * 0.32) * cos(radians(k * 45 + 90)),
                   y + (r if k % 2 == 0 else r * 0.32) * sin(radians(k * 45 + 90))) for k in range(8)], color)

    def wheel(wx, wy, r, dark=False):                                   # rubber tyre, tread ticks, metal hub
        disc(wx, wy, r, "url(#cy-tire)", ink, 2)
        for k in range(12):
            a = radians(k * 30)
            stroke([(wx + (r - 0.2) * cos(a), wy + (r - 0.2) * sin(a)), (wx + (r - 2.4) * cos(a), wy + (r - 2.4) * sin(a))], "#5C6964", 1.1)
        disc(wx, wy, r * 0.5, "url(#cy-hub)", "#2E3A35", 1.4); disc(wx, wy, r * 0.13, ink)

    near = [(-62, 44), (66, 44), (50, 0), (-46, 0)]
    far = [(x + d[0], y + d[1]) for x, y in near]
    xl = lambda y, o=0: -62 + (44 - y) / 44 * 16 + o
    xr = lambda y, o=0: 66 - (44 - y) / 44 * 16 + o

    blob(6, -52, 92, 6, "url(#cy-shadow)")                                         # soft ground shadow

    # far side: wheels, rail, back wall of the basket
    stroke([(-35, 8), (-39, -20)], "#4A5853", 3); stroke([(61, 8), (65, -20)], "#4A5853", 3)
    stroke([(-39, -20), (65, -20)], "#4A5853", 3.4)
    for wx in (-39, 65):
        stroke([(wx, -20), (wx, -28)], "#4A5853", 3); wheel(wx, -35, 8.6)
    fillpoly(far, "rgba(205,218,213,.30)")
    for y in (16, 24, 32, 40, 48):
        stroke([(xl(y - d[1], d[0]), y), (xr(y - d[1], d[0]), y)], "#8F9D98", 0.9)
    for k in range(1, 12):
        u = k / 12
        stroke([(-51 + u * 128, 52), (-35 + u * 96, 8)], "#8F9D98", 0.9)
    stroke(far, "#6B7A75", 1.8, True)
    stroke([(-62, 44), (-51, 52)], green_dk, 4); stroke([(66, 44), (77, 52)], green_dk, 4)
    capsule((-51, 52), (77, 52), 3, green, ink, 2)                                  # back rim

    # groceries sit between the two walls
    leaf(-34, 38, 38, 105, "#5E9150"); leaf(-26, 38, 36, 75, "#86B873"); leaf(-40, 38, 30, 135, "#4E8044")
    if mood != "calm":
        fillpoly([(14, 14), (40, 14), (40, 54), (14, 54)], "url(#cy-box)"); stroke([(14, 36), (40, 36)], "#B9812A", 2)
        stroke([(14, 14), (40, 14), (40, 54), (14, 54)], ink, 2.2, True)
        capsule((-4, 30), (22, 66), 5.2, "url(#cy-bread)")
        disc(-10, 47, 11, "url(#cy-apple)", ink, 2.5); disc(-13.5, 50.5, 2.8, "#F7B3A6")
        stroke([(-10, 58), (-8.5, 64)], "#6B4A33", 2.4); leaf(-8, 62, 11, 20, "#6FA55C", 3.4)

    # near wall of the basket: glass-like sheen, mesh, outline, rims
    fillpoly(near, "url(#cy-glass)")
    for y in (36, 28, 20, 12, 4):
        stroke([(xl(y), y), (xr(y), y)], wire, 1.3)
    for k in range(1, 12):
        u = k / 12
        stroke([(-62 + u * 128, 44), (-46 + u * 96, 0)], wire, 1.3)
    stroke(near, ink, 3, True)
    capsule((-46, 0), (50, 0), 2.8, steel)
    capsule((-62, 44), (66, 44), 4.2, green, ink)
    stroke([(-58, 46.4), (62, 46.4)], "rgba(255,255,255,.6)", 1.5)
    capsule((-44, 16), (-6, 16), 7.2, green, ink, 2.2)                              # nameplate (text added below)

    # chrome frame, handle, shelf, near wheels
    tube([(-70, 60), (-62, 44), (-46, 0), (-50, -26)])
    tube([(50, 0), (56, -26)])
    fillpoly([(-48, -9), (54, -9), (63, -3), (-39, -3)], "rgba(205,218,213,.45)")    # shelf top, seen from above
    for x in range(-36, 60, 12):
        stroke([(x, -9), (x + 9, -3)], "#8F9D98", 1)
    stroke([(-48, -9), (54, -9), (63, -3), (-39, -3)], ink, 1.6, True)
    fillpoly([(-48, -9), (54, -9), (56, -16), (-50, -16)], "rgba(205,218,213,.55)")
    for x in range(-40, 50, 12):
        stroke([(x, -9), (x + 2, -16)], wire, 1.2)
    stroke([(-48, -9), (54, -9), (56, -16), (-50, -16)], ink, 2, True)
    tube([(-50, -26), (58, -26)], 5)
    capsule((-95, 63), (-67, 61), 5, green, ink)                                    # rubber grip
    stroke([(-92, 65.6), (-70, 63.6)], "rgba(255,255,255,.45)", 1.4)
    capsule((60, 4), (60, -10), 3, "#2B3834", ink, 1.6)                              # front bumper
    for wx in (-50, 58):
        tube([(wx, -26), (wx, -37)], 4.5); wheel(wx, -42, 10.5)

    if mood == "cheer":
        sparkle(-88, 34, 7); sparkle(82, 66, 8); sparkle(-100, 10, 4.5); disc(88, 34, 2.2, "#F0937B"); disc(-82, 72, 2, "#8FC07A")

    svg = t.to_svg(width, label="Carty, the ShopImpact shopping cart", animate=False)
    defs = ("<defs>"
            "<linearGradient id='cy-green' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#63A079'/><stop offset='.55' stop-color='#3F7352'/><stop offset='1' stop-color='#2B5240'/></linearGradient>"
            "<linearGradient id='cy-glass' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.42'/><stop offset='1' stop-color='#C9D6D1' stop-opacity='.10'/></linearGradient>"
            "<radialGradient id='cy-shadow'><stop offset='0' stop-color='#1F3329' stop-opacity='.42'/><stop offset='1' stop-color='#1F3329' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='cy-tire' cx='.4' cy='.35' r='.75'><stop offset='0' stop-color='#55625D'/><stop offset='1' stop-color='#151B18'/></radialGradient>"
            "<radialGradient id='cy-hub' cx='.38' cy='.32' r='.8'><stop offset='0' stop-color='#FFFFFF'/><stop offset='1' stop-color='#8D9A96'/></radialGradient>"
            "<radialGradient id='cy-apple' cx='.35' cy='.3' r='.8'><stop offset='0' stop-color='#E9705A'/><stop offset='1' stop-color='#B53A27'/></radialGradient>"
            "<linearGradient id='cy-bread' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#F0CE96'/><stop offset='1' stop-color='#C99A5B'/></linearGradient>"
            "<linearGradient id='cy-box' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#EDB94E'/><stop offset='1' stop-color='#C98E2E'/></linearGradient>"
            "</defs>")
    plate = ("<text x='-25' y='-12.6' text-anchor='middle' font-family=\"Fraunces,Georgia,serif\" font-weight='700' "
             "font-size='10.5' fill='#FBF7EC' letter-spacing='.4'>Carty</text>")
    return svg.replace(">", ">" + defs, 1).replace("</svg>", plate + "</svg>")


def mascot_says() -> tuple[str, str]:
    """Pick Carty's mood and message from what the user just did."""
    log, name = ss.last_log, ss.profile.get("name", "friend")
    if log and log["new"]:
        return "cheer", f"Wow {name}, you earned the {log['new'][0]} badge!"
    if log:
        mult = PRODUCTS[log["entry"]["type"]][0]
        if mult <= LOW_MULT:
            return "happy", "Good pick. Every bit helps."
        if mult >= HIGH_MULT:
            return "calm", "Worth a look: there are greener ideas for next time."
        return "happy", "Logged. Small swaps add up."
    left = sum(1 for g in ss.groceries if not g["done"])
    if left:
        return "happy", f"{left} item(s) left to buy. You've got this!"
    return "happy", f"Hi {name}! I'm Carty. Add an item or log a purchase and I'll cheer you on."


def draw_footprint_svg() -> str:
    """Draw a small footprint: an oval sole plus four toes."""
    t = MiniTurtle()
    t.color("#7A5C45", "#C9A98A")
    t.penup(); t.goto(20, -15); t.pendown(); t.begin_fill()
    for deg in range(0, 361, 15):
        t.goto(20 * cos(radians(deg)), -15 + 34 * sin(radians(deg)))
    t.end_fill()
    for x, y, s in ((-16, 38, 13), (-5, 46, 13), (7, 46, 12), (18, 38, 11)):
        t.penup(); t.goto(x, y); t.dot(s)
    return t.to_svg(label="A small footprint drawn to celebrate an ethical choice")


def draw_badge_svg() -> str:
    """Draw an eco badge: a ring with a five-pointed star inside."""
    t = MiniTurtle()
    t.color("#2D4A3E", "#E9DFC7")
    t.penup(); t.goto(0, -50); t.setheading(0); t.pendown()
    t.begin_fill(); t.circle(50, 360, 40); t.end_fill()
    t.color("#B8862B", "#E0B84C")
    t.penup(); t.goto(-35, 11.4); t.setheading(0); t.pendown(); t.begin_fill()
    for _ in range(5):
        t.forward(70); t.right(144)
    t.end_fill()
    return t.to_svg(label="A gold star badge for a new achievement")


# =============================================================================
# 3. STATE, HELPERS AND CORE LOGIC
# =============================================================================
DEFAULTS = {
    "onboarded": False, "ob_step": 0, "profile": {}, "groceries": [], "purchases": [], "meal_plan": [],
    "badges": [], "next_id": 1, "hc": False, "people": 1, "tz": 0.0, "mode": "Weekly",
    "trip_date": date.today() + timedelta(days=1), "trip_time": time(17, 30), "max_prep": 60,
    "snooze_until": None, "reminder_dismissed": None, "toast_key": None, "last_log": None,
    "plan_imported": False, "celebrate": [], "import_sig": None, "autolog": True, "target": 30, "log_msg": None,
    "nav": "grocery", "recent_badges": [], "avatar": None, "av_open": False, "av_draft": None, "av_step": 1, "av_loaded": False, "av_msg": None, "mp_days": 5, "mp_diet": "Any", "mp_budget": 5.0, "mp_all": False,
    "lp_type": list(PRODUCTS)[0], "lp_brand": "", "lp_price": 5.0, "lp_date": date.today(), "lp_eth": False,
}
PERSIST = ["hc", "people", "tz", "mode", "trip_date", "trip_time", "max_prep", "autolog", "target",
           "mp_days", "mp_diet", "mp_budget", "mp_all", "lp_type", "lp_brand", "lp_price", "lp_date", "lp_eth"]  # widget keys kept across screens


def init_state() -> None:
    """Create every session key once so nothing resets unexpectedly."""
    for key, val in DEFAULTS.items():
        if key not in ss:
            ss[key] = deepcopy(val)
    for key in PERSIST:  # self-assignment stops Streamlit dropping widget values while a widget is hidden
        ss[key] = ss[key]


def now_local() -> datetime:
    """Server clock shifted by the user's chosen UTC offset (Streamlit Cloud runs on UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=float(ss.tz))


def calculate_impact(ptype: str, price: float) -> float:
    """CO2 (kg) = price x multiplier. Unknown types or negative prices give 0."""
    if ptype not in PRODUCTS or price is None or price < 0:
        return 0.0
    return round(float(price) * PRODUCTS[ptype][0], 2)


def impact_label(mult: float) -> str:
    return "Low impact" if mult <= LOW_MULT else ("High impact" if mult >= HIGH_MULT else "Medium impact")


def get_alternatives(ptype: str, price: float) -> list[dict]:
    """Greener options for a product type, with the CO2 saved if the user switches."""
    mult = PRODUCTS.get(ptype, (0, ""))[0]
    out = [{"option": o, "saved": round(price * (mult - m), 2)} for o, m in ALTS.get(ptype, []) if m < mult]
    return sorted(out, key=lambda a: a["saved"], reverse=True)


def suggest_quantity(item: dict) -> tuple[str, str]:
    """Compare an item's quantity with typical need. Returns (status, friendly message)."""
    weekly = next((v for k, v in NAME_RULES.items() if k in item["name"].lower()), TYPICAL_WEEKLY.get(item["type"]))
    if not weekly:
        return "ok", ""
    need = weekly * max(1, int(ss.people)) * (4 if ss.mode == "Monthly" else 1)
    name = item["name"]
    if item["qty"] > need * 1.5:
        extra = " They may spoil before you can eat them." if item["type"] in PERISHABLE else ""
        return "over", f"That's a lot of **{name}** for {ss.mode.lower()} shopping.{extra} Try {need} instead."
    if item["qty"] < need * 0.5:
        return "under", f"You may run out of **{name}** before your next trip. Around {need} would be safer."
    return "ok", ""


def profile_mode(p: dict) -> str:
    """Pick a persona from the profession to tune tips."""
    prof = p.get("profession", "").lower()
    if "student" in prof:
        return "student"
    if any(k in prof for k in ("nurse", "doctor", "shift", "driver", "chef")):
        return "busy"
    return "balanced"


def suggest_shop_time(p: dict) -> tuple[time, str]:
    """Default shopping time (early evening). The user can change it in Trip settings."""
    return time(17, 30), "A calm early-evening shop around 17:30 suits most people. Change the time below whenever you like."


def find_item(iid: int) -> dict | None:
    return next((g for g in ss.groceries if g["id"] == iid), None)


def add_grocery(name: str, ptype: str, brand: str, qty: float, price: float) -> tuple[bool, str]:
    """Validate and add an item; duplicates are merged by summing quantities."""
    name = (name or "").strip()
    if not name:
        return False, "Please give the item a name."
    if ptype not in PRODUCTS:
        return False, "Please choose a product type."
    if qty is None or qty <= 0:
        return False, "Quantity must be at least 1."
    if price is None or price < 0:
        return False, "Price can't be negative."
    brand = (brand or "").strip()
    for g in ss.groceries:
        if (g["name"].lower(), g["type"], g["brand"].lower()) == (name.lower(), ptype, brand.lower()) and not g["done"]:
            g["qty"] += int(qty)
            return True, f"{name} was already on your list, so I added {int(qty)} to the quantity."
    ss.groceries.append({"id": ss.next_id, "name": name, "type": ptype, "brand": brand,
                         "qty": int(qty), "price": float(price), "done": False})
    ss.next_id += 1
    return True, f"Added {name} to your list."


def item_co2(g: dict) -> float:
    return calculate_impact(g["type"], g["price"] * g["qty"])


def build_meal_plan(recipes: list[dict], days: int) -> list[str]:
    """Pick up to `days` recipes, lowest CO2 first, rotating meal types for variety."""
    pool = sorted(recipes, key=lambda r: (r["co2"], r["mins"]))
    plan, seen = [], {}
    for r in pool:  # first pass: at most 3 of each meal type
        if len(plan) < days and seen.get(r["meal"], 0) < 3:
            plan.append(r["name"]); seen[r["meal"]] = seen.get(r["meal"], 0) + 1
    for r in pool:  # second pass: fill any gaps
        if len(plan) < days and r["name"] not in plan:
            plan.append(r["name"])
    return plan


def import_plan_to_list(skip: set | None = None) -> int:
    """Push every ingredient of the plan into the grocery list (duplicates merged)."""
    recipes = {r["name"]: r for r in get_recipes()}
    count, skip = 0, skip or set()
    for name in ss.meal_plan:
        r = recipes.get(name)
        if not r:
            continue
        share = r["cost"] * SERVINGS / max(1, len(r["ingredients"]))
        for ing, qty, ptype in r["ingredients"]:
            if ing in skip:  # already in the user's pantry
                continue
            ok, _ = add_grocery(ing, ptype, "", qty, round(share / qty, 2))
            count += int(ok)
    ss.plan_imported = len(ss.meal_plan) >= 5
    update_badges()
    return count


COLS = ["id", "date", "type", "brand", "price", "co2", "ethical", "category", "month"]


def purchase_status(d: date, today: date | None = None) -> str:
    """'planned' if the purchase date is after today, otherwise 'completed'.
    Status is derived from the date every time, so a planned purchase becomes completed
    automatically when its day arrives."""
    today = today or now_local().date()
    return "planned" if d > today else "completed"


def purchases_df(include_planned: bool = False, only_planned: bool = False) -> pd.DataFrame:
    """Purchases as a DataFrame (empty-safe) with category, month and status columns.
    By default only COMPLETED purchases are returned, so every total, chart, badge, streak and
    challenge ignores future-dated (planned) purchases. Pass include_planned=True for everything,
    or only_planned=True for the planned ones alone."""
    rows = [{**p, "category": PRODUCTS[p["type"]][1]} for p in ss.purchases if p.get("type") in PRODUCTS]
    cols = COLS + ["status"]
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])  # skip records with an unreadable date instead of crashing
    if df.empty:
        return pd.DataFrame(columns=cols)
    today = now_local().date()
    df["status"] = df["date"].dt.date.map(lambda d: purchase_status(d, today))
    df["month"] = df["date"].dt.strftime("%Y-%m")
    if only_planned:
        df = df[df["status"] == "planned"]
    elif not include_planned:
        df = df[df["status"] == "completed"]
    return df.sort_values("date").reset_index(drop=True)


MAX_PRICE = 100000.0   # sanity limit so a typing slip cannot create absurd totals
MAX_BRAND_LEN = 60


def validate_purchase(ptype: str, price: object, d: object, brand: str = "") -> tuple[bool, str]:
    """Check every field of a purchase. Returns (ok, message); the message explains the first problem."""
    if ptype not in PRODUCTS:
        return False, "Please choose a product type from the list."
    try:
        price = float(price)
    except (TypeError, ValueError):
        return False, "The price must be a number."
    if price != price or price in (float("inf"), float("-inf")):
        return False, "The price must be a real number."
    if price <= 0:
        return False, "Please enter a price above zero so I can estimate the footprint."
    if price > MAX_PRICE:
        return False, f"That price looks too large. Please enter an amount up to {MAX_PRICE:,.0f}."
    if not isinstance(d, date):
        return False, "Please choose a purchase date."
    if len((brand or "").strip()) > MAX_BRAND_LEN:
        return False, f"Please keep the brand name under {MAX_BRAND_LEN} characters."
    return True, ""


def compare_alternative(ptype: str, price: float) -> dict | None:
    """Original vs. best greener alternative using the SAME price, so only the multiplier differs.
    Returns None when no lower-impact alternative exists. All figures are estimates."""
    if ptype not in PRODUCTS or price is None or price <= 0:
        return None
    alts = get_alternatives(ptype, price)
    if not alts:
        return None
    best = alts[0]
    original = calculate_impact(ptype, price)
    alt_total = round(original - best["saved"], 2)
    pct = round(best["saved"] / original * 100, 1) if original > 0 else None
    return {"original": original, "option": best["option"], "alternative": alt_total,
            "saved": best["saved"], "pct": pct}


def month_summary(df: pd.DataFrame, month: str) -> dict:
    """Totals for one month of completed purchases (zeros when the month has no data)."""
    m = df[df["month"] == month] if not df.empty else df
    if m.empty:
        return {"co2": 0.0, "spend": 0.0, "n": 0, "by_cat": {}}
    return {"co2": float(m["co2"].sum()), "spend": float(m["price"].sum()), "n": int(len(m)),
            "by_cat": {k: float(v) for k, v in m.groupby("category")["co2"].sum().items()}}


def pct_change(new: float, old: float) -> float | None:
    """Percentage change from old to new, or None when old is zero (a percentage would be meaningless)."""
    return None if not old else round((new - old) / old * 100, 1)


def monthly_comparison(df: pd.DataFrame, month: str, prev_month: str | None) -> dict:
    """Compare a month with the previous one. Uses completed purchases only (pass the completed df).
    'direction' is 'up', 'down', 'same' or 'unknown' and never claims a drop the data does not show."""
    cur = month_summary(df, month)
    prev = month_summary(df, prev_month) if prev_month else None
    out = {"month": month, "prev_month": prev_month, "current": cur, "previous": prev,
           "co2_pct": None, "spend_pct": None, "n_diff": None, "direction": "unknown",
           "top_category": None, "most_improved": None}
    if cur["by_cat"]:
        out["top_category"] = max(cur["by_cat"], key=cur["by_cat"].get)
    if prev and prev["n"] > 0:
        out["co2_pct"], out["spend_pct"] = pct_change(cur["co2"], prev["co2"]), pct_change(cur["spend"], prev["spend"])
        out["n_diff"] = cur["n"] - prev["n"]
        diff = round(cur["co2"] - prev["co2"], 2)
        out["direction"] = "up" if diff > 0 else "down" if diff < 0 else "same"
        drops = {c: prev["by_cat"].get(c, 0.0) - cur["by_cat"].get(c, 0.0) for c in prev["by_cat"]}
        drops = {c: v for c, v in drops.items() if v > 0}
        if drops:
            out["most_improved"] = max(drops, key=drops.get)
    return out


def goal_progress(total: float, target: float) -> dict:
    """Progress towards a monthly estimated-impact target, with a supportive (never shaming) message."""
    target = max(1.0, float(target))
    total = max(0.0, float(total))
    ratio = total / target
    remaining = round(target - total, 2)
    if ratio < 0.5:
        msg = "You have plenty of room left this month."
    elif ratio <= 1:
        msg = "You're within your target. A greener swap on your next shop keeps it that way."
    else:
        msg = f"You're {abs(remaining):.1f} kg above this month's target. That's okay. Swaps on your next shop can bring next month down."
    return {"target": target, "total": total, "ratio": ratio, "remaining": remaining,
            "over": total > target, "message": msg}


def build_insights(df: pd.DataFrame) -> list[str]:
    """Plain-language insights computed only from the completed purchases that were actually logged."""
    if df.empty:
        return []
    out = []
    freq = df["category"].value_counts()
    out.append(f"Most frequent category: {freq.index[0]} ({int(freq.iloc[0])} of {len(df)} purchases).")
    by_cat = df.groupby("category")["co2"].sum().sort_values()
    if len(by_cat) > 1:
        out.append(f"Highest estimated impact: {by_cat.index[-1]} ({by_cat.iloc[-1]:.1f} kg CO₂e). "
                   f"Lowest: {by_cat.index[0]} ({by_cat.iloc[0]:.1f} kg).")
    else:
        out.append(f"All logged purchases so far are in {by_cat.index[0]}.")
    by_type = df.groupby("type")["co2"].sum().sort_values(ascending=False)
    if by_type.iloc[0] > 0:
        out.append(f"Your biggest single contributor is {by_type.index[0]} ({by_type.iloc[0]:.1f} kg CO₂e).")
    months = sorted(df["month"].unique())
    if len(months) >= 2:
        a, b = df[df["month"] == months[-2]]["price"].sum(), df[df["month"] == months[-1]]["price"].sum()
        ch = pct_change(float(b), float(a))
        if ch is not None:
            word = "up" if ch > 0 else "down" if ch < 0 else "unchanged"
            out.append(f"Spending in {months[-1]} is {word}" + (f" {abs(ch):.0f}%" if ch else "") + f" compared with {months[-2]}.")
    swaps = [(t, v) for t, v in by_type.items() if get_alternatives(t, float(df[df["type"] == t]["price"].sum()))]
    if swaps:
        t = swaps[0][0]
        alt = compare_alternative(t, float(df[df["type"] == t]["price"].sum()))
        if alt and alt["saved"] >= 0.5:
            out.append(f"Opportunity: swapping {t} for '{alt['option']}' could save about {alt['saved']:.1f} kg CO₂e (estimate).")
    return out


def evaluate_badges() -> list[str]:
    """Return the names of every badge whose rule is currently satisfied."""
    df, G, earned = purchases_df(), ss.groceries, []
    if not df.empty:
        mult = df["type"].map(lambda t: PRODUCTS[t][0])
        month_sum = df.groupby("month").agg(n=("co2", "size"), total=("co2", "sum"))
        if ((month_sum["n"] >= 3) & (month_sum["total"] < MONTH_LIMIT)).any():
            earned.append("Eco Saver of the Month")
        if len(df) >= 3 and (mult <= LOW_MULT).mean() >= 0.6:
            earned.append("Low Impact Shopper")
        if df["type"].isin(PLANT_BASED).sum() >= 3:
            earned.append("Plant Powered")
        if (df["type"] == "Second-hand clothes").any():
            earned.append("Second-Hand Hero")
        if df["ethical"].fillna(False).astype(bool).sum() >= 2:
            earned.append("Local Legend")
        if (df["type"] == "Reusable & zero-waste items").sum() >= 2:
            earned.append("Zero Waste Streak")
    if len(G) >= 3 and all(g["done"] for g in G) and not any(suggest_quantity(g)[0] == "over" for g in G):
        earned.append("Smart Planner")
    if ss.plan_imported:
        earned.append("Meal Prep Master")
    if sum(c["have"] >= c["goal"] for c in challenge_progress(df)) >= 2:
        earned.append("Challenge Champion")
    return earned


def update_badges() -> list[str]:
    """Award newly earned badges (kept for good) and queue a celebration."""
    new = [b for b in evaluate_badges() if b not in ss.badges]
    ss.badges += new
    ss.celebrate += new
    if new:
        ss.recent_badges = list(new)
    return new


def log_purchase(ptype: str, brand: str, price: float, d: date, ethical: bool) -> dict:
    """Record a purchase, update badges and prepare the result card."""
    entry = {"id": ss.next_id, "date": d.isoformat(), "type": ptype, "brand": (brand or "").strip() or "Unbranded",
             "price": round(float(price), 2), "co2": calculate_impact(ptype, price), "ethical": bool(ethical),
             "status": purchase_status(d)}
    ss.next_id += 1
    ss.purchases.append(entry)
    new = update_badges()
    ss.last_log = {"entry": entry, "tip": random.choice(TIPS), "new": new,
                   "alts": get_alternatives(ptype, entry["price"])}
    return entry


def check_reminders() -> list[dict]:
    """Items still to buy if the trip is within 30 min (or past) and not snoozed/dismissed."""
    pending = [g for g in ss.groceries if not g["done"]]
    trip = datetime.combine(ss.trip_date, ss.trip_time)
    now = now_local()
    if not pending or now < trip - timedelta(minutes=30) or ss.reminder_dismissed == trip.isoformat():
        return []
    if ss.snooze_until and now < ss.snooze_until:
        return []
    return pending


def co2_equivalents(kg: float) -> dict:
    """Translate kg of CO2 into everyday comparisons (rough figures, for awareness only)."""
    kg = max(0.0, float(kg))
    return {"km": round(kg / 0.17), "charges": round(kg / 0.008), "tree_days": round(kg / 21 * 365)}


def green_streak(df: pd.DataFrame, today: date | None = None) -> int:
    """Consecutive days (ending today or yesterday) with a low-impact and no high-impact purchase."""
    today = today or now_local().date()
    if df.empty:
        return 0
    flags: dict = {}
    for d, t in zip(df["date"].dt.date, df["type"]):
        low, high = flags.get(d, (False, False))
        flags[d] = (low or PRODUCTS[t][0] <= LOW_MULT, high or PRODUCTS[t][0] >= HIGH_MULT)
    good = {d for d, (low, high) in flags.items() if low and not high}
    day = today if today in good else today - timedelta(days=1)
    n = 0
    while day in good:
        n, day = n + 1, day - timedelta(days=1)
    return n


def challenge_progress(df: pd.DataFrame, today: date | None = None) -> list[dict]:
    """Progress on this week's (Mon-Sun) challenges as a list of {title, have, goal}."""
    today = today or now_local().date()
    start = today - timedelta(days=today.weekday())
    w = df if df.empty else df[(df["date"].dt.date >= start) & (df["date"].dt.date <= today)]
    low = plant = 0
    total = 0.0
    if not w.empty:
        low = int((w["type"].map(lambda t: PRODUCTS[t][0]) <= LOW_MULT).sum())
        plant = int(w["type"].isin(PLANT_BASED).sum())
        total = float(w["co2"].sum())
    return [
        {"title": "Make 5 low-impact purchases", "have": low, "goal": 5},
        {"title": "Buy 3 plant-based items", "have": plant, "goal": 3},
        {"title": "Stay under 15 kg CO₂ (with 3+ purchases)", "have": int(len(w) >= 3 and total < 15), "goal": 1},
        {"title": "Tick off 5 grocery items", "have": sum(g["done"] for g in ss.groceries), "goal": 5},
    ]


CARD_CSS = ("body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:Nunito,Arial,sans-serif;"
            "background:linear-gradient(135deg,#2D4A3E,#6B8F5E,#E9DFC7)}.c{background:#fffffff2;border-radius:28px;padding:32px 40px;"
            "max-width:420px;text-align:center;color:#1F3329;box-shadow:0 20px 50px #0004}.n{font-size:3rem;font-weight:800;color:#2D4A3E}"
            "li{text-align:left;margin:4px 0}.tl-path{stroke-dasharray:1;stroke-dashoffset:1;animation:d 1.6s ease forwards}"
            ".tl-fill{opacity:0;animation:f .8s ease 1.2s forwards}@keyframes d{to{stroke-dashoffset:0}}@keyframes f{to{opacity:1}}")


def build_impact_card(name: str, month: str, m: pd.DataFrame, eq: dict) -> str:
    """A standalone, shareable HTML 'impact card' for one month."""
    top = m.groupby("type")["co2"].sum().sort_values(ascending=False).head(3)
    rows = "".join(f"<li>{html.escape(t)}: {v:.1f} kg CO₂</li>" for t, v in top.items())
    return (f"<!doctype html><meta charset='utf-8'><title>My ShopImpact card</title><style>{CARD_CSS}</style>"
            f"<div class='c'>{draw_leaf_svg()}<h1>{html.escape(name)}'s impact · {html.escape(month)}</h1>"
            f"<div class='n'>{m['co2'].sum():.1f} kg CO₂e</div><p>{len(m)} purchases · ${m['price'].sum():.2f} spent</p>"
            f"<ul>{rows}</ul><p>≈ {eq['km']} km by car · ≈ {eq['charges']} phone charges</p>"
            f"<small>Simplified learning estimates · made with ShopImpact</small></div>")


def export_json() -> str:
    return json.dumps({"groceries": ss.groceries, "purchases": ss.purchases, "badges": ss.badges, "avatar": ss.get("avatar")}, indent=2)


def import_json(text: str) -> str:
    """Load data from an exported JSON file. Everything is validated first; saved data is only
    replaced once the whole file has been checked, and invalid rows are counted and skipped."""
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("top level must be an object")
        raw_p, raw_g = data.get("purchases", []), data.get("groceries", [])
        if not isinstance(raw_p, list) or not isinstance(raw_g, list):
            raise ValueError("purchases and groceries must be lists")
    except (ValueError, TypeError):
        return "Sorry, that file doesn't look like a ShopImpact export. Nothing was changed."
    purchases, groceries, skipped = [], [], 0
    for p in raw_p:
        try:
            price = float(p["price"])
            d = datetime.strptime(str(p["date"]), "%Y-%m-%d").date()
            if p["type"] not in PRODUCTS or not validate_purchase(p["type"], price, d, str(p.get("brand", "")))[0]:
                raise ValueError("invalid purchase")
            purchases.append({"date": d.isoformat(), "type": p["type"], "brand": str(p.get("brand", "") or "Unbranded")[:MAX_BRAND_LEN],
                              "price": round(price, 2), "co2": calculate_impact(p["type"], price),
                              "ethical": bool(p.get("ethical", False)), "status": purchase_status(d)})
        except (KeyError, TypeError, ValueError, AttributeError):
            skipped += 1
    for g in raw_g:
        try:
            qty, price = int(g.get("qty", 1)), float(g.get("price", 0))
            if g.get("type") not in PRODUCTS or not str(g.get("name", "")).strip() or qty < 1 or not 0 <= price <= MAX_PRICE:
                raise ValueError("invalid item")
            groceries.append({"name": str(g["name"]).strip(), "type": g["type"], "brand": str(g.get("brand", "")),
                              "qty": qty, "price": price, "done": bool(g.get("done", False))})
        except (KeyError, TypeError, ValueError, AttributeError):
            skipped += 1
    if not purchases and not groceries and skipped:
        return "No valid rows were found in that file. Nothing was changed."
    ss.purchases, ss.groceries = [], []
    for p in purchases:
        ss.purchases.append({**p, "id": ss.next_id}); ss.next_id += 1
    for g in groceries:
        ss.groceries.append({**g, "id": ss.next_id}); ss.next_id += 1
    ss.badges = [b for b in data.get("badges", []) if b in BADGES] if isinstance(data.get("badges"), list) else []
    if valid_avatar(data.get("avatar")):
        ss.avatar = {k: int(data["avatar"][k]) for k in AV_LIMITS}
        save_avatar_file(ss.avatar)
    note = f" {skipped} invalid row(s) were skipped." if skipped else ""
    return f"Loaded {len(ss.purchases)} purchases and {len(ss.groceries)} list items.{note}"


# =============================================================================
# 4. LOOK AND FEEL (animated background + custom CSS)
# =============================================================================
CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html {font-size:17px;}
html, body, .stApp, .stApp button, .stApp input, .stApp textarea {font-family:'DM Sans',system-ui,sans-serif;}
.stApp {font-weight:500; color:var(--text);}

/* ---------- 1. TYPOGRAPHY: one sans-serif family, clear hierarchy ---------- */
h1,h2,h3,h4 {font-family:'DM Sans',system-ui,sans-serif !important; font-weight:700 !important; letter-spacing:-.01em; color:var(--accent) !important;}
.stApp p, .stApp li, .stApp label, .stApp [data-testid="stMarkdownContainer"] {color:var(--text); font-size:1.02rem; font-weight:500; line-height:1.55;}
.stApp strong, .stApp b {font-weight:700;}
[data-testid="stCaptionContainer"] p, .muted {color:var(--muted) !important; font-weight:500 !important; font-size:.94rem !important;}
[data-testid="stWidgetLabel"] {margin-bottom:4px;}
[data-testid="stWidgetLabel"] p {font-weight:700 !important; font-size:.96rem !important; color:var(--text) !important;}

/* ---------- 2. PAGE FRAME ---------- */
.stApp, .stApp [data-testid="stAppViewContainer"], .stApp [data-testid="stHeader"] {background:transparent !important;}
[data-testid="stMain"] {position:relative; z-index:1;}
[data-testid="stSidebar"] {z-index:2; background:var(--card) !important; border-right:1px solid var(--border);}
.block-container {max-width:1240px; padding-top:2rem; padding-bottom:3rem;}
.si-bg {position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden;}
.si-grad {position:absolute; inset:0; background:var(--bg);}
.si-grain {position:absolute; inset:0; background-image:radial-gradient(var(--dot) 1px, transparent 1.3px); background-size:28px 28px;}
.si-orb {position:absolute; border-radius:50%; filter:blur(90px);}
.si-orb.o1 {width:42vw; height:42vw; top:-14vw; right:-10vw; background:radial-gradient(circle,var(--orb1),transparent 68%);}
.si-orb.o2 {width:46vw; height:46vw; bottom:-20vw; left:-12vw; background:radial-gradient(circle,var(--orb2),transparent 68%);}

/* ---------- 3. CARDS AND CONTAINERS: one style everywhere ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {background:var(--card); border-radius:14px; border:1px solid var(--border) !important;
  box-shadow:var(--shadow); padding:.7rem 1rem;}
[data-testid="stExpander"] {border:1px solid var(--border) !important; border-radius:12px !important; background:var(--card);}
[data-testid="stExpander"] summary p {font-weight:700 !important; font-size:1.02rem !important; color:var(--text);}
[data-testid="stMetric"] {background:var(--card); border-radius:12px; padding:14px 18px; box-shadow:var(--shadow); border:1px solid var(--border);}
[data-testid="stMetricLabel"] p {font-weight:600 !important; color:var(--muted) !important; font-size:.92rem !important;}
[data-testid="stMetricValue"] {font-size:1.9rem; font-weight:700; color:var(--accent);}
[data-testid="stAlert"], [data-testid="stAlertContainer"] {background:var(--tab-off) !important; border:1px solid var(--border) !important; border-radius:12px !important; color:var(--text) !important;}
[data-testid="stAlert"] p {color:var(--text) !important;}
[data-testid="stForm"] {border:none !important; padding:0 !important; background:transparent;}

/* ---------- 4. FORM CONTROLS ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {border-radius:10px !important; background:var(--input) !important;}
[data-baseweb="input"], [data-baseweb="select"] > div {border:1px solid var(--border) !important;}
.stApp input, .stApp textarea {color:var(--text) !important; min-height:44px; font-size:1rem; font-weight:500;}
.stProgress > div > div > div > div {background:linear-gradient(90deg,var(--accent2),var(--accent)) !important;}
[data-testid="stCheckbox"] span[data-baseweb="checkbox"] > span {border-color:var(--accent2) !important;}

/* ---------- 5. BUTTONS ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {border-radius:10px; font-weight:700; font-size:1rem;
  border:1.5px solid var(--accent2); background:var(--card); color:var(--text); min-height:44px; transition:box-shadow .15s ease, border-color .15s ease, background .15s ease;}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover
  {box-shadow:0 3px 10px rgba(35,71,53,.14); border-color:var(--accent); background:var(--tab-off);}
button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]
  {background:var(--accent) !important; border-color:var(--accent) !important;}
button[kind="primary"] *, button[kind="primaryFormSubmit"] *, button[data-testid="stBaseButton-primary"] *, button[data-testid="stBaseButton-primaryFormSubmit"] * {color:var(--on-accent) !important;}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {width:100%;}

/* main navigation: three equal, separate, button-style tabs */
.nav-anchor {height:0; margin:0;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"], .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] {gap:14px; margin-bottom:6px;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton,
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button {width:100%;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button
  {min-height:58px; border-radius:14px; font-size:1.12rem; box-shadow:var(--shadow);}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button p, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button p {font-size:1.12rem !important; font-weight:700 !important;}

/* ---------- 6. SECTION HEADINGS AND SMALL TEXT ---------- */
.sec {margin:2px 0 14px;}
.sec-head {display:flex; align-items:center; gap:12px;}
.sec-n {flex:none; width:28px; height:28px; border-radius:50%; background:var(--accent); color:var(--on-accent); font-weight:700; display:grid; place-items:center; font-size:.9rem;}
.sec-title {font-weight:700; font-size:1.3rem; color:var(--accent); line-height:1.25;}
.sec-sub {font-weight:500; font-size:.96rem; color:var(--muted); margin-top:4px;}
.mini-title {font-weight:700; font-size:1.02rem; margin:10px 0 4px; color:var(--text);}
.kicker {font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); font-weight:700; margin:6px 0 2px;}
.chip {display:inline-block; padding:4px 12px; border-radius:8px; background:var(--tab-off); border:1px solid var(--border); font-weight:600; font-size:.9rem; margin:2px 6px 2px 0; color:var(--text);}
.big-num {font-size:2.6rem; font-weight:800; color:var(--accent); line-height:1.1;}

/* ---------- 7. HEADER ---------- */
.hero {display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:20px; background:var(--card); border-radius:16px;
  padding:20px 28px; margin-bottom:18px; border:1px solid var(--border); box-shadow:var(--shadow);}
.hero-left {display:flex; align-items:center; gap:20px;}
.hero-title {font-size:2.1rem; font-weight:800; color:var(--accent); line-height:1.1; letter-spacing:-.02em;}
.hero-sub {font-size:1.05rem; color:var(--muted); font-weight:600; margin-top:4px;}
.hero-stats {display:flex; gap:12px; flex-wrap:wrap;}
.stat {min-width:104px; padding:12px 14px; border-radius:12px; background:var(--tab-off); border:1px solid var(--border); text-align:center;}
.stat-num {font-size:1.6rem; font-weight:800; color:var(--accent); line-height:1.1;}
.stat-label {font-size:.82rem; color:var(--muted); font-weight:600; margin-top:2px;}
.bubble {display:inline-block; margin-top:10px; padding:8px 16px; border-radius:12px 12px 12px 4px; background:var(--tab-off); border:1px solid var(--border); font-weight:600; font-size:.96rem; color:var(--text);}
.mascot {animation:bob 4.2s ease-in-out infinite; flex:none;}
.mascot svg {background:var(--mascot-bg); border-radius:18px; padding:4px;}
.mascot-box {text-align:center; flex:none;}
.mascot-name {font-weight:800; font-size:1.05rem; color:var(--accent); line-height:1;}
.mascot-role {font-size:.78rem; color:var(--muted); font-weight:600;}
@keyframes bob {50%{transform:translateY(-5px)}}

/* ---------- 8. GUIDES AND STEP CARDS ---------- */
.steps {display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:0 0 12px;}
.step {display:flex; gap:12px; align-items:flex-start; padding:14px 16px; background:var(--card); border:1px solid var(--border); border-radius:12px;}
.step-n {flex:none; width:28px; height:28px; border-radius:50%; background:var(--accent); color:var(--on-accent); font-weight:700; display:grid; place-items:center; font-size:.9rem;}
.step-t {font-weight:700; font-size:1.02rem; color:var(--text);}
.step-d {font-size:.93rem; color:var(--muted); font-weight:500; margin-top:2px;}
.guide-intro {font-size:1.04rem; font-weight:600; color:var(--text); margin:2px 0 12px;}
.guide-tip {margin-top:6px; padding:12px 16px; border-radius:12px; background:rgba(176,141,87,.14); border-left:4px solid var(--gold); font-size:.96rem; font-weight:600; color:var(--text);}

/* ---------- 9. RIGHT-HAND SUMMARY CARDS ---------- */
.side-head {display:flex; align-items:center; gap:10px; font-weight:700; font-size:1.02rem; color:var(--accent); margin-bottom:12px;}
.side-head .ico {width:30px; height:30px; border-radius:9px; background:var(--tab-off); border:1px solid var(--border); display:grid; place-items:center; font-size:.95rem;}
.side-big {font-size:2rem; font-weight:800; color:var(--accent); line-height:1.1;}
.side-big small {font-size:.88rem; font-weight:600; color:var(--muted); margin-left:6px;}
.side-row {display:flex; justify-content:space-between; align-items:center; margin:10px 0 2px; font-size:.92rem; color:var(--muted); font-weight:600;}
.lvl {padding:2px 10px; border-radius:999px; font-size:.8rem; font-weight:700; border:1px solid var(--border);}
.lvl.low {background:rgba(135,155,118,.25); color:var(--text);}
.lvl.mid {background:rgba(176,141,87,.22); color:var(--text);}
.lvl.high {background:rgba(160,90,70,.20); color:var(--text);}
.pbar {height:8px; border-radius:99px; background:rgba(115,125,82,.20); overflow:hidden; margin:8px 0 6px;}
.pbar i {display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,var(--accent2),var(--accent));}
.side-note {font-size:.84rem; color:var(--muted); font-weight:500; line-height:1.4;}
.side-two {display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:6px;}
.side-two div {background:var(--tab-off); border:1px solid var(--border); border-radius:10px; padding:10px 12px;}
.side-two b {display:block; font-size:1.5rem; font-weight:800; color:var(--accent); line-height:1.15;}
.side-two span {font-size:.8rem; color:var(--muted); font-weight:600;}
.side-next {margin-top:8px; padding:10px 12px; border-radius:10px; background:var(--tab-off); border:1px solid var(--border); font-size:.9rem; color:var(--text); font-weight:600;}

/* ---------- 10. ACHIEVEMENTS GALLERY ---------- */
.ach-wrap {margin-top:26px;}
.ach-count {font-size:.82rem; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); font-weight:700; margin:14px 0 4px;}
.ach-grid {display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:14px; margin:8px 0 6px;}
.ach {display:flex; gap:12px; align-items:flex-start; padding:14px 16px; border-radius:14px; background:var(--card); border:1px solid var(--border); box-shadow:var(--shadow);}
.ach.earned {border-color:var(--gold); background:linear-gradient(180deg,var(--card),rgba(176,141,87,.10));}
.ach.locked {background:var(--tab-off); box-shadow:none;}
.ach-ico {flex:none; width:44px; height:44px; border-radius:12px; display:grid; place-items:center; font-size:1.35rem; background:var(--tab-off); border:1px solid var(--border);}
.ach.earned .ach-ico {background:rgba(176,141,87,.16); border-color:var(--gold);}
.ach.locked .ach-ico {filter:grayscale(1); opacity:.6; background:var(--card);}
.ach-body {flex:1; min-width:0;}
.ach-name {font-weight:700; font-size:1rem; color:var(--text); line-height:1.25;}
.ach-desc {font-size:.86rem; color:var(--muted); font-weight:500; margin-top:3px; line-height:1.4;}
.ach-tag {font-size:.7rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:var(--gold-d); margin-bottom:2px;}
.ach-prog {font-size:.78rem; color:var(--muted); font-weight:600; margin-top:2px;}
.ach.new {animation:achGlow 2.6s ease-out 2;}
@keyframes achGlow {0% {box-shadow:0 0 0 0 rgba(176,141,87,.55);} 100% {box-shadow:0 0 0 14px rgba(176,141,87,0);}}

/* ---------- 10b. MOCKUP REFINEMENTS: header, page heading, ring cards, achievements panel ---------- */
.topbar {display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:16px; margin-bottom:12px;}
.brand {display:flex; align-items:center; gap:14px;}
.logo {width:40px; height:40px; border-radius:12px; background:var(--accent); display:grid; place-items:center;}
.logo svg {width:22px; height:22px; stroke:var(--on-accent); fill:none; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round;}
.brand-name {font-size:1.6rem; font-weight:800; color:var(--accent); letter-spacing:-.02em;}
.brand-div {width:1px; height:22px; background:var(--border);}
.brand-sub {font-size:.95rem; font-weight:500; color:var(--muted);}
.user {display:flex; align-items:center; gap:18px;}
.welcome {font-size:1rem; font-weight:600; color:var(--text);}
.chip-user {display:flex; align-items:center; gap:10px; padding:5px 16px 5px 5px; border-radius:999px; background:var(--card); border:1px solid var(--border);}
.avatar {width:32px; height:32px; border-radius:50%; background:var(--sage); color:#234735; font-weight:800; display:grid; place-items:center; font-size:.9rem;}
.uname {font-size:.92rem; font-weight:700;}
.carty {display:flex; align-items:center; gap:14px; padding:8px 16px; margin-bottom:14px; background:var(--card); border:1px solid var(--border); border-radius:14px; box-shadow:var(--shadow);}
.carty .bubble {margin:0;}
.page-head {margin:2px 0 14px;}
.page-head h1 {margin:0 !important; padding:0 !important; font-size:1.9rem !important; font-weight:800 !important; letter-spacing:-.02em;}
.page-desc {color:var(--muted); font-size:1.02rem; font-weight:500; margin-top:4px;}
.ring-row {display:flex; align-items:center; gap:18px; margin:4px 0 8px;}
.ring {position:relative; width:96px; height:96px; flex:none;}
.ring svg {width:96px; height:96px;}
.ring .trk {stroke:var(--tab-off);} .ring .val {stroke:var(--accent);}
.ring b {position:absolute; inset:0; display:grid; place-items:center; font-size:1.3rem; font-weight:800; color:var(--accent);}
.side-head .ico svg {width:16px; height:16px; stroke:var(--accent); fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round;}
.side-meal {font-size:1.12rem; font-weight:700; color:var(--text); margin-top:2px;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button
  {min-height:52px; font-size:1.05rem; background:var(--tab-off); box-shadow:none;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button p, .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] .stButton > button p {font-size:1.05rem !important;}
[data-testid="stElementContainer"]:has(.nav-anchor) + [data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-primary"], .element-container:has(.nav-anchor) + [data-testid="stHorizontalBlock"] button[kind="primary"] {box-shadow:0 6px 16px rgba(35,71,53,.22) !important;}
.ach-panel {background:var(--tab-off); border:1px solid var(--border); border-radius:18px; padding:18px 22px 20px; margin-top:26px;}
.ach-head {display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:6px;}
.ach-title {font-weight:700; font-size:1.2rem; color:var(--accent);}
.ach-meta {font-size:.92rem; font-weight:600; color:var(--muted);}
.ach-panel .ach {box-shadow:none; background:var(--card);}
.ach-panel .ach.earned {border-color:var(--accent2); background:var(--card);}
.ach.earned .ach-ico {background:var(--accent); color:var(--on-accent); border-color:var(--accent);}
.ach.locked .ach-ico {filter:none; opacity:1; background:var(--tab-off); color:var(--muted);}
.ach-ico svg {width:26px; height:26px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round;}
.ach-tag {color:var(--accent);}

/* ---------- 10c. PROFILE + AVATAR CREATOR ---------- */
.prof-box {text-align:center; padding:2px 0 8px;}
.prof-av {display:flex; justify-content:center; margin:8px 0 8px;}
.prof-av svg, .prof-ph {box-shadow:0 0 0 3px var(--card), 0 0 0 4.5px var(--accent2);}
.prof-ph {width:112px; height:112px; border-radius:50%; background:var(--sage); color:#234735; font-size:2.6rem; font-weight:800; display:grid; place-items:center;}
.prof-name {font-weight:800; font-size:1.2rem; color:var(--accent);}
.prof-hint {font-size:.88rem; color:var(--muted); font-weight:500; margin:2px 0 8px;}
.av-edit {height:0;}
[data-testid="stElementContainer"]:has(.av-edit) + [data-testid="stElementContainer"] button, .element-container:has(.av-edit) + .element-container button {min-height:34px; font-size:.88rem; padding:2px 12px;}
[data-testid="stSidebar"] .stButton, [data-testid="stSidebar"] .stButton > button {width:100%;}
.chip-user .avatar-svg svg {width:34px; height:34px;}
.av-steps {display:flex; align-items:center; justify-content:center; gap:10px; margin:0 0 16px; flex-wrap:wrap;}
.av-s {display:flex; align-items:center; gap:8px; color:var(--muted); font-weight:600; font-size:.9rem;}
.av-s b {width:26px; height:26px; border-radius:50%; display:grid; place-items:center; background:var(--tab-off); border:1px solid var(--border); font-size:.8rem;}
.av-s.on {color:var(--text);} .av-s.on b {background:var(--accent); color:var(--on-accent); border-color:var(--accent);}
.av-s.done b {background:var(--sage); color:#234735; border-color:var(--sage);}
.av-s:not(:last-child)::after {content:''; width:34px; height:2px; background:var(--border); margin-left:6px;}
.av-prev {text-align:center; background:var(--tab-off); border:1px solid var(--border); border-radius:18px; padding:16px 8px 12px;}
.av-prev svg {margin:0 auto;}
.av-h {font-weight:700; font-size:1.1rem; color:var(--accent); margin:6px 0 2px;}
.av-sub {color:var(--muted); font-size:.9rem; font-weight:500; margin-bottom:8px;}
.av-tile {border:1.5px solid var(--border); border-radius:14px; padding:8px 4px 6px; text-align:center; background:var(--card); margin:4px 0 6px;}
.av-tile.sel {border-color:var(--accent); box-shadow:0 0 0 3px var(--dot-off);}
.av-tile svg {margin:0 auto; max-width:100%; height:auto;}
.av-lbl {font-size:.82rem; font-weight:700; margin-top:4px; color:var(--text);}
.av-sw {width:34px; height:34px; border-radius:50%; margin:4px auto 0; box-shadow:0 0 0 1.5px var(--border);}
.av-tile.sel .av-sw {box-shadow:0 0 0 3px var(--accent);}
.av-nav {height:0;}
[data-testid="stDialog"] div[role="dialog"] {background:var(--card) !important; border:1px solid var(--border); border-radius:18px;}
[data-testid="stDialog"] .stButton, [data-testid="stDialog"] .stButton > button {width:100%;}
[data-testid="stDialog"] .stButton > button {min-height:36px; padding:2px 8px; font-size:.88rem;}
[data-testid="stElementContainer"]:has(.av-nav) + [data-testid="stHorizontalBlock"] .stButton > button, .element-container:has(.av-nav) + [data-testid="stHorizontalBlock"] .stButton > button {min-height:46px; font-size:1rem;}

/* ---------- 11. REMINDER, DRAWINGS ---------- */
.reminder {background:var(--card); border:1px solid var(--gold); border-left:5px solid var(--gold); color:var(--text); border-radius:12px; padding:14px 20px; margin-bottom:14px; box-shadow:var(--shadow);}
.reminder, .reminder * {color:var(--text) !important;}
.tl-svg {display:block; margin:6px auto;}
.tl-path {stroke-dasharray:1; stroke-dashoffset:1; animation:tlDraw 1.6s ease forwards;}
.tl-fill {opacity:0; animation:tlFade .8s ease 1.2s forwards;}
@keyframes tlDraw {to {stroke-dashoffset:0}}
@keyframes tlFade {to {opacity:1}}

/* ---------- 12. ONBOARDING ---------- */
.ob-hero {text-align:center; margin:1vh 0 18px;}
.ob-title {font-size:2.2rem; font-weight:800; color:var(--accent); letter-spacing:-.02em; margin-top:8px;}
.ob-tag {font-size:1rem; color:var(--muted); font-weight:600;}
.ob-bubble {display:inline-block; margin-top:14px; padding:10px 18px; border-radius:14px; background:var(--card); border:1px solid var(--border); color:var(--text); font-weight:600; box-shadow:var(--shadow);}
.ob-dots {display:flex; justify-content:center; align-items:center; gap:14px; margin:4px 0 22px;}
.ob-dots span {display:block; width:9px; height:9px; border-radius:50%; background:var(--dot-off);}
.ob-dots span.done {background:var(--dot-done);}
.ob-dots span.on {background:var(--accent); box-shadow:0 0 0 4px var(--dot-off);}
.ob-step {text-align:center; font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; font-weight:700; color:var(--muted);}
.ob-q {text-align:center; font-size:1.45rem; font-weight:700; color:var(--accent); margin:6px 0 22px; line-height:1.25;}

@media (max-width:700px) {
  .block-container {padding-left:1rem; padding-right:1rem;}
  .hero {padding:16px; } .hero-left {flex-wrap:wrap;} .hero-stats {width:100%;} .stat {flex:1;}
}
@media (prefers-reduced-motion: reduce) {
  .mascot, .tl-fill, .ach.new {animation:none !important;}
  .tl-path {animation:none !important; stroke-dashoffset:0 !important;} .tl-fill {opacity:1 !important;}
}
"""
ONBOARD_CSS = """[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapseButton"] {display:none;}
.block-container {max-width:600px; padding-top:2.2rem;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px; padding:1.6rem 1.8rem 1.4rem;}
[data-testid="stForm"] [data-testid="stHorizontalBlock"] {gap:14px;}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {min-height:48px;}"""


def render_background() -> None:
    """Inject the calm earthy-green background (soft gradient, faint dot texture, two quiet glows) and the colour system."""
    palette = ("--card:rgba(27,42,34,.96);--text:#F2F0E6;--muted:#BAC7BA;--accent:#A3B18A;--accent2:#879B76;--sage:#A3B18A;--olive:#737D52;--gold:#D6B76B;--gold-d:#D6B76B;"
               "--border:rgba(163,177,138,.30);--input:#15221B;--on-accent:#14201A;--mascot-bg:#E6EEDF;--tab-off:rgba(163,177,138,.12);"
               "--bg:linear-gradient(135deg,#0F1914 0%,#16251D 50%,#0F1914 100%);--dot:rgba(163,177,138,.07);--orb1:rgba(115,125,82,.20);--orb2:rgba(135,155,118,.14);"
               "--shadow:0 6px 18px rgba(0,0,0,.28);--dot-off:rgba(163,177,138,.28);--dot-done:#5F7255;") if ss.hc else (
        "--card:rgba(252,251,247,.97);--text:#26332B;--muted:#5A6A5E;--accent:#234735;--accent2:#879B76;--sage:#A3B18A;--olive:#737D52;--gold:#B08D57;--gold-d:#8A6A38;"
        "--border:rgba(115,125,82,.30);--input:#FFFFFF;--on-accent:#FFFFFF;--mascot-bg:transparent;--tab-off:#EEF2E8;"
        "--bg:linear-gradient(135deg,#F7F5EC 0%,#EEF2E8 50%,#F7F5EC 100%);--dot:rgba(115,125,82,.10);--orb1:rgba(163,177,138,.42);--orb2:rgba(176,141,87,.16);"
        "--shadow:0 1px 2px rgba(35,71,53,.05),0 6px 18px rgba(35,71,53,.07);--dot-off:rgba(115,125,82,.28);--dot-done:#A3B18A;")
    st.markdown(f"<style>:root{{{palette}}}{CSS_BASE}</style>"
                "<div class='si-bg'><div class='si-grad'></div><div class='si-grain'></div><div class='si-orb o1'></div><div class='si-orb o2'></div></div>",
                unsafe_allow_html=True)


def chart_theme() -> dict:
    """Colours that match the app theme (light or dark/high-contrast)."""
    if ss.hc:
        return {"text": "#F2F0E6", "muted": "#BAC7BA", "grid": "rgba(163,177,138,.22)", "main": "#A3B18A",
                "cats": {"Food": "#A3B18A", "Household": "#D6B76B", "Clothing": "#6F9A86"}}
    return {"text": "#26332B", "muted": "#5A6A5E", "grid": "rgba(115,125,82,.20)", "main": "#234735",
            "cats": {"Food": "#234735", "Household": "#879B76", "Clothing": "#B08D57"}}


def style_chart(ch: alt.Chart, height: int = 320) -> alt.Chart:
    """Apply the app fonts, bigger labels, soft grid lines and a transparent background to any Altair chart."""
    t = chart_theme()
    return (ch.properties(height=height, background="transparent", padding={"left": 6, "right": 14, "top": 10, "bottom": 6})
            .configure_view(stroke=None)
            .configure_axis(labelFont="DM Sans", titleFont="DM Sans", labelColor=t["text"], titleColor=t["text"], labelFontSize=13,
                            titleFontSize=14, titleFontWeight="bold", labelFontWeight=600, gridColor=t["grid"],
                            domainColor=t["grid"], tickColor=t["grid"], titlePadding=10)
            .configure_legend(labelFont="DM Sans", titleFont="DM Sans", labelColor=t["text"], titleColor=t["text"],
                              labelFontSize=13, titleFontSize=14, titleFontWeight="bold", symbolType="circle", symbolSize=140,
                              orient="top", padding=4))


def show_chart(ch: alt.Chart) -> None:
    st.altair_chart(ch, theme=None)


def co2_bar_chart(m: pd.DataFrame) -> None:
    """Horizontal bars: CO2 per product type, coloured by category, with the value written at the end of each bar."""
    t = chart_theme()
    d = m.groupby(["type", "category"], as_index=False)["co2"].sum().sort_values("co2", ascending=False)
    d["co2"] = d["co2"].round(2)
    base = alt.Chart(d).encode(y=alt.Y("type:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)))
    bars = base.mark_bar(cornerRadiusEnd=7, size=22).encode(
        x=alt.X("co2:Q", title="kg CO₂", axis=alt.Axis(grid=True)),
        color=alt.Color("category:N", title="Category", scale=alt.Scale(domain=list(t["cats"]), range=list(t["cats"].values()))),
        tooltip=[alt.Tooltip("type:N", title="Product"), alt.Tooltip("category:N", title="Category"), alt.Tooltip("co2:Q", title="kg CO₂", format=".2f")])
    labels = base.mark_text(align="left", dx=6, font="DM Sans", fontWeight="bold", fontSize=13, color=t["text"]).encode(
        x="co2:Q", text=alt.Text("co2:Q", format=".1f"))
    show_chart(style_chart(bars + labels, height=max(220, 34 * len(d) + 50)))


def co2_line_chart(m: pd.DataFrame) -> None:
    """Soft area + line with dots for CO2 per day, with tooltips."""
    t = chart_theme()
    d = m.groupby(m["date"].dt.date, as_index=False)["co2"].sum()
    d.columns = ["day", "co2"]
    d["day"] = pd.to_datetime(d["day"])
    d["co2"] = d["co2"].round(2)
    base = alt.Chart(d).encode(x=alt.X("day:T", title=None, axis=alt.Axis(format="%d %b", labelAngle=0, tickCount=6)),
                               y=alt.Y("co2:Q", title="kg CO₂ per day", scale=alt.Scale(zero=True)))
    area = base.mark_area(color=t["main"], opacity=0.18, interpolate="monotone")
    line = base.mark_line(color=t["main"], strokeWidth=3.5, interpolate="monotone")
    dots = base.mark_circle(color=t["main"], size=110, opacity=1, stroke="#FCFBF7" if not ss.hc else "#15221B", strokeWidth=2).encode(
        tooltip=[alt.Tooltip("day:T", title="Date", format="%d %b %Y"), alt.Tooltip("co2:Q", title="kg CO₂", format=".2f")])
    show_chart(style_chart(area + line + dots))


def co2_scatter_chart(m: pd.DataFrame) -> None:
    """Each dot is a purchase: spend vs CO2, coloured by category, with a tooltip showing the details."""
    t = chart_theme()
    d = m[["price", "co2", "category", "type", "brand"]].copy()
    d["co2"] = d["co2"].round(2)
    ch = alt.Chart(d).mark_circle(size=190, opacity=0.85, stroke="#FFFFFF" if not ss.hc else "#0B120E", strokeWidth=1.5).encode(
        x=alt.X("price:Q", title="Price ($)", scale=alt.Scale(zero=True)),
        y=alt.Y("co2:Q", title="kg CO₂", scale=alt.Scale(zero=True)),
        color=alt.Color("category:N", title="Category", scale=alt.Scale(domain=list(t["cats"]), range=list(t["cats"].values()))),
        tooltip=[alt.Tooltip("type:N", title="Product"), alt.Tooltip("brand:N", title="Brand"),
                 alt.Tooltip("price:Q", title="Price ($)", format=".2f"), alt.Tooltip("co2:Q", title="kg CO₂", format=".2f")])
    show_chart(style_chart(ch))


def guide(title: str, intro: str, steps: list[tuple[str, str]], tip: str = "") -> None:
    """A 'how to use this tab' guide shown first, open by default. The user can fold it away once they know the tab."""
    with st.expander(f"📖 How to use {title} (start here)", expanded=True):
        st.markdown(f"<div class='guide-intro'>{html.escape(intro)}</div>", unsafe_allow_html=True)
        cards = "".join(f"<div class='step'><div class='step-n'>{i}</div><div><div class='step-t'>{html.escape(t)}</div>"
                        f"<div class='step-d'>{html.escape(d)}</div></div></div>" for i, (t, d) in enumerate(steps, 1))
        st.markdown(f"<div class='steps'>{cards}</div>", unsafe_allow_html=True)
        if tip:
            st.markdown(f"<div class='guide-tip'>💡 {html.escape(tip)}</div>", unsafe_allow_html=True)


def section(title: str, sub: str = "", n: int | None = None) -> None:
    """A section heading: optional step number, bold title with a thin brass rule, then a regular-weight helper line."""
    num = f"<div class='sec-n'>{n}</div>" if n else ""
    helper = f"<div class='sec-sub'>{html.escape(sub)}</div>" if sub else ""
    st.markdown(f"<div class='sec'><div class='sec-head'>{num}<div class='sec-title'>{html.escape(title)}</div></div>{helper}</div>",
                unsafe_allow_html=True)


def show_drawing(svg: str, caption: str) -> None:
    st.markdown(f"<div style='text-align:center'>{svg}<div class='chip'>{html.escape(caption)}</div></div>",
                unsafe_allow_html=True)


# =============================================================================
# 5. ONBOARDING (one friendly card at a time)
# =============================================================================
def render_onboarding() -> None:
    """Full-screen welcome card with a step-by-step question flow."""
    step, p = ss.ob_step, ss.profile
    st.markdown(ONBOARD_CSS.join(["<style>", "</style>"]), unsafe_allow_html=True)
    dots = "".join(f"<span class='{'on' if i == step else 'done' if i < step else ''}'></span>" for i in range(4))
    says = ["Hi! I'm Carty, your shopping cart buddy. What's your name?", "Lovely! Where do you live?",
            "Great! What do you do?",
            "Last one: shall we plan meal prep together?"]
    questions = ["What's your name?", "Where do you live?", "What's your profession?",
                 "Do you want to do meal prepping?"]
    st.markdown(f"<div class='ob-hero'><div class='mascot'>{draw_mascot_svg('cheer' if step == 3 else 'happy', 140)}</div>"
                f"<div class='ob-title'>ShopImpact</div><div class='ob-tag'>Shop mindfully. Eat well. Love the planet.</div>"
                f"<div class='ob-bubble'>{html.escape(says[step])}</div></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<div class='ob-dots'>{dots}</div><div class='ob-step'>Step {step + 1} of 4</div>"
                    f"<div class='ob-q'>{questions[step]}</div>", unsafe_allow_html=True)
        with st.form(f"ob_form_{step}"):
            if step == 0:
                val = st.text_input("Your first name", value=p.get("name", ""), placeholder="e.g. Aisha")
            elif step == 1:
                val = st.text_input("City, country", value=p.get("location", ""), placeholder="e.g. Pune, India")
            elif step == 2:
                val = st.text_input("Profession (student, nurse, designer...)", value=p.get("profession", ""))
            else:
                opts = ["Yes, I love a good meal prep", "No, I prefer grab-and-go"]
                val = st.radio("Meal prepping", opts, index=0 if p.get("meal_prep", True) else 1, label_visibility="collapsed")
            c1, c2 = st.columns(2)
            back = c1.form_submit_button("← Back", disabled=step == 0)
            nxt = c2.form_submit_button("Let's go" if step == 3 else "Next →", type="primary")
    if back:
        ss.ob_step -= 1
        st.rerun()
    if nxt:
        error = ""
        if step in (0, 1, 2):
            text = (val or "").strip()
            limit = (40, 60, 60)[step]  # length limit enforced here, so no "4/60" counter shows beside the box
            error = ("" if text else "Please fill this in so I can personalise ShopImpact for you.") or \
                    ("" if len(text) <= limit else f"Please keep this under {limit} characters.")
            if not error:
                p[("name", "location", "profession")[step]] = text
        else:
            p["meal_prep"] = val.startswith("Yes")
        if error:
            st.warning(error)
        elif step < 3:
            ss.ob_step += 1
            st.rerun()
        else:
            ss.onboarded = True
            if not ss.get("configured"):  # only pre-fill on first setup, not when editing the profile
                ss.trip_time = suggest_shop_time(p)[0]
                ss.max_prep = 30 if profile_mode(p) == "busy" else 60
                ss.configured = True
            st.toast(f"Welcome, {p['name']}! Let's make shopping greener.")
            st.rerun()


# =============================================================================
# 6. SIDEBAR
# =============================================================================
def render_sidebar() -> None:
    """Sidebar: profile, settings and data tools only. Badges live in their own section."""
    p = ss.profile
    with st.sidebar:
        av = ss.get("avatar")
        art = draw_avatar_svg(av, 112) if av else f"<div class='prof-ph'>{html.escape(p['name'])[:1].upper() or '?'}</div>"
        st.markdown(f"<div class='prof-box'><div class='kicker'>My Profile</div><div class='prof-av'>{art}</div>"
                    f"<div class='prof-name'>{html.escape(p['name'])}</div></div>", unsafe_allow_html=True)
        if av:
            st.markdown("<div class='av-edit'></div>", unsafe_allow_html=True)
            st.button("✏️ Edit Avatar", key="av_edit", on_click=open_avatar, args=(True,))
        else:
            st.markdown("<div class='prof-hint' style='text-align:center'>Make a cartoon you in 3 quick steps.</div>", unsafe_allow_html=True)
            st.button("Create My Avatar", key="av_create", type="primary", on_click=open_avatar, args=(False,))
        with st.expander("Settings"):
            st.caption(f"{p.get('location', '')} · {p.get('profession', '')}")
            if st.button("Edit profile"):
                ss.onboarded, ss.ob_step = False, 0
                st.rerun()
            st.toggle("High-contrast / dark mode", key="hc")
            st.toggle("Auto-log bought items to my CO₂ tracker", key="autolog")
            st.number_input("Shopping for how many people?", min_value=1, max_value=12, step=1, key="people")
            st.number_input("Your UTC offset (hours)", min_value=-12.0, max_value=14.0, step=0.5, key="tz",
                            help="Streamlit Cloud runs on UTC. Set your offset (e.g. 5.5 for India) so reminders match your clock.")
        with st.expander("Save / load / reset data"):
            st.download_button("Download my data (JSON)", export_json(), "shopimpact_data.json", "application/json")
            up = st.file_uploader("Load a saved JSON", type="json")
            if up is not None and ss.import_sig != (up.name, up.size):
                ss.import_sig = (up.name, up.size)
                st.info(import_json(up.getvalue().decode("utf-8", errors="ignore")))
            if st.button("Reset list, purchases and badges"):
                for k in ("groceries", "purchases", "meal_plan", "badges"):
                    ss[k] = []
                ss.plan_imported, ss.last_log, ss.recent_badges = False, None, []
                st.rerun()


# =============================================================================
# AVATAR CREATOR: a simple, three-step cartoon avatar (character, look, save)
# =============================================================================
# Each avatar is just five small numbers, so it is quick to save, export and redraw.
AV_CHARS = [
    dict(name="Maya", skin="#F2C9A5", skin_d="#D9A97F", bg="#F3E3D8", eyes="dot", mouth="smile", hair=5, hair_color=1, outfit=2, acc=0),
    dict(name="Arjun", skin="#C68642", skin_d="#A56A2F", bg="#E3EAD7", eyes="dot", mouth="grin", hair=1, hair_color=0, outfit=3, acc=1),
    dict(name="Zoe", skin="#8D5524", skin_d="#6E3F18", bg="#F6E7C8", eyes="arc", mouth="grin", hair=3, hair_color=0, outfit=1, acc=0),
    dict(name="Leo", skin="#F6D5BF", skin_d="#DDB79B", bg="#E8D5CC", eyes="dot", mouth="smile", hair=0, hair_color=3, outfit=0, acc=3),
    dict(name="Priya", skin="#D49A6A", skin_d="#B97D4E", bg="#F2D8D8", eyes="arc", mouth="smile", hair=7, hair_color=0, outfit=4, acc=5),
    dict(name="Sam", skin="#E3A878", skin_d="#C98B5C", bg="#E3EAD7", eyes="dot", mouth="smile", hair=4, hair_color=2, outfit=5, acc=0),
    dict(name="Nia", skin="#6F4220", skin_d="#54300F", bg="#F6E7C8", eyes="arc", mouth="grin", hair=6, hair_color=0, outfit=6, acc=1),
    dict(name="Omar", skin="#A86B3E", skin_d="#8A5329", bg="#F3E3D8", eyes="dot", mouth="smile", hair=2, hair_color=0, outfit=7, acc=0),
]
AV_HAIR = ["Short", "Quiff", "Buzz", "Curly", "Bob", "Long", "Bun", "Ponytail"]
AV_HAIR_COLORS = [("Black", "#2B2220"), ("Cocoa", "#5A3A2A"), ("Auburn", "#9C4A2F"), ("Golden", "#D9A441"), ("Rose", "#C98B8B"), ("Silver", "#B9BDB5")]
AV_OUTFITS = ["Tee", "Hoodie", "Sweater", "Shirt", "Eco tee", "Jacket", "Stripes", "Blazer"]
AV_ACCS = ["None", "Glasses", "Shades", "Headphones", "Cap", "Leaf pin"]
AV_LIMITS = {"char": len(AV_CHARS), "hair": len(AV_HAIR), "hair_color": len(AV_HAIR_COLORS), "outfit": len(AV_OUTFITS), "accessory": len(AV_ACCS)}
AV_FILE = Path(globals().get("__file__", "shopimpact_app.py")).with_name("shopimpact_avatars.json")

_AV_FRONT_SHORT = "M60 90 C56 54 80 44 100 44 C122 44 144 54 140 90 C134 74 120 66 100 66 C80 66 66 74 60 90 Z"
_AV_FRONT = {
    "Short": _AV_FRONT_SHORT, "Bob": _AV_FRONT_SHORT, "Long": _AV_FRONT_SHORT, "Bun": _AV_FRONT_SHORT, "Ponytail": _AV_FRONT_SHORT,
    "Quiff": "M58 92 C48 52 88 32 118 40 C142 48 146 72 142 92 C138 72 122 62 98 66 C80 68 66 76 58 92 Z",
    "Buzz": "M62 84 C62 58 80 52 100 52 C120 52 138 58 138 84 C130 70 118 64 100 64 C82 64 70 70 62 84 Z",
    "Curly": "M66 76 C74 62 90 58 100 58 C112 58 128 62 134 76 C124 68 112 66 100 66 C88 66 76 68 66 76 Z",
}
_AV_BACK = {
    "Long": "<path d='M54 92 C46 140 54 170 74 176 L126 176 C146 170 154 140 146 92 Z'/>",
    "Bob": "<path d='M54 92 C50 126 54 142 68 146 L132 146 C146 142 150 126 146 92 Z'/>",
    "Curly": "".join(f"<circle cx='{x}' cy='{y}' r='{r}'/>" for x, y, r in [(62, 78, 18), (138, 78, 18), (56, 102, 16), (144, 102, 16), (72, 56, 18), (128, 56, 18), (100, 46, 20)]),
    "Bun": "<circle cx='100' cy='38' r='15'/>",
    "Ponytail": "<path d='M136 78 C168 84 170 130 150 156 C150 132 146 112 138 98 Z'/>",
}


def _av_outfit(i: int, skin: str) -> tuple[str, str]:
    neck = f"<path d='M84 145 Q100 164 116 145 Z' fill='{skin}'/>"
    return [
        ("#C06A4D", neck),
        ("#6B4A3A", "<path d='M68 150 Q100 126 132 150 L132 162 Q100 150 68 162Z' fill='#5A3D2F'/>" + neck
         + "<path d='M92 160V178M108 160V178' stroke='#FCFBF7' stroke-width='2.5' stroke-linecap='round'/>"),
        ("#C98B8B", neck + "<path d='M84 145 Q100 164 116 145' fill='none' stroke='#B27474' stroke-width='5' stroke-linecap='round'/>"),
        ("#EFE6D2", f"<path d='M86 144 L100 168 L114 144Z' fill='{skin}'/>"
         "<path d='M82 142 L100 170 L90 176 L74 150Z' fill='#FCFBF7' stroke='#CFC3AA' stroke-width='1.5'/>"
         "<path d='M118 142 L100 170 L110 176 L126 150Z' fill='#FCFBF7' stroke='#CFC3AA' stroke-width='1.5'/>"),
        ("#234735", neck + "<path d='M92 184 C92 172 100 168 112 168 C112 180 104 186 92 184Z' fill='#A3B18A'/>"),
        ("#D9A441", f"<path d='M86 144 L100 164 L114 144Z' fill='{skin}'/>"
         "<path d='M84 144 L100 162 L116 144' fill='none' stroke='#B8862A' stroke-width='4' stroke-linecap='round'/>"
         "<path d='M100 162 V200' stroke='#B8862A' stroke-width='3'/>"),
        ("#EFE6D2", neck + "<path d='M30 168H170M26 182H174M24 196H176' stroke='#C98B8B' stroke-width='6'/>"),
        ("#3C4A41", f"<path d='M86 144 L100 168 L114 144Z' fill='#F7F5EC'/>"
         "<path d='M100 168 L80 144 L72 150 L90 184Z' fill='#2F3B34'/><path d='M100 168 L120 144 L128 150 L110 184Z' fill='#2F3B34'/>"),
    ][i]


def _av_accessory(i: int) -> str:
    return [
        "",
        "<g fill='rgba(255,255,255,.25)' stroke='#26332B' stroke-width='3'><circle cx='86' cy='93' r='11.5'/><circle cx='114' cy='93' r='11.5'/></g>"
        "<path d='M97.5 93H102.5M74.5 92L63 90M125.5 92L137 90' stroke='#26332B' stroke-width='3' stroke-linecap='round'/>",
        "<rect x='74' y='84' width='24' height='17' rx='6' fill='#26332B'/><rect x='102' y='84' width='24' height='17' rx='6' fill='#26332B'/>"
        "<path d='M98 91H102' stroke='#26332B' stroke-width='3'/>",
        "<path d='M58 90 C54 36 146 36 142 90' fill='none' stroke='#26332B' stroke-width='6' stroke-linecap='round'/>"
        "<rect x='50' y='84' width='14' height='28' rx='7' fill='#C06A4D'/><rect x='136' y='84' width='14' height='28' rx='7' fill='#C06A4D'/>",
        "<path d='M58 82 C56 44 144 44 142 82 Z' fill='#C06A4D'/><path d='M96 80 H160 Q166 80 166 86 H96 Z' fill='#A4553B'/><circle cx='100' cy='48' r='4' fill='#A4553B'/>",
        "<path d='M128 168 C128 156 136 152 146 152 C146 164 138 170 128 168Z' fill='#879B76'/><path d='M130 166 L142 156' stroke='#FCFBF7' stroke-width='1.5'/>",
    ][i]


def draw_avatar_svg(av: dict, size: int = 120, view: str = "0 0 200 200", radius: str = "50%") -> str:
    """Draw a friendly cartoon avatar. Skin, face and background come from the chosen character, so every combination looks coordinated."""
    ch = AV_CHARS[av["char"]]
    skin, sd = ch["skin"], ch["skin_d"]
    hc, style = AV_HAIR_COLORS[av["hair_color"]][1], AV_HAIR[av["hair"]]
    body, detail = _av_outfit(av["outfit"], skin)
    eyes = ("<circle cx='86' cy='92' r='4.2' fill='#2B1F1A'/><circle cx='114' cy='92' r='4.2' fill='#2B1F1A'/>" if ch["eyes"] == "dot" else
            "<path d='M80 94 Q86 86 92 94M108 94 Q114 86 120 94' stroke='#2B1F1A' stroke-width='3.4' fill='none' stroke-linecap='round'/>")
    mouth = ("<path d='M89 111 Q100 121 111 111' stroke='#8A3B2E' stroke-width='3.2' fill='none' stroke-linecap='round'/>" if ch["mouth"] == "smile" else
             "<path d='M89 109 Q100 125 111 109 Z' fill='#7A2E24'/>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{view}' width='{size}' height='{size}' role='img' aria-label='Cartoon avatar' "
            f"style='border-radius:{radius};overflow:hidden;display:block'>"
            f"<rect width='200' height='200' fill='{ch['bg']}'/>"
            f"<g fill='{hc}'>{_AV_BACK.get(style, '')}</g>"
            f"<rect x='88' y='120' width='24' height='30' rx='10' fill='{sd}'/>"
            f"<path d='M24 200 C24 158 58 144 100 144 C142 144 176 158 176 200 Z' fill='{body}'/>{detail}"
            f"<circle cx='62' cy='95' r='7' fill='{skin}'/><circle cx='138' cy='95' r='7' fill='{skin}'/>"
            f"<ellipse cx='100' cy='92' rx='38' ry='43' fill='{skin}'/>"
            f"<circle cx='76' cy='106' r='6' fill='#E58F7A' opacity='.28'/><circle cx='124' cy='106' r='6' fill='#E58F7A' opacity='.28'/>"
            f"{eyes}<path d='M79 82 Q86 78 93 82M107 82 Q114 78 121 82' stroke='{hc}' stroke-width='2.6' fill='none' stroke-linecap='round'/>"
            f"<path d='M100 97 Q96 104 100 105' stroke='{sd}' stroke-width='2.2' fill='none' stroke-linecap='round'/>{mouth}"
            f"<path d='{_AV_FRONT[style]}' fill='{hc}'/>{_av_accessory(av['accessory'])}</svg>")


def valid_avatar(av: object) -> bool:
    return isinstance(av, dict) and all(isinstance(av.get(k), int) and not isinstance(av.get(k), bool) and 0 <= av[k] < n for k, n in AV_LIMITS.items())


def av_default(i: int = 0) -> dict:
    """A ready-made avatar for character i (so users can skip customising)."""
    c = AV_CHARS[i]
    return {"char": i, "hair": c["hair"], "hair_color": c["hair_color"], "outfit": c["outfit"], "accessory": c["acc"]}


def _av_user() -> str:
    return str(ss.profile.get("name", "")).strip().lower()


def load_avatar_once() -> None:
    """Bring back the avatar this person saved on an earlier visit (stored in a small JSON file next to the app)."""
    if ss.av_loaded or not ss.onboarded:
        return
    ss.av_loaded = True
    if ss.avatar is None:
        try:
            av = json.loads(AV_FILE.read_text(encoding="utf-8")).get(_av_user())
        except (OSError, ValueError, AttributeError):
            av = None
        if valid_avatar(av):
            ss.avatar = av


def save_avatar_file(av: dict) -> bool:
    try:
        data = json.loads(AV_FILE.read_text(encoding="utf-8")) if AV_FILE.exists() else {}
        data[_av_user()] = av
        AV_FILE.write_text(json.dumps(data), encoding="utf-8")
        return True
    except (OSError, ValueError):
        return False


def open_avatar(edit: bool) -> None:
    """Callback for the profile buttons: new users start at step 1, people editing start at step 2 with their saved look."""
    editing = bool(edit and ss.avatar)
    ss.av_draft = dict(ss.avatar) if editing else av_default(0)
    ss.av_step = 2 if editing else 1
    ss.av_open = True


def av_pick_char(i: int) -> None:
    ss.av_draft = av_default(i)


def av_set(field: str, value: int) -> None:
    ss.av_draft[field] = value


def av_go(step: int) -> None:
    ss.av_step = step


def av_start_over() -> None:
    ss.av_draft, ss.av_step = av_default(0), 1


def av_save() -> None:
    ss.avatar = {k: int(ss.av_draft[k]) for k in AV_LIMITS}
    ok = save_avatar_file(ss.avatar)
    ss.av_msg = "Avatar saved. It now shows in your profile and header." + ("" if ok else " (Kept for this visit only, as the app can't write files here.)")


def _av_option(key: str, svg: str, label: str, selected: bool, field: str, value: int) -> None:
    """One visual selection card: a picture, its name and a pick button."""
    st.markdown(f"<div class='av-tile{' sel' if selected else ''}'>{svg}<div class='av-lbl'>{html.escape(label)}</div></div>", unsafe_allow_html=True)
    st.button("✓ Picked" if selected else "Pick", key=key, type="primary" if selected else "secondary", on_click=av_set, args=(field, value))


_AV_CROP = "34 22 132 132"
_dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog")


@_dialog("Your avatar", width="large")
def avatar_dialog() -> None:
    """Three simple steps: 1 choose a character, 2 personalise, 3 preview and save. The preview updates on every click."""
    d, step = ss.av_draft, ss.av_step
    bar = "".join(f"<div class='av-s {'on' if i == step else 'done' if i < step else ''}'><b>{'✓' if i < step else i}</b><span>{t}</span></div>"
                  for i, t in enumerate(["Character", "Your look", "Save"], 1))
    st.markdown(f"<div class='av-steps'>{bar}</div>", unsafe_allow_html=True)

    if step < 3:
        left, right = st.columns([1, 2.2], gap="large")
        with left:
            st.markdown(f"<div class='av-prev'>{draw_avatar_svg(d, 170)}<div class='av-lbl'>Your avatar</div></div>", unsafe_allow_html=True)
        with right:
            if step == 1:
                st.markdown("<div class='av-h'>Choose your character</div><div class='av-sub'>Tap the one that feels like you. You can fine-tune it next, or skip ahead.</div>", unsafe_allow_html=True)
                for row in (range(0, 4), range(4, 8)):
                    for col, i in zip(st.columns(4), row):
                        with col:
                            sel = d["char"] == i
                            st.markdown(f"<div class='av-tile{' sel' if sel else ''}'>{draw_avatar_svg(av_default(i), 84)}<div class='av-lbl'>{AV_CHARS[i]['name']}</div></div>", unsafe_allow_html=True)
                            st.button("✓ Picked" if sel else "Pick", key=f"av_c_{i}", type="primary" if sel else "secondary", on_click=av_pick_char, args=(i,))
            else:
                st.markdown("<div class='av-h'>Hairstyle</div>", unsafe_allow_html=True)
                for row in (range(0, 4), range(4, 8)):
                    for col, i in zip(st.columns(4), row):
                        with col:
                            _av_option(f"av_h_{i}", draw_avatar_svg({**d, "hair": i}, 64, _AV_CROP, "14px"), AV_HAIR[i], d["hair"] == i, "hair", i)
                st.markdown("<div class='av-h'>Hair colour</div>", unsafe_allow_html=True)
                for col, (i, (nm, hexv)) in zip(st.columns(6), enumerate(AV_HAIR_COLORS)):
                    with col:
                        sel = d["hair_color"] == i
                        st.markdown(f"<div class='av-tile{' sel' if sel else ''}'><div class='av-sw' style='background:{hexv}'></div><div class='av-lbl'>{nm}</div></div>", unsafe_allow_html=True)
                        st.button("✓" if sel else "Pick", key=f"av_hc_{i}", type="primary" if sel else "secondary", on_click=av_set, args=("hair_color", i))
                st.markdown("<div class='av-h'>Outfit</div>", unsafe_allow_html=True)
                for row in (range(0, 4), range(4, 8)):
                    for col, i in zip(st.columns(4), row):
                        with col:
                            _av_option(f"av_o_{i}", draw_avatar_svg({**d, "outfit": i}, 64, "20 70 160 130", "14px"), AV_OUTFITS[i], d["outfit"] == i, "outfit", i)
                st.markdown("<div class='av-h'>Accessory</div>", unsafe_allow_html=True)
                for col, i in zip(st.columns(6), range(6)):
                    with col:
                        _av_option(f"av_a_{i}", draw_avatar_svg({**d, "accessory": i}, 56, _AV_CROP, "14px"), AV_ACCS[i], d["accessory"] == i, "accessory", i)
    else:
        _, mid, _ = st.columns([1, 1.4, 1])
        with mid:
            st.markdown(f"<div class='av-prev'>{draw_avatar_svg(d, 230)}<div class='av-h' style='margin-top:10px'>Looking good, {html.escape(ss.profile['name'])}!</div>"
                        "<div class='av-sub'>Happy with it? Save it to your profile, or start again.</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='av-nav'></div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("Save My Avatar", key="av_save", type="primary"):
            av_save()
            st.rerun()
        b2.button("Start Again", key="av_again", on_click=av_start_over)

    st.markdown("<div class='av-nav'></div>", unsafe_allow_html=True)
    nav = st.columns(3)
    if step == 1:
        nav[1].button("Skip, use this one", key="av_skip", on_click=av_go, args=(3,))
        nav[2].button("Continue →", key="av_next1", type="primary", on_click=av_go, args=(2,))
    elif step == 2:
        nav[0].button("← Back", key="av_back2", on_click=av_go, args=(1,))
        nav[2].button("Continue →", key="av_next2", type="primary", on_click=av_go, args=(3,))
    else:
        nav[0].button("← Back", key="av_back3", on_click=av_go, args=(2,))


# =============================================================================
# 7. TAB 1: GROCERY LIST
# =============================================================================
def delete_purchase(pid: int) -> None:
    """Remove a purchase and unlink any grocery item that created it."""
    ss.purchases = [p for p in ss.purchases if p.get("id") != pid]
    for g in ss.groceries:
        if g.get("log_id") == pid:
            g["log_id"] = None
    if ss.last_log and ss.last_log["entry"].get("id") == pid:
        ss.last_log = None


def toggle_item(iid: int) -> None:
    """Tick/untick an item. With auto-log on, bought items flow into the CO2 tracker (and out again if unticked)."""
    it = find_item(iid)
    if not it:
        return
    it["done"] = bool(ss[f"chk_{iid}"])
    if it["done"] and ss.autolog and not it.get("log_id") and it["price"] > 0:
        e = log_purchase(it["type"], it["brand"], it["price"] * it["qty"], now_local().date(), False)
        it["log_id"] = e["id"]
        st.toast(f"Logged {e['co2']:.2f} kg CO₂ to your tracker")
    elif not it["done"] and it.get("log_id"):
        delete_purchase(it["log_id"])
    update_badges()


def delete_item(iid: int) -> None:
    ss.groceries = [g for g in ss.groceries if g["id"] != iid]


def save_edit(iid: int) -> None:
    it, name = find_item(iid), ss[f"en_{iid}"].strip()
    if it and name and ss[f"eq_{iid}"] > 0 and ss[f"ep_{iid}"] >= 0:
        it.update(name=name, qty=int(ss[f"eq_{iid}"]), price=float(ss[f"ep_{iid}"]))
    else:
        st.toast("Keep a name, a quantity of 1+ and a price of 0 or more.")


def snooze_reminder() -> None:
    ss.snooze_until = now_local() + timedelta(minutes=30)


def dismiss_reminder() -> None:
    ss.reminder_dismissed = datetime.combine(ss.trip_date, ss.trip_time).isoformat()


@st.fragment(run_every="30s")
def reminder_banner() -> None:
    """Re-checks every 30 s; shows a banner (plus one toast per snooze period) for unbought items."""
    pending = check_reminders()
    if not pending:
        return
    key = f"{ss.trip_date}{ss.trip_time}{ss.snooze_until}"
    if ss.toast_key != key:  # show the toast only once per snooze period
        ss.toast_key = key
        st.toast(f"{len(pending)} item(s) still to buy!")
    names = ", ".join(html.escape(g["name"]) for g in pending[:8]) + ("…" if len(pending) > 8 else "")
    st.markdown(f"<div class='reminder'><b>Shopping time is near!</b><br>Still on your list: {names}</div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3])
    c1.button("Snooze 30 min", on_click=snooze_reminder)
    c2.button("Got it", on_click=dismiss_reminder)


def render_item_row(g: dict) -> None:
    c1, c2, c3, c4 = st.columns([5, 3, 1.3, 0.8])
    label = f"~~{g['name']}~~" if g["done"] else f"**{g['name']}**"
    c1.checkbox(f"{label} ×{g['qty']}", value=g["done"], key=f"chk_{g['id']}", on_change=toggle_item, args=(g["id"],))
    c1.caption(f"{g['type']}" + (f" · {g['brand']}" if g["brand"] else ""))
    c2.markdown(f"<span class='chip'>{item_co2(g):.2f} kg</span><span class='chip'>${g['price'] * g['qty']:.2f}</span>",
                unsafe_allow_html=True)
    with c3.popover("Edit"):
        st.text_input("Name", value=g["name"], key=f"en_{g['id']}")
        st.number_input("Quantity", min_value=1, value=g["qty"], step=1, key=f"eq_{g['id']}")
        st.number_input("Price each ($)", min_value=0.0, value=g["price"], step=0.5, key=f"ep_{g['id']}")
        st.button("Save", key=f"sv_{g['id']}", on_click=save_edit, args=(g["id"],))
    c4.button("×", key=f"del_{g['id']}", on_click=delete_item, args=(g["id"],), help="Delete")


def render_grocery_tab() -> None:
    """Grocery tab: add items, tick them off. Trip settings, advice and swaps live in expanders."""
    p = ss.profile
    page_head("Grocery List", "Tick items off as you buy them. Smart advice keeps each trip greener.")
    guide("Grocery List", "Your shopping list, like a to-do list that also shows how green each item is.",
          [("Add an item", "Type the item name, pick its product type, then press Add to list."),
           ("Read the CO₂ and tips", "Each row shows its CO₂ estimate. Open Smart advice for buying tips and greener swaps."),
           ("Tick it when bought", "Bought items move to Done, and the progress bar fills up."),
           ("Set your trip", "Open Trip settings to choose weekly or monthly, plus the date and time for your reminder.")],
          "Tip: use Meal Prep to fill this list automatically with the ingredients you need." if p.get("meal_prep") else
          "Tip: no time to plan? Try the Grab-and-go greener swaps at the bottom of this tab.")
    _, why = suggest_shop_time(p)
    st.caption(f"{ss.mode} trip · {datetime.combine(ss.trip_date, ss.trip_time):%a %d %b, %H:%M}")
    with st.expander("Trip settings (weekly or monthly, date and time)"):
        c1, c2, c3 = st.columns(3)
        c1.radio("Planning for", ["Weekly", "Monthly"], horizontal=True, key="mode")
        c2.date_input("Shopping date", key="trip_date")
        c3.time_input("Shopping time", key="trip_time", step=900)
        st.caption(f"{why}")
        st.caption(PERSONA_TIPS[profile_mode(p)])

    with st.container(border=True):
        section("Add an item", "Type what you need and pick its product type. Its CO₂ estimate appears in the list.", 1)
        with st.form("add_item", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 3, 2])
            name = c1.text_input("Item name", placeholder="e.g. Bananas")
            ptype = c2.selectbox("Product type", list(PRODUCTS), index=list(PRODUCTS).index("Vegetables"))
            brand = c3.text_input("Brand (optional)")
            c4, c5, c6 = st.columns([2, 2, 2])
            qty = c4.number_input("Quantity", min_value=1, value=1, step=1)
            price = c5.number_input("Price each ($)", min_value=0.0, value=1.0, step=0.5, format="%.2f")
            c6.markdown("<br>", unsafe_allow_html=True)
            submitted = c6.form_submit_button("Add to list", type="primary")
        if submitted:
            ok, msg = add_grocery(name, ptype, brand, qty, price)
            (st.success if ok else st.warning)(msg)

    items = ss.groceries
    todo, done = [g for g in items if not g["done"]], [g for g in items if g["done"]]
    with st.container(border=True):
        section("Your shopping list", "Tick items as you buy them. Bought items move to the Done section.", 2)
        if not items:
            st.info("Your list is empty. Add your first item above, nice and easy!")
        else:
            st.progress(len(done) / len(items), text=f"{len(done)} of {len(items)} items bought")
            st.markdown(f"<span class='chip'>${sum(g['price'] * g['qty'] for g in items):.2f} planned</span>"
                        f"<span class='chip'>{sum(item_co2(g) for g in items):.1f} kg CO₂</span>", unsafe_allow_html=True)
        for cat in CAT_ICONS:  # group the to-do list by category
            group = [g for g in todo if PRODUCTS[g["type"]][1] == cat]
            if group:
                st.markdown(f"<div class='kicker'>{cat}</div>", unsafe_allow_html=True)
                for g in group:
                    render_item_row(g)
        if items and not todo:
            st.success("Everything is bought. Nicely planned.")
        if done:
            with st.expander(f"Done ({len(done)})"):
                for g in done:
                    render_item_row(g)

    if todo:
        advice = [m for stt, m in (suggest_quantity(g) for g in todo) if stt != "ok"]
        hints = []
        for g in todo:
            alt = get_alternatives(g["type"], g["price"] * g["qty"])
            if alt and alt[0]["saved"] >= 0.5:
                hints.append(f"**{g['name']}**: try *{alt[0]['option']}* to save ~{alt[0]['saved']:.1f} kg CO₂")
        label = f"Smart advice ({len(advice)} buying tip(s), {len(hints)} greener swap(s))"
        with st.expander(label, expanded=bool(advice)):
            for m in advice:
                st.markdown(f"- {m}")
            for h in hints:
                st.markdown(f"- {h}")
            if not advice and not hints:
                st.success("Your quantities look nicely balanced for your household.")

    if not p.get("meal_prep"):
        with st.expander("Grab-and-go greener swaps"):
            for i, (label, new, cost, old) in enumerate(GRAB_AND_GO):
                saved = cost * (PRODUCTS[old][0] - PRODUCTS[new][0])
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{label}**  \n<span class='chip'>saves about {saved:.1f} kg CO₂</span>", unsafe_allow_html=True)
                if c2.button("Add", key=f"swap_{i}"):
                    st.toast(add_grocery(label.split(" instead")[0], new, "", 1, cost)[1])
                    st.rerun()


# =============================================================================
# 8. TAB 2: MEAL PREP
# =============================================================================
def render_meal_tab() -> None:
    """Meal prep: build a plan in one click; filters, pantry and full recipe list are tucked away."""
    recipes = get_recipes()
    page_head("Meal Prep", "Plan your week in a few clicks, then send every ingredient to your grocery list.")
    guide("Meal Prep", "Plan a week of meals in a few clicks and send everything you need to your grocery list.",
          [("Choose how many meals", "Use the slider to pick 5 to 7 meals. Open Filters if you want a diet, a time limit or a budget."),
           ("Press Build my plan", "I pick your lowest-CO₂ recipes and show total time, cost and footprint."),
           ("Skip what you already have", "Open the pantry box and select ingredients at home so they are not added twice."),
           ("Send it to your list", "Press Add all ingredients to my grocery list. You can also add or remove single recipes below.")],
          "Tip: every recipe makes 2 servings, so one prep session covers a few dinners.")
    with st.container(border=True):
        section("Plan your week", "Choose how many meals, press Build my plan, then send the ingredients to your grocery list.", 1)
        days = st.slider("Meals to prep this week", 5, 7, key="mp_days")
        with st.expander("Filters (diet, prep time, budget)"):
            c1, c2, c3 = st.columns(3)
            diet = c1.selectbox("Diet", ["Any", "Vegetarian", "Vegan", "High-protein", "Budget", "Quick"])
            ss.max_prep = c2.slider("Max prep time (min)", 10, 60, min(ss.max_prep, 60), step=5)
            budget = c3.slider("Max cost per serving ($)", 1.0, 5.0, step=0.5, key="mp_budget")
        if profile_mode(ss.profile) == "busy":
            st.caption("Your schedule is full, so I've started you on quicker recipes.")
        tag = diet.lower()
        shown = [r for r in recipes if r["mins"] <= ss.max_prep and r["cost"] <= budget
                 and (diet == "Any" or tag in r["tags"])]
        b1, b2, _ = st.columns([1, 1, 2])
        if b1.button("Build my plan", type="primary"):
            ss.meal_plan = build_meal_plan(shown, days)
            if not ss.meal_plan:
                st.warning("No recipes match those filters. Try relaxing them a little.")
        if b2.button("Clear plan"):
            ss.meal_plan = []

    plan = [r for r in recipes if r["name"] in ss.meal_plan]
    if plan:
        with st.container(border=True):
            section("This week's plan", "Your lowest-CO₂ meals, with total time, cost and footprint.", 2)
            st.markdown(" ".join(f"<span class='chip'>{html.escape(r['name'])}</span>" for r in plan), unsafe_allow_html=True)
            co2 = sum(r["co2"] for r in plan) * SERVINGS
            base = BEEF_BASELINE * SERVINGS * len(plan)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total prep time", f"{sum(r['mins'] for r in plan)} min")
            m2.metric("Estimated cost", f"${sum(r['cost'] for r in plan) * SERVINGS:.2f}")
            m3.metric("Estimated CO₂", f"{co2:.1f} kg")
            if base > co2:
                st.success(f"That's about {base - co2:.1f} kg CO₂ less than a beef-based week.")
            with st.expander("Already have some of these? (they'll be skipped)"):
                have = st.multiselect("Pantry items", sorted({n for r in plan for n, _, _ in r["ingredients"]}))
            if st.button("Add all ingredients to my grocery list", type="primary"):
                n = import_plan_to_list(set(have))
                st.toast(f"Added {n} ingredients (duplicates merged).")
                st.rerun()

    section("Recipe library", "Browse every recipe and add or remove meals from your plan.", 3)
    if not shown:
        st.info("No recipes match your filters yet. Try a longer prep time or a bigger budget.")
    show_all = st.toggle("Show all recipes", key="mp_all")
    cols = st.columns(2)
    for i, r in enumerate(shown if show_all else shown[:6]):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{r['name']}**  \n<span class='muted'>{r['meal']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='chip'>{r['mins']} min</span><span class='chip'>{r['co2']} kg/serving</span>"
                        f"<span class='chip'>${r['cost']:.2f}</span>", unsafe_allow_html=True)
            with st.expander("Ingredients and greener swap"):
                st.caption(", ".join(r["tags"]))
                st.markdown("\n".join(f"- {q} × {n}" for n, q, _ in r["ingredients"]))
                st.info(f"{r['swap']}")
            inplan = r["name"] in ss.meal_plan
            if st.button("Remove from plan" if inplan else "Add to plan", key=f"rp_{i}"):
                ss.meal_plan = [x for x in ss.meal_plan if x != r["name"]] if inplan else ss.meal_plan + [r["name"]]
                st.rerun()


# =============================================================================
# 9. TAB 3: CO2 IMPACT DASHBOARD
# =============================================================================
def render_result_card() -> None:
    """Show the most recent logged purchase with a tip, alternatives and a turtle drawing."""
    log = ss.last_log
    if not log:
        return
    e = log["entry"]
    mult = PRODUCTS[e["type"]][0]
    with st.container(border=True):
        c1, c2 = st.columns([2, 1])
        c1.markdown(f"<div class='big-num'>{e['co2']:.2f} kg CO₂e</div>{impact_label(mult)} · {e['type']} · {html.escape(e['brand'])}",
                    unsafe_allow_html=True)
        c1.info(f"{log['tip']}")
        for b in log["new"]:
            c1.success(f"New badge: {BADGES[b][0]} {b}!")
        if log["alts"] and mult >= 1.5:
            for a in log["alts"]:
                c1.markdown(f"Try {a['option']} and save about **{a['saved']:.2f} kg CO₂**.")
        cmp_alt = compare_alternative(e["type"], e["price"])
        if cmp_alt:
            pct = f" ({cmp_alt['pct']:.0f}% lower)" if cmp_alt["pct"] is not None else ""
            c1.markdown(f"**Compare:** {e['type']} ≈ {cmp_alt['original']:.2f} kg CO₂e vs. {cmp_alt['option']} ≈ "
                        f"{cmp_alt['alternative']:.2f} kg at the same price: about {cmp_alt['saved']:.2f} kg less{pct}. "
                        f"(Estimate based on price × multiplier.)")
        if e.get("status") == "planned":
            c1.info("Saved as planned. It is not counted in your totals until its date arrives.")
        c1.markdown(f"**Greener ideas:** {BRAND_IDEAS[e['type']]}")
        if e["ethical"]:
            c1.caption("Counted as a local / ethical brand.")
        fn, cap = ((draw_badge_svg, "Badge earned!") if log["new"] else (draw_leaf_svg, "Green choice!") if mult <= LOW_MULT
                   else (draw_footprint_svg, "Kind footprint!") if e["ethical"] else (None, ""))
        with c2:
            if fn:
                show_drawing(fn(), cap)
                with st.expander("See the turtle code"):
                    st.code(inspect.getsource(fn), language="python")


def submit_purchase() -> None:
    """Callback for the 'Log purchase' button: validate, log, then reset the brand field."""
    price, d = ss.lp_price, ss.lp_date
    ok, problem = validate_purchase(ss.lp_type, price, d, ss.lp_brand)
    if not ok:
        ss.log_msg = ("warning", problem)
        return
    ss.log_msg = (("info", "That date is in the future, so it is saved as PLANNED. It will not count towards your "
                           "totals, badges or challenges until the day arrives.")
                  if purchase_status(d) == "planned" else ("success", "Purchase logged as completed."))
    eth = bool(ss.lp_eth) or (ss.lp_brand or "").strip().lower() in ETHICAL_BRANDS
    log_purchase(ss.lp_type, ss.lp_brand, price, d, eth)
    ss.lp_brand, ss.lp_eth = "", False


def render_challenges(df: pd.DataFrame) -> None:
    """Weekly challenges with progress bars plus the green streak (shown inside an expander)."""
    st.metric("Green streak", f"{green_streak(df)} day(s)")
    for c in challenge_progress(df):
        have = min(c["have"], c["goal"])
        st.progress(have / c["goal"], text=f"{'Done: ' if have >= c['goal'] else ''}{c['title']} ({have}/{c['goal']})")
    st.caption("A green streak counts days with a low-impact purchase and no high-impact one.")


def render_impact_tab() -> None:
    """CO2 tab: log a purchase and see the result first; the dashboard details sit in expanders."""
    page_head("CO₂ Tracking", "See how your shopping affects the planet, and which swaps help most.")
    guide("CO₂ Tracking", "Find out how much CO₂ your shopping creates, and how to bring it down.",
          [("Log a purchase", "Pick the product type, enter the price and date, then press Log purchase."),
           ("See your result", "You get the CO₂ estimate straight away, with a tip and a greener idea."),
           ("Read the dashboard", "Choose a month to see your totals and three charts: by product, over time, and spend vs CO₂."),
           ("Improve", "Set a monthly target, try greener swaps, take weekly challenges and earn badges.")],
          "Tip: no purchases yet? Press Load sample data below to explore the dashboard first.")
    with st.container(border=True):
        section("Log a purchase", "Choose a product type and price to see its footprint straight away.", 1)
        c1, c2, c3 = st.columns(3)
        ptype = c1.selectbox("Product type", list(PRODUCTS), key="lp_type")
        c2.text_input("Brand", key="lp_brand", placeholder="e.g. Oatly")
        price = c3.number_input("Price ($)", min_value=0.0, step=0.5, format="%.2f", key="lp_price")
        c4, c5, c6 = st.columns(3)
        c4.date_input("Purchase date", key="lp_date")
        c5.checkbox("Local / ethical brand", key="lp_eth")
        c6.markdown("<br>", unsafe_allow_html=True)
        c6.button("Log purchase", type="primary", on_click=submit_purchase)
        st.markdown(f"Live estimate: **{calculate_impact(ptype, price):.2f} kg CO₂e** · {impact_label(PRODUCTS[ptype][0])}")
        alt = get_alternatives(ptype, price)
        if alt and alt[0]["saved"] >= 0.5:
            st.caption(f"Greener idea: {alt[0]['option']} could save about {alt[0]['saved']:.2f} kg CO₂.")
        if ss.log_msg:
            getattr(st, ss.log_msg[0])(ss.log_msg[1])
    render_result_card()

    df, planned_df = purchases_df(), purchases_df(only_planned=True)
    if not planned_df.empty:
        with st.expander(f"Planned purchases ({len(planned_df)}) - not counted in your totals yet"):
            st.caption("These have a future date. They become completed automatically on their date, and only then "
                       "count towards totals, charts, badges, streaks and challenges.")
            st.metric("Projected impact if bought (estimate)", f"{planned_df['co2'].sum():.1f} kg CO₂e")
            pt = planned_df[["date", "type", "brand", "price", "co2", "status"]].copy()
            pt["date"] = pt["date"].dt.date
            st.dataframe(pt, hide_index=True)
    if df.empty:
        with st.container(border=True):
            st.info("No completed purchases logged yet. Log one above, or try the sample data to explore the dashboard.")
            if st.button("Load sample data"):
                start = date.today().replace(day=1)
                for i, (t, b, pr, eth) in enumerate(SAMPLE):
                    log_purchase(t, b, pr, start + timedelta(days=min(i, date.today().day - 1)), eth)
                ss.last_log = None
                st.rerun()
    else:
        section("Monthly dashboard", "Pick a month to see your spending, CO₂ total and charts.", 2)
        months = sorted(df["month"].unique(), reverse=True)
        month = st.selectbox("Month", months)
        m = df[df["month"] == month]
        tot = float(m["co2"].sum())
        idx = months.index(month)
        prev = months[idx + 1] if idx + 1 < len(months) else None
        prev_tot = float(df[df["month"] == prev]["co2"].sum()) if prev else 0.0
        delta = f"{(tot - prev_tot) / prev_tot * 100:+.0f}% vs {prev}" if prev_tot > 0 else None
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total spend", f"${m['price'].sum():.2f}")
        c2.metric("Total CO₂", f"{tot:.1f} kg", delta=delta, delta_color="inverse")
        c3.metric("Purchases", len(m))
        c4.metric("Avg CO₂ / purchase", f"{m['co2'].mean():.2f} kg")
        eq = co2_equivalents(tot)

        with st.expander("Charts", expanded=True):
            g1, g2 = st.columns(2)
            g1.markdown("<div class='mini-title'>CO₂ by product type (kg)</div>", unsafe_allow_html=True)
            with g1:
                co2_bar_chart(m)
            g2.markdown("<div class='mini-title'>CO₂ over time (kg per day)</div>", unsafe_allow_html=True)
            with g2:
                co2_line_chart(m)
            st.markdown("<div class='mini-title'>Spend vs CO₂ (each dot is a purchase)</div>", unsafe_allow_html=True)
            co2_scatter_chart(m)
            st.markdown("<div class='mini-title'>Share of CO₂ by category</div>", unsafe_allow_html=True)
            share = m.groupby("category")["co2"].sum().sort_values(ascending=False)
            st.markdown("".join(f"<span class='chip'>{c}: {v / max(float(share.sum()), 1e-9) * 100:.0f}%</span>" for c, v in share.items()), unsafe_allow_html=True)
        with st.expander("Compared with last month (completed purchases only)", expanded=True):
            cmp_ = monthly_comparison(df, month, prev)
            if cmp_["direction"] == "unknown":
                st.info("There is no earlier month with completed purchases to compare with yet.")
            else:
                a, b, c = st.columns(3)
                words = {"up": "higher", "down": "lower", "same": "unchanged"}
                a.metric("Estimated CO₂", f"{cmp_['current']['co2']:.1f} kg",
                         delta=None if cmp_["co2_pct"] is None else f"{cmp_['co2_pct']:+.0f}%", delta_color="inverse")
                b.metric("Spending", f"${cmp_['current']['spend']:.2f}",
                         delta=None if cmp_["spend_pct"] is None else f"{cmp_['spend_pct']:+.0f}%", delta_color="off")
                c.metric("Purchases", cmp_["current"]["n"], delta=f"{cmp_['n_diff']:+d}", delta_color="off")
                st.write(f"Estimated impact is **{words[cmp_['direction']]}** than in {prev}.")
                if cmp_["most_improved"]:
                    st.write(f"Most improved category: **{cmp_['most_improved']}**.")
            if cmp_["top_category"]:
                st.write(f"Highest-impact category this month: **{cmp_['top_category']}**.")
        with st.expander("Monthly target and environmental insights"):
            st.slider("Target (kg CO₂ per month)", 10, 200, step=5, key="target")
            gp = goal_progress(tot, ss.target)
            st.progress(min(gp["ratio"], 1.0), text=f"{tot:.1f} of {ss.target} kg used"
                        + (f" · {gp['remaining']:.1f} kg remaining" if not gp["over"] else " · target passed"))
            (st.warning if gp["over"] else st.success)(gp["message"])
            for line in build_insights(df):
                st.markdown(f"- {line}")
            st.markdown(f"<span class='chip'>≈ {eq['km']} km by car</span><span class='chip'>≈ {eq['charges']} phone charges</span>"
                        f"<span class='chip'>a tree needs ~{eq['tree_days']} days to absorb this</span>", unsafe_allow_html=True)
        with st.expander("Greener alternatives for this month"):
            high = m[m["type"].map(lambda t: PRODUCTS[t][0]) >= 1.5].sort_values("co2", ascending=False).head(5)
            shown = False
            for _, r in high.iterrows():
                for a in get_alternatives(r["type"], r["price"]):
                    shown = True
                    st.markdown(f"- **{r['type']}** ({r['brand']}, ${r['price']:.2f}): try *{a['option']}* to save ~**{a['saved']:.2f} kg CO₂**")
            if not shown:
                st.success("No high-impact purchases this month. Nothing to swap!")
        with st.expander("All purchases, downloads and delete"):
            all_df = purchases_df(include_planned=True)
            table = all_df[["date", "type", "brand", "price", "co2", "category", "status"]].copy()
            table["date"] = table["date"].dt.date
            st.dataframe(table.sort_values("date", ascending=False), hide_index=True)
            d1, d2 = st.columns(2)
            d1.download_button("Download CSV", table.to_csv(index=False).encode("utf-8"), "shopimpact_purchases.csv", "text/csv")
            d2.download_button("Download my impact card", build_impact_card(ss.profile["name"], month, m, eq),
                               f"shopimpact_{month}.html", "text/html")
            opts = {int(r.id): f"{r.date:%Y-%m-%d} · {r.type} · {r.brand} · ${r.price:.2f}"
                    for r in all_df.sort_values("date", ascending=False).itertuples()}
            pick = st.selectbox("Remove a purchase", list(opts), format_func=opts.get)
            st.button("Delete it", on_click=delete_purchase, args=(pick,))

    section("Learn and improve", "Set a target, find greener swaps, take on challenges and review every purchase.", 3)
    with st.expander("Weekly challenges and green streak"):
        render_challenges(df)
    with st.expander("Greener ideas for every product type"):
        st.dataframe(pd.DataFrame(list(BRAND_IDEAS.items()), columns=["Product type", "Greener options"]), hide_index=True)
    with st.expander("How is CO₂ estimated?"):
        st.caption("CO₂ = price × multiplier for the product type. These multipliers are simplified estimates for learning "
                   "purposes, not scientific measurements. Animal products and long-lived goods score higher; plants, "
                   "reusable and second-hand items score lower. Values are inspired by public research (for example Poore & Nemecek, 2018, "
                   "and Our World in Data) but simplified to price × multiplier.")
        st.dataframe(multiplier_table(), hide_index=True)


# =============================================================================
# 10. MAIN
# =============================================================================
def celebrate() -> None:
    """Show balloons and a toast for any badges queued since the last run."""
    if ss.celebrate:
        for b in ss.celebrate:
            st.toast(f"{BADGES[b][0]} Badge unlocked: {b}!")
        st.balloons()
        ss.celebrate = []


LOGO_SVG = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M5 19C5 10 10 5 20 5c0 9-5 14-15 14z'/><path d='M5 19L14 10'/></svg>"


def render_header(p: dict, mood: str, says: str) -> None:
    """Slim top bar (logo, welcome, profile chip) with Carty's tip underneath."""
    name = html.escape(p["name"])
    av = ss.get("avatar")
    chip = f"<div class='avatar-svg'>{draw_avatar_svg(av, 34)}</div>" if av else f"<div class='avatar'>{name[:1].upper() or '?'}</div>"
    st.markdown(f"<div class='topbar'><div class='brand'><div class='logo'>{LOGO_SVG}</div><div class='brand-name'>ShopImpact</div>"
                f"<div class='brand-div'></div><div class='brand-sub'>Conscious Shopping Dashboard</div></div>"
                f"<div class='user'><div class='welcome'>Welcome back, {name}</div>"
                f"<div class='chip-user'>{chip}<div class='uname'>{name}</div></div></div></div>"
                f"<div class='carty'><div class='mascot'>{draw_mascot_svg(mood, 64)}</div>"
                f"<div class='bubble'><b>Carty:</b> {html.escape(says)}</div></div>", unsafe_allow_html=True)


def page_head(title: str, desc: str) -> None:
    """Large heading and one-line description at the top of each workspace."""
    st.markdown(f"<div class='page-head'><h1>{title}</h1><div class='page-desc'>{desc}</div></div>", unsafe_allow_html=True)


def render_steps(p: dict) -> None:
    """A short 'how it works' strip so a new user knows what each part of the app is for."""
    steps = [("Plan your list", "Add what you need in Grocery List and tick items as you buy them.")]
    if p.get("meal_prep"):
        steps.append(("Prep your meals", "Build a weekly plan in Meal Prep and send the ingredients to your list."))
    steps.append(("Track your impact", "Log purchases in CO₂ Tracking to see your footprint, badges and greener swaps."))
    cards = "".join(f"<div class='step'><div class='step-n'>{i}</div><div><div class='step-t'>{t}</div><div class='step-d'>{d}</div></div></div>"
                    for i, (t, d) in enumerate(steps, 1))
    st.markdown(f"<div class='steps'>{cards}</div>", unsafe_allow_html=True)


NAV = {"grocery": "🛒 Grocery List", "meal": "🍱 Meal Prep", "co2": "🌍 CO₂ Tracking"}


def set_nav(key: str) -> None:
    """Callback for the navigation buttons and the quick-access buttons."""
    ss.nav = key


def render_nav(keys: list[str]) -> None:
    """Three equal, button-style navigation tabs. The active one is filled forest green."""
    st.markdown("<div class='nav-anchor'></div>", unsafe_allow_html=True)
    for col, k in zip(st.columns(len(keys)), keys):
        col.button(NAV[k], key=f"nav_{k}", type="primary" if ss.nav == k else "secondary", on_click=set_nav, args=(k,))


ICON_GLOBE = "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='9'/><path d='M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18'/></svg>"
ICON_BOWL = "<svg viewBox='0 0 24 24'><path d='M3 11h18a9 9 0 0 1-18 0z'/><path d='M8 7c0-1.5 1-1.5 1-3M13 7c0-1.5 1-1.5 1-3'/></svg>"
ICON_CART = "<svg viewBox='0 0 24 24'><path d='M3 4h2.5l2 10h10.5l2-7.5H6.5'/><circle cx='9' cy='19' r='1.4'/><circle cx='17' cy='19' r='1.4'/></svg>"


def side_card(icon: str, title: str, body: str) -> None:
    st.markdown(f"<div class='side-head'><span class='ico'>{icon}</span>{title}</div>{body}", unsafe_allow_html=True)


def render_side_panel(p: dict) -> None:
    """Three compact summary cards. Full features stay inside the matching navigation tab."""
    df, month = purchases_df(), now_local().strftime("%Y-%m")
    tot_all = float(df["co2"].sum()) if not df.empty else 0.0
    tot_m = float(df.loc[df["month"] == month, "co2"].sum()) if not df.empty else 0.0
    target = max(1, int(ss.target))
    ratio = tot_m / target
    level, cls = ("Low", "low") if ratio < 0.5 else ("Moderate", "mid") if ratio <= 1 else ("High", "high")
    arc = min(ratio, 1) * 238.76
    with st.container(border=True):
        side_card(ICON_GLOBE, "CO₂ Impact",
                  f"<div class='ring-row'><div class='ring'><svg viewBox='0 0 96 96' aria-hidden='true'>"
                  f"<circle class='trk' cx='48' cy='48' r='38' fill='none' stroke-width='10'/>"
                  f"<circle class='val' cx='48' cy='48' r='38' fill='none' stroke-width='10' stroke-linecap='round' "
                  f"stroke-dasharray='{arc:.1f} 238.8' transform='rotate(-90 48 48)'/></svg><b>{ratio * 100:.0f}%</b></div>"
                  f"<div><div class='side-big'>{tot_m:.1f}<small>kg</small></div>"
                  f"<div class='side-note'>of {target} kg monthly target</div>"
                  f"<div style='margin-top:6px'><span class='lvl {cls}'>{level} impact</span></div></div></div>"
                  f"<div class='side-note'>{tot_all:.1f} kg all time. Simplified learning estimates.</div>")
        st.button("Open CO₂ tracking", key="go_co2", on_click=set_nav, args=("co2",), disabled=ss.nav == "co2")
    if p.get("meal_prep"):
        plan = list(ss.meal_plan)
        recipes = {r["name"]: r for r in get_recipes()}
        nxt = recipes.get(plan[0]) if plan else None
        total_min = sum(recipes[n]["mins"] for n in plan if n in recipes)
        upcoming = (f"<div class='kicker'>Next meal</div><div class='side-meal'>{html.escape(nxt['name'])}</div>"
                    f"<div class='side-note'>{nxt['mins']} min prep · {nxt['co2']} kg CO₂ per serving</div>" if nxt
                    else "<div class='kicker'>Next meal</div><div class='side-note'>No plan yet. Build one in the meal planner.</div>")
        with st.container(border=True):
            side_card(ICON_BOWL, "Meal Prep",
                      f"{upcoming}<div class='side-two' style='margin-top:10px'><div><b>{len(plan)}</b><span>meals planned</span></div>"
                      f"<div><b>{total_min // 60} h {total_min % 60} min</b><span>total prep</span></div></div>")
            st.button("Open meal planner", key="go_meal", on_click=set_nav, args=("meal",), disabled=ss.nav == "meal")
    G = ss.groceries
    done = sum(1 for g in G if g["done"])
    frac = done / len(G) if G else 0
    with st.container(border=True):
        side_card(ICON_CART, "Grocery List",
                  f"<div class='side-big'>{len(G) - done}<small>items remaining</small></div>"
                  f"<div class='pbar'><i style='width:{frac * 100:.0f}%'></i></div>"
                  f"<div class='side-note'>{done} of {len(G)} items bought</div>")
        st.button("Open grocery list", key="go_grocery", on_click=set_nav, args=("grocery",), disabled=ss.nav == "grocery")


def badge_progress() -> dict:
    """Display-only progress (fraction, label) towards each badge. The earning rules themselves are unchanged."""
    df, G = purchases_df(), ss.groceries
    prog = {name: (0.0, "Not started") for name in BADGES}
    if not df.empty:
        mult = df["type"].map(lambda t: PRODUCTS[t][0])
        best = int(df.groupby("month").size().max())
        share = float((mult <= LOW_MULT).mean())
        plant = int(df["type"].isin(PLANT_BASED).sum())
        eth = int(df["ethical"].fillna(False).astype(bool).sum())
        zero = int((df["type"] == "Reusable & zero-waste items").sum())
        prog["Eco Saver of the Month"] = (min(best, 3) / 3, f"{min(best, 3)}/3 purchases in your best month")
        prog["Low Impact Shopper"] = (min(len(df) / 3, share / 0.6, 1.0), f"{len(df)} purchases, {share * 100:.0f}% low-impact (need 60%)")
        prog["Plant Powered"] = (min(plant, 3) / 3, f"{min(plant, 3)}/3 plant-based")
        prog["Second-Hand Hero"] = (float((df["type"] == "Second-hand clothes").any()), "0/1 second-hand purchase")
        prog["Local Legend"] = (min(eth, 2) / 2, f"{min(eth, 2)}/2 local or ethical")
        prog["Zero Waste Streak"] = (min(zero, 2) / 2, f"{min(zero, 2)}/2 reusable")
    done = sum(1 for g in G if g["done"])
    prog["Smart Planner"] = (min(done, 3) / 3 if G else 0.0, f"{done}/{max(len(G), 3)} items ticked off")
    prog["Meal Prep Master"] = (min(len(ss.meal_plan), 5) / 5, f"{min(len(ss.meal_plan), 5)}/5 recipes in plan")
    prog["Challenge Champion"] = (min(sum(c["have"] >= c["goal"] for c in challenge_progress(df)), 2) / 2,
                                  f"{min(sum(c['have'] >= c['goal'] for c in challenge_progress(df)), 2)}/2 challenges")
    return prog


BADGE_SVG = {
    "Eco Saver of the Month": "<path d='M12 21V11'/><path d='M12 11c0-4-3-6-7-6 0 4 2 7 7 6z'/><path d='M12 13c0-3 2-5 7-5 0 3-2 6-7 5z'/>",
    "Low Impact Shopper": "<path d='M5 19C5 10 10 5 20 5c0 9-5 14-15 14z'/><path d='M5 19L14 10'/>",
    "Plant Powered": "<path d='M12 21V9'/><path d='M12 9c0-3-2-5-6-5 0 3 2 6 6 5z'/><path d='M12 12c0-3 2-5 6-5 0 3-2 6-6 5z'/><path d='M8 21h8'/>",
    "Smart Planner": "<rect x='4' y='5' width='16' height='15' rx='3'/><path d='M4 10h16M9 3v4M15 3v4'/><path d='M9 15l2 2 4-4'/>",
    "Meal Prep Master": "<path d='M3 11h18a9 9 0 0 1-18 0z'/><path d='M8 7c0-1.5 1-1.5 1-3M13 7c0-1.5 1-1.5 1-3'/>",
    "Second-Hand Hero": "<path d='M8 4L3 7l2 4 3-1v10h8V10l3 1 2-4-5-3c-1 2-2 3-4 3S9 6 8 4z'/>",
    "Local Legend": "<path d='M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z'/><circle cx='12' cy='10' r='2.5'/>",
    "Zero Waste Streak": "<path d='M20 12a8 8 0 0 0-14-5M6 3v4h4M4 12a8 8 0 0 0 14 5M18 21v-4h-4'/>",
    "Challenge Champion": "<path d='M3 20l6-10 4 6 2-3 6 7z'/><circle cx='18' cy='6' r='2.5'/>",
}


def render_achievements() -> None:
    """Separate achievements panel: earned badges first, then locked ones with progress."""
    prog, recent = badge_progress(), set(ss.get("recent_badges", []))
    earned = [n for n in BADGES if n in ss.badges]
    locked = [n for n in BADGES if n not in ss.badges]

    def card(name: str, kind: str) -> str:
        _, how = BADGES[name]
        art = f"<svg viewBox='0 0 24 24' aria-hidden='true'>{BADGE_SVG[name]}</svg>"
        if kind == "earned":
            tag, extra = "<div class='ach-tag'>Earned</div>", ""
        else:
            frac, label = prog[name]
            tag = ""
            extra = f"<div class='pbar'><i style='width:{frac * 100:.0f}%'></i></div><div class='ach-prog'>{html.escape(label)}</div>"
        new = " new" if name in recent and kind == "earned" else ""
        return (f"<div class='ach {kind}{new}'><div class='ach-ico'>{art}</div><div class='ach-body'>{tag}"
                f"<div class='ach-name'>{html.escape(name)}</div><div class='ach-desc'>{html.escape(how)}</div>{extra}</div></div>")

    body = ""
    if earned:
        body += f"<div class='ach-count'>Earned ({len(earned)})</div><div class='ach-grid'>{''.join(card(n, 'earned') for n in earned)}</div>"
    else:
        body += "<div class='ach-desc' style='margin-top:10px'>No badges yet. Your first one is closer than you think.</div>"
    if locked:
        body += f"<div class='ach-count'>Locked ({len(locked)})</div><div class='ach-grid'>{''.join(card(n, 'locked') for n in locked)}</div>"
    st.markdown(f"<div class='ach-panel'><div class='ach-head'><div class='ach-title'>Achievements &amp; Eco Badges</div>"
                f"<div class='ach-meta'>{len(earned)} of {len(BADGES)} earned</div></div>{body}</div>", unsafe_allow_html=True)


def main() -> None:
    init_state()
    render_background()
    if not ss.onboarded:
        render_onboarding()
        return
    load_avatar_once()
    render_sidebar()
    if ss.av_open:
        ss.av_open = False
        avatar_dialog()
    if ss.av_msg:
        st.toast(ss.av_msg)
        ss.av_msg = None
    p = ss.profile
    mood, says = mascot_says()
    render_header(p, mood, says)
    with st.expander("How ShopImpact works", expanded=(not ss.groceries and purchases_df().empty)):
        render_steps(p)
    reminder_banner()
    keys = ["grocery"] + (["meal"] if p.get("meal_prep") else []) + ["co2"]
    if ss.nav not in keys:
        ss.nav = "grocery"
    main_col, side_col = st.columns([3.3, 1.2], gap="large")
    with main_col:
        render_nav(keys)
        {"grocery": render_grocery_tab, "meal": render_meal_tab, "co2": render_impact_tab}[ss.nav]()
    with side_col:
        render_side_panel(p)
    render_achievements()
    celebrate()


if __name__ == "__main__":
    main()
