# IDAI102-1000676--HeerJitendraPatel
ShopImpact is a Python and Streamlit app designed to help shoppers make more sustainable purchasing decisions. It estimates the CO₂ impact of purchases, tracks monthly shopping habits, and provides greener alternatives, insights, grocery planning, and eco badges to turn everyday shopping into conscious choices.
# 🌱 ShopImpact — Conscious Shopping Dashboard

### *Shop smarter. Understand your impact. Choose greener.*

ShopImpact is an interactive Python and Streamlit web application designed to help users make more conscious shopping decisions. It allows users to record purchases, estimate their associated CO₂ impact, monitor monthly spending and environmental impact, explore greener alternatives, plan meals, and earn achievements for sustainable choices.

The application combines **Python programming, data structures, calculations, Streamlit UI design, visual feedback, and sustainability-focused features** into one user-friendly dashboard.

---

## 👤 Student Information

| Detail | Information |
|---|---|
| **Name** | Heer Jitendra Patel |
| **School Name** | Udgam School For Children |
| **CRS** | Artificial Intelligence And Interpretation |
| **Registration Number** | 1000676 |
| **Subject** | Python Programming |
| **Project** | Summative Assesment Scenario 1 (ShopImpact) |

---

# 🌎 About ShopImpact

Everyday purchases have an environmental impact, but it can be difficult for consumers to understand that impact while shopping.

ShopImpact addresses this problem by transforming purchase information into simple, understandable environmental feedback.

Users can enter information such as:

- Product name
- Product type
- Brand
- Price
- Quantity
- Purchase date

The application then uses predefined product-type impact multipliers to produce an **estimated CO₂ impact** and provides feedback about the user's shopping choices.

Instead of presenting sustainability as something complicated or guilt-driven, ShopImpact uses **friendly language, visual feedback, achievements, eco tips, and greener alternatives** to encourage awareness and better decision-making.

---

# 🎯 Project Aim

The main aim of ShopImpact is to create a practical digital tool that helps users:

- Understand the estimated environmental impact of purchases.
- Track their shopping expenditure.
- Monitor monthly CO₂ impact.
- Discover greener alternatives.
- Plan purchases before buying them.
- Build sustainable shopping habits.
- Make informed choices without making the experience complicated.

The application focuses on **awareness, empowerment, and positive reinforcement** rather than simply showing environmental statistics.

---

# ✨ Key Features

## 🛒 1. Purchase Logging

Users can record purchases by entering relevant information such as:

- Product name
- Product type
- Brand
- Price
- Quantity
- Purchase date

The application validates user inputs before adding a purchase to the shopping data.

This creates a structured purchase history that can be used by the dashboard and impact calculations.

---

## 📅 2. Planned Purchases

ShopImpact also supports purchases that users are planning to make.

Planned purchases allow users to think about their choices **before** purchasing an item.

Planned purchases are kept separate from completed purchases so they do not incorrectly increase the current impact totals before their relevant date.

This makes the application useful not only for tracking past choices but also for **conscious purchase planning**.

---

# 🌍 3. CO₂ Impact Estimation

One of the core features of ShopImpact is its CO₂ impact calculation.

Each product category is associated with a predefined environmental impact multiplier.

The application uses the purchase information and multiplier to estimate the environmental impact.

### Basic calculation concept:

```text
Estimated CO₂ Impact
= Price × Product-Type Multiplier × Quantity
```

The result is presented as an **estimate**, rather than an exact measurement, because the actual environmental footprint of a product can depend on many factors such as production, transportation, materials, packaging, and supply chains.

This feature helps users understand the relative impact of different purchasing decisions.

---

# 📊 4. Monthly Impact Dashboard

ShopImpact provides a dashboard that helps users monitor their activity over time.

The dashboard can show information such as:

- Monthly spending
- Estimated monthly CO₂ impact
- Purchase activity
- Recent purchases
- Environmental impact trends

This transforms individual purchase records into information that is easier to understand and reflect on.

---

# 🌱 5. Greener Alternatives

ShopImpact provides greener alternatives based on the selected product type.

For example, a user may be shown alternative products or choices that have a lower estimated environmental impact.

