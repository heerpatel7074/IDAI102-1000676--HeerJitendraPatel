# IDAI102-1000676--HeerJitendraPatel
ShopImpact is a Python and Streamlit app designed to help shoppers make more sustainable purchasing decisions. It estimates the CO₂ impact of purchases, tracks monthly shopping habits, and provides greener alternatives, insights, grocery planning, and eco badges to turn everyday shopping into conscious choices.
# 🌱 ShopImpact — Conscious Shopping Dashboard

> **Make smarter choices. Track your impact. Shop for a better future.**

An interactive Python + Streamlit application designed to help users understand the environmental impact of their planned purchases. **ShopImpact** allows users to record purchases, estimate associated CO₂ emissions, monitor monthly impact, discover greener alternatives, earn achievement badges, and make more informed consumption choices.

---

## 👤 Student Information

Name: Heer Jitendra Patel  
School Name: Udgam School For Children  
CRS: Artificial Intelligence And Interpretation  
Registration Number: 1000676  
Subject: Python Programming  
Project: Summative Assesment Scenario 1 (ShopImpact)

---

# 📌 About ShopImpact

Shopping decisions are made every day, but the environmental consequences of those decisions are not always easy to understand.

**ShopImpact** addresses this problem through an interactive dashboard that connects everyday purchasing decisions with estimated environmental impact.

Users can enter planned purchases, view estimated CO₂ emissions, monitor spending, receive greener alternatives, and unlock achievements for making more conscious choices.

The application combines **Python programming, calculations, data structures, Streamlit interactivity, recommendation logic, visual design, and gamification** into one functional application.

---

# 🎯 Problem Statement

Consumers often consider factors such as price, quality and brand when shopping, but the environmental impact of their choices may not be immediately visible.

This creates a gap between:

**Purchasing → Understanding Impact → Making Better Choices**

ShopImpact aims to reduce this gap by providing immediate, understandable feedback about the estimated environmental impact of planned purchases.

---

# 💡 Project Aim

The main aim of ShopImpact is to make conscious shopping:

- 🌱 Interactive
- 📊 Understandable
- 💡 Educational
- 🎯 Action-oriented
- 🏆 Engaging
- 🌍 Environmentally aware

Instead of simply presenting environmental information, the application allows users to actively explore the impact of their own planned purchases.

---

# ⚙️ Key Features

## 🛒 1. Interactive Purchase Planning

Users can add planned purchases by entering information such as:

- Product name
- Product type
- Brand
- Price
- Quantity

Purchases are organized into an interactive shopping list.

---

## 🌍 2. Real-Time CO₂ Impact Calculation

ShopImpact estimates the environmental impact of a purchase using curated product-type multipliers.

The calculation follows the basic structure:

**Estimated CO₂ Impact = Purchase Price × Product-Type Multiplier**

The result is updated dynamically as purchases are added, allowing users to immediately understand the potential impact of their choices.

---

## 📊 3. Monthly Impact Dashboard

The application provides a central dashboard showing information such as:

- Total planned spending
- Estimated CO₂ emissions
- Monthly CO₂ target
- Progress toward the target
- Overall impact level

This gives users a quick visual understanding of their current shopping impact.

---

## 🌱 4. Greener Alternatives

ShopImpact provides alternative suggestions based on product categories.

The purpose is to move beyond simply identifying environmental impact and provide users with practical options for making potentially lower-impact choices.

The process is:

**Purchase → Calculate Impact → Suggest Alternative → Encourage Better Choice**

---

## 🏆 5. Achievement & Badge System

ShopImpact uses gamification to make conscious shopping more engaging.

The application includes achievements such as:

- 🌿 **Low Impact Shopper**
- 🥬 **Plant Powered**
- ♻️ **Second-Hand Hero**
- 📍 **Local Legend**
- 🌎 **Zero Waste Streak**
- 🧠 **Smart Planner**
- 🍽️ **Meal Prep Master**
- 🏅 **Challenge Champion**

These badges provide positive feedback when users complete different actions or meet environmental goals.

---

# 🐢 6. Turtle-Inspired Eco Graphics

The application includes a Turtle-inspired graphical system to satisfy the requirement for an eco-friendly Turtle graphic.

The graphics can be used to represent environmental themes such as:

- Eco badges
- Leaves
- Environmental symbols
- Positive user achievements

The graphics are integrated directly into the Streamlit interface rather than opening a separate desktop graphics window.

This combines **programming logic with visual design and gamification**.

---

# 🍽️ 7. Meal Planning

ShopImpact includes an interactive meal-planning section.

Users can explore meal options based on estimated CO₂ impact and use the selected plan to help generate shopping-list items.

The meal-planning system can:

- Recommend recipes
- Compare recipes by estimated impact
- Organize meal options
- Add ingredients to the shopping list

