"""
GI-Aware Metabolic Health Coach
A rule-based Streamlit app that predicts metabolic risk and generates a
personalized, Glycemic-Index-aware diet + exercise plan for sedentary tech workers.
"""

import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Metabolic Health Coach", page_icon="⚖️", layout="wide")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    food_df = pd.read_csv("data/food_db.csv")
    exercise_df = pd.read_csv("data/exercise_db.csv")
    return food_df, exercise_df

food_df, exercise_df = load_data()

# ---------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_bmr(weight_kg, height_cm, age, gender):
    if gender == "Male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

ACTIVITY_MULTIPLIER = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly Active (1-3 days/week)": 1.375,
    "Moderately Active (3-5 days/week)": 1.55,
}

def calculate_risk_score(bmi, waist_cm, gender, sitting_hours, family_history, age):
    score = 0
    if bmi >= 25:
        score += 2
    if bmi >= 30:
        score += 2
    if (gender == "Male" and waist_cm > 90) or (gender == "Female" and waist_cm > 80):
        score += 2
    if sitting_hours >= 8:
        score += 2
    if family_history == "Yes":
        score += 2
    if age > 45:
        score += 1
    return score

def risk_band(score):
    if score <= 3:
        return "Low Risk", "🟢"
    elif score <= 6:
        return "Moderate Risk", "🟡"
    else:
        return "High Risk", "🔴"

def get_meal_plan(food_df, calorie_target, risk_level, diet_pref):
    """Filters the food DB and picks one Breakfast/Lunch/Dinner item each."""
    pool = food_df.copy()
    if diet_pref == "Veg":
        pool = pool[pool["Category"] == "Veg"]
    # else Non-Veg users can still eat Veg items too, so no filter needed

    # Moderate/High risk -> restrict to Low GI foods only
    if risk_level != "Low Risk":
        pool = pool[pool["GI_Category"] == "Low"]

    meal_plan = {}
    for meal in ["Breakfast", "Lunch", "Dinner"]:
        options = pool[pool["Meal_Type"] == meal]
        if options.empty:  # fallback if filter is too strict
            options = food_df[food_df["Meal_Type"] == meal]
        # prefer higher protein options for Lunch/Dinner
        if meal in ["Lunch", "Dinner"]:
            options = options.sort_values("Protein_g", ascending=False)
        meal_plan[meal] = options.iloc[0] if not options.empty else None

    return meal_plan

def get_exercise_plan(exercise_df, age, sitting_hours):
    if age > 50:
        level = "Beginner"
    elif sitting_hours >= 8:
        level = "Intermediate"
    else:
        level = "Beginner"

    matches = exercise_df[exercise_df["Difficulty_Level"] == level]
    if len(matches) < 3:
        matches = exercise_df
    return matches.sample(min(3, len(matches)), random_state=42)

# ---------------------------------------------------------
# UI — AWARENESS SECTION
# ---------------------------------------------------------
st.title("⚖️ GI-Aware Metabolic Health Coach")
st.markdown("""
Metabolic Syndrome is a cluster of conditions — **high blood sugar, excess abdominal fat,
abnormal cholesterol, and elevated blood pressure** — that together raise the risk of
diabetes, heart disease, and fatty liver. Sedentary tech workers are especially vulnerable
due to long sitting hours, irregular meals, and high-Glycemic-Index diets.

This tool takes your health data and builds a personalized, **GI-aware** diet and fitness
plan to help you manage that risk.
""")

st.divider()

# ---------------------------------------------------------
# UI — INPUT FORM
# ---------------------------------------------------------
st.header("📝 Tell us about yourself")

with st.form("health_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", min_value=15, max_value=90, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)

    with col2:
        height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=170.0)
        waist = st.number_input("Waist Circumference (cm)", min_value=50.0, max_value=160.0, value=85.0)
        sitting_hours = st.slider("Hours sitting per day", 0, 16, 8)

    with col3:
        activity_level = st.selectbox("Activity Level", list(ACTIVITY_MULTIPLIER.keys()))
        diet_pref = st.selectbox("Diet Preference", ["Veg", "Non-Veg"])
        family_history = st.selectbox("Family history of diabetes/hypertension?", ["No", "Yes"])

    submitted = st.form_submit_button("Get My Plan →", use_container_width=True)

# ---------------------------------------------------------
# UI — OUTPUT DASHBOARD
# ---------------------------------------------------------
if submitted:
    bmi = calculate_bmi(weight, height)
    bmi_cat = bmi_category(bmi)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = bmr * ACTIVITY_MULTIPLIER[activity_level]

    score = calculate_risk_score(bmi, waist, gender, sitting_hours, family_history, age)
    risk_level, risk_emoji = risk_band(score)

    # Weight-loss calorie target only if overweight/at risk, else maintenance
    if bmi >= 25 or risk_level != "Low Risk":
        calorie_target = tdee - 500
    else:
        calorie_target = tdee

    protein_target = round(weight * 1.2)  # simple ~1.2g/kg guideline

    st.divider()
    st.header("📊 Your Results")

    # --- Risk summary cards ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMI", f"{bmi}", bmi_cat)
    c2.metric("Metabolic Risk", f"{risk_emoji} {risk_level}", f"Score: {score}")
    c3.metric("Daily Calorie Target", f"{round(calorie_target)} kcal")
    c4.metric("Protein Target", f"{protein_target} g")

    st.divider()

    # --- Meal plan + exercise plan ---
    meal_col, exercise_col = st.columns([1.3, 1])

    with meal_col:
        st.subheader("🍽️ Your Sample 1-Day Meal Plan")
        if risk_level != "Low Risk":
            st.caption("Since your risk is moderate/high, meals are restricted to **Low-GI** foods.")
        meal_plan = get_meal_plan(food_df, calorie_target, risk_level, diet_pref)
        total_cal = 0
        for meal_name, item in meal_plan.items():
            if item is not None:
                total_cal += item["Calories"]
                with st.container(border=True):
                    st.markdown(f"**{meal_name}: {item['Food_Item']}**  ({item['Portion_Size']})")
                    st.caption(
                        f"{item['Calories']} kcal · {item['Protein_g']}g protein · "
                        f"GI: {item['GI_Category']}"
                    )
        st.caption(f"Total: ~{total_cal} kcal across the day")

    with exercise_col:
        st.subheader("🏃 Recommended Exercises")
        plan = get_exercise_plan(exercise_df, age, sitting_hours)
        for _, ex in plan.iterrows():
            with st.container(border=True):
                st.markdown(f"**{ex['Exercise_Name']}**")
                st.caption(f"{ex['Target_Area']} · {ex['Calories_Burned_Per_Minute']} kcal/min · {ex['Difficulty_Level']}")

    st.divider()
    