The application can also compare the original purchase with an alternative at a similar price.

The comparison can display:

- Original estimated CO₂ impact
- Alternative estimated CO₂ impact
- Estimated CO₂ savings
- Percentage reduction

This makes the environmental difference between choices more visible.

---

# ⚖️ 6. Alternative Comparison

A dedicated comparison feature allows users to evaluate a purchase against a greener alternative.

The comparison follows the general structure:

```text
Original Product
        ↓
Estimated CO₂ Impact
        ↓
Greener Alternative
        ↓
Estimated CO₂ Impact
        ↓
Estimated Savings
```

This turns sustainability information into a practical decision-making tool rather than just a statistic.

---

# 🏆 7. Achievement & Badge System

ShopImpact uses achievements to make sustainable shopping more engaging.

Badges can be earned when users meet specific conditions related to their purchases and choices.

Examples include:

- 🏅 Low Impact Shopper
- 🌱 Plant Powered
- ♻️ Second-Hand Hero
- 📍 Local Legend
- 🔄 Zero Waste Streak
- 🧠 Smart Planner
- 🍽️ Meal Prep Master
- 🏆 Challenge Champion

The achievement system gives users positive feedback and encourages them to continue making conscious choices.

---

# 🐢 8. Turtle-Inspired Eco Graphics

The project incorporates Turtle-inspired visual elements as part of its sustainability theme.

These graphics can represent positive environmental choices through elements such as:

- Eco badges
- Leaves
- Footprint-style visuals
- Sustainability-themed illustrations

The visual feedback makes the application more engaging and connects directly with the assignment requirement for Turtle graphics.

---

# 🍽️ 9. Meal Prep & Recipe Library

ShopImpact includes a meal-planning section that extends the application beyond basic shopping tracking.

The recipe library contains information such as:

- Recipe name
- Meal type
- Preparation time
- Estimated CO₂ per serving
- Cost
- Ingredients
- Recipe tags
- Greener ingredient swaps

Users can explore recipes and add or remove recipes from their meal plan.

The recipe section helps connect **meal planning with conscious grocery shopping**.

---

# 🥗 10. Greener Recipe Swaps

Some recipes provide suggestions for greener ingredient choices.

These swaps help users consider the environmental impact of ingredients while planning meals.

This creates a connection between:

```text
Meal Planning
      ↓
Ingredient Choices
      ↓
Grocery Decisions
      ↓
Environmental Awareness
```

---

# 💡 11. Eco Tips

ShopImpact provides sustainability-focused tips and feedback to help users understand how small choices can contribute to more conscious consumption.

Examples of feedback include suggestions related to:

- Choosing lower-impact products
- Considering alternatives
- Planning purchases
- Reducing unnecessary purchases
- Making more sustainable food choices

The purpose is to provide **helpful guidance rather than negative or guilt-based messaging**.

---

# 🎯 12. Monthly Goals & Smart Feedback

The application provides feedback based on user activity and environmental impact.

Instead of only displaying raw numbers, ShopImpact helps users interpret their results through:

- Impact labels
- Achievement progress
- Eco tips
- Alternative suggestions
- Monthly information
- Positive feedback

This makes the dashboard more meaningful for everyday users.

---

# 🧠 Python Implementation

ShopImpact demonstrates the use of core Python programming concepts.

## Lists

Lists are used to manage collections of information such as:

- Purchases
- Recipes
- Ingredients
- Product categories
- Alternative suggestions
- Achievements

Example concept:

```python
purchases = []
```

Purchase records can then be added and processed throughout the application.

---

## Dictionaries

Dictionaries are used to store structured information using key-value pairs.

They are suitable for representing:

- Product information
- CO₂ multipliers
- Recipe information
- Achievement rules
- Greener alternatives

Example concept:

```python
product = {
    "type": "Clothing",
    "price": 1200,
    "brand": "Example Brand"
}
```

---

## Conditional Logic

Conditional statements are used throughout the application to determine:

- CO₂ impact levels
- Badge eligibility
- Input validation
- Alternative suggestions
- Purchase status
- User feedback
- Achievement conditions

Example:

```python
if impact < threshold:
    # provide low-impact feedback
```

---

## Functions

The application is organised into modular functions rather than placing all logic into one section of code.

Functions are used for tasks such as:

- Initialising session state
- Rendering the interface
- Processing purchases
- Calculating impact
- Displaying achievements
- Rendering recipes
- Comparing alternatives
- Showing feedback

This improves code organisation, readability, and maintainability.

---

# 🗃️ Data Structures

ShopImpact uses structured data to connect different parts of the application.

| Data | Purpose |
|---|---|
| Lists | Store collections such as purchases and recipes |
| Dictionaries | Store structured product and recipe information |
| Product multipliers | Estimate CO₂ impact |
| Achievement rules | Determine badge eligibility |
| Recipe data | Support meal planning |
| Alternative data | Recommend greener choices |

These structures allow the application to transform user input into meaningful output.

---

# 🧮 CO₂ Calculation Logic

The CO₂ system is based on product-type multipliers.

The general process is:

```text
User enters purchase
        ↓
Product type identified
        ↓
Relevant multiplier selected
        ↓
Price and quantity processed
        ↓
Estimated CO₂ calculated
        ↓
Impact displayed to the user
        ↓
Feedback / alternatives provided
```

The application uses the resulting estimate to support dashboards, comparisons, tips, and achievement logic.

---

# 🔄 Application Workflow

The overall ShopImpact experience follows this flow:

```text
Start Application
        ↓
User Profile / Onboarding
        ↓
Enter Shopping Information
        ↓
Choose Product Type
        ↓
Enter Price, Brand & Quantity
        ↓
Calculate Estimated CO₂ Impact
        ↓
Add Purchase / Plan Purchase
        ↓
Update Dashboard
        ↓
Display Impact Feedback
        ↓
Suggest Greener Alternatives
        ↓
Compare Choices
        ↓
Update Achievements
        ↓
Explore Meal Planning & Recipes
```

---

# 🎨 Streamlit Interface

The application is built using **Streamlit**, allowing Python code to create an interactive web interface.

The interface focuses on:

- Clear navigation
- Large headings
- Structured sections
- Buttons and interactive controls
- Tabs
- Expandable information
- Dashboard cards
- Friendly feedback
- Visual sustainability indicators
- Earth-inspired design

The application uses separate areas for major functions such as:

- Grocery
- Meal planning
- CO₂ impact

This keeps the interface organised and reduces unnecessary visual clutter.

---

# 🧭 Application Structure

The application is organised into major functional sections.

### Main Application

Responsible for:

- Starting the application
- Initialising session state
- Loading the interface
- Managing navigation
- Displaying major sections

### Grocery Section

Responsible for:

- Recording purchases
- Planning purchases
- Managing shopping information
- Showing purchase-related feedback

### Meal Section

Responsible for:

- Recipe browsing
- Meal planning
- Recipe filtering
- Ingredients
- Preparation time
- CO₂ information
- Greener recipe swaps

### Impact Section

Responsible for:

- CO₂ information
- Monthly impact
- Impact feedback
- Alternative comparisons
- Sustainability suggestions

### Achievement System

Responsible for:

- Checking achievement conditions
- Identifying earned badges
- Displaying locked and unlocked achievements
- Celebrating user progress

---

# 💾 Session State & Data Management

ShopImpact uses Streamlit session state to maintain application information while the user interacts with different parts of the application.

This allows information such as:

- User profile
- Purchases
- Planned purchases
- Meal plans
- Achievements
- Interface state

to remain available as the user moves through the application.

This is important because the application contains multiple interactive sections that depend on shared user information.

---

# ✅ Input Validation

Input validation is used to improve reliability and prevent invalid information from being processed.

The application checks user input such as:

- Product information
- Price
- Quantity
- Required fields
- Purchase details

Validation helps reduce calculation errors and improves the overall user experience.

---

# 🧪 Testing & Reliability

ShopImpact was designed to be tested using different types of purchase scenarios.

Testing should include combinations such as:

- Low-cost purchases
- High-cost purchases
- Different product categories
- Different quantities
- Eco-friendly choices
- Higher-impact choices
- Planned purchases
- Alternative comparisons
- Different achievement conditions