This expands the application beyond individual purchases and demonstrates how environmental thinking can be incorporated into everyday planning.

---

# 🎯 8. Monthly Impact Target

Users can compare their estimated environmental impact with a monthly target.

The dashboard communicates progress using visual indicators and impact levels.

This turns environmental information into a measurable personal objective.

---

# 💡 9. Smart Advice & Impact Insights

ShopImpact provides contextual advice based on the user's purchases and environmental impact.

Rather than displaying only numerical information, the application helps users understand what the numbers mean and encourages more conscious decisions.

---

# 📥 10. Data Management

The application provides functionality for managing purchase information.

Users can:

- Review purchases
- Mark items as completed
- Delete purchases
- Track planned spending
- View environmental impact
- Download relevant information

This makes ShopImpact useful as both an awareness tool and a practical shopping-planning application.

---

# 🧠 Python Implementation

ShopImpact was developed using **Python** with a modular programming structure.

The application separates different responsibilities into reusable functions rather than placing all logic inside one large section.

### Product & CO₂ Logic

The application contains logic for:

- Product validation
- Product-type identification
- CO₂ calculations
- Impact processing

### Purchase Management

Purchase records contain information such as:

- ID
- Product name
- Product type
- Brand
- Quantity
- Price
- Completion status

### Badge Logic

The badge system evaluates user activity and determines which achievements have been unlocked.

### Recommendation Logic

The application uses product categories and purchase information to generate greener alternatives.

### Meal Planning Logic

Recipes are processed using their environmental impact information, allowing lower-impact options to be prioritized.

### State Management

`st.session_state` is used to maintain application data while users navigate between different sections.

This allows the interface and dashboard to update dynamically without unnecessarily losing the user's information.

---

# 🖥️ Streamlit Interface

The application uses **Streamlit** to create an interactive web-based interface.

The interface contains:

- Interactive input controls
- Buttons
- Checkboxes
- Navigation
- Progress indicators
- Dashboard cards
- Achievement displays
- Impact summaries
- Purchase lists
- Download functionality
- Dynamic recommendations

The interface follows a clear visual hierarchy:

**Purchases → Spending → CO₂ Impact → Recommendations → Achievements**

This allows users to understand the application's purpose without needing to understand the underlying Python code.

---

# 🧩 Application Structure

## 🛒 Grocery List

The Grocery List section allows users to:

- Add purchases
- Specify product information
- Set quantities
- Track planned spending
- View estimated impact
- Manage their shopping list

---

## 🍽️ Meal Prep

The Meal Prep section allows users to:

- Explore meal options
- Compare estimated environmental impact
- Select recipes
- Import ingredients into the shopping list

---

## 🌍 CO₂ Tracking

The CO₂ Tracking section allows users to:

- View estimated emissions
- Track monthly impact
- Compare impact with a target
- Understand their impact level
- View environmental insights

---

## 🏆 Achievements

The achievements section provides users with:

- Unlocked badges
- Progress indicators
- Positive feedback
- Motivation to make more conscious choices

---

# 🔄 Application Workflow

```text
User enters purchase information
              ↓
Product type is identified
              ↓
Price and product data are processed
              ↓
Estimated CO₂ impact is calculated
              ↓
Purchase is added to the shopping list
              ↓
Dashboard updates automatically
              ↓
Impact insights are generated
              ↓
Greener alternatives are suggested
              ↓
Achievements may be unlocked
              ↓
User can make a more informed choice
```

---

# 🧮 CO₂ Calculation Logic

ShopImpact uses curated product-category multipliers to estimate environmental impact.

For a purchase:

```text
CO₂ Impact = Price × Product-Type Multiplier
```

The result is then incorporated into the overall dashboard.

This allows ShopImpact to provide immediate feedback instead of requiring users to manually calculate their estimated environmental impact.

> **Note:** The CO₂ values generated by the application are estimates based on the application's curated multipliers. They are intended for awareness and comparison rather than precise lifecycle assessments of individual products.

---

# 🧠 Data Structures

The application uses Python data structures to organize and process information efficiently.

### Lists

Lists are used for collections such as:

- Purchases
- Recipes
- Product information
- Achievement information
- Alternative suggestions

### Dictionaries

Dictionaries are used to store structured information such as:

- Product details
- Purchase records
- Brand information
- Recipe information
- Badge conditions
- Environmental multipliers

This structure allows the application to retrieve and update information efficiently.

---

# 🔐 Input Validation

ShopImpact validates user input before processing it.

The application checks conditions such as:

- Product name is not empty
- Product type is valid
- Quantity is greater than zero
- Price is not negative
- Required information has been provided

This reduces invalid data and prevents

Streamlit Link:https://idai102-1000676--heerjitendrapatel-2g7v29v65qjct9w9qge4up.streamlit.app/