The main purpose of testing is to ensure that:

- Calculations update correctly.
- Purchases are stored correctly.
- Planned purchases are handled separately.
- Dashboard information changes appropriately.
- Badges are awarded according to their rules.
- Greener alternatives appear correctly.
- Recipe and meal-planning features respond correctly.
- The interface remains clear and usable.

The assignment specifically recommends testing **10–15 purchases**, including expensive, cheap, eco-friendly, and non-eco-friendly examples.

---

# 🌟 User Experience Design

ShopImpact is designed around the idea that sustainability tools should feel approachable rather than overwhelming.

The application uses:

### Clear Information

Important values such as spending and estimated impact are separated into easy-to-understand sections.

### Friendly Feedback

Messages are designed to encourage awareness and positive decision-making.

### Visual Feedback

Badges, graphics, impact cards, and achievement feedback make progress easier to recognise.

### Interactive Design

Users actively interact with their shopping information rather than simply reading static information.

### Personalisation

The profile and meal-planning features allow the application experience to adapt to the user's choices.

---

# 🌍 Social Impact

ShopImpact addresses the issue of **limited awareness about the environmental impact of everyday purchases**.

The application encourages users to:

- Think about the environmental consequences of purchases.
- Compare alternatives.
- Plan purchases more carefully.
- Explore sustainable food choices.
- Track their estimated impact.
- Build awareness through repeated use.

The goal is not to tell users what they must buy. Instead, ShopImpact gives users information that can help them make more informed decisions.

This supports the assignment's focus on creating technology that has **real-world usability and social impact**.

---

# 🔗 Integration of Components

One of the main strengths of ShopImpact is how its individual features work together.

```text
Purchase Input
      ↓
Python Data Structures
      ↓
CO₂ Calculation
      ↓
Impact Dashboard
      ↓
Eco Feedback
      ↓
Greener Alternative
      ↓
Alternative Comparison
      ↓
Achievements
```

The meal-planning system extends this structure:

```text
Recipe
   ↓
Ingredients
   ↓
Meal Plan
   ↓
Grocery Decisions
   ↓
Environmental Awareness
```

This integration means the application functions as one connected system rather than a collection of unrelated features.

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **Streamlit** | Interactive web application interface |
| **Datetime** | Purchase and date-related functionality |
| **Python Lists** | Store collections of data |
| **Python Dictionaries** | Store structured information |
| **Conditional Logic** | Decision-making and rules |
| **Functions** | Modular application structure |
| **Turtle-inspired Graphics** | Eco-themed visual feedback |

The assignment specifically identifies Python constructs such as lists, dictionaries, control structures, and libraries including `datetime` and Streamlit as relevant learning outcomes.

---

# 📁 Project Structure

A typical project structure is organised around the main Python application and its supporting files.

```text
ShopImpact/
│
├── finall(1).py
├── requirements.txt
└── README.md
```

The main Python file contains the application's interface, logic, calculations, data structures, and interactive functionality.

---

# 🔮 Future Improvements

Possible future improvements could include:

- Connecting to larger real-world sustainability datasets.
- Adding more product categories.
- Expanding the greener-alternative database.
- Adding more recipe options.
- Introducing additional accessibility settings.
- Adding long-term sustainability trends.
- Allowing users to export personal impact summaries.
- Adding more personalised recommendations.
- Improving data persistence beyond the current session-based system.

These improvements could make ShopImpact more useful as a long-term sustainability companion.

---

# 🏁 Conclusion

ShopImpact combines **Python programming, interactive Streamlit design, data structures, environmental calculations, visual feedback, meal planning, and sustainability recommendations** into one practical application.

The project goes beyond simply calculating numbers. It turns shopping information into understandable feedback and gives users opportunities to compare choices, plan purchases, discover alternatives, and recognise positive behaviour.

Through its combination of **functionality, interactivity, visual design, and social purpose**, ShopImpact demonstrates how Python can be used to create a practical technology solution for conscious consumerism.

### 🌱 ShopImpact

**Track your choices. Understand your impact. Shop more consciously.**
