import streamlit as st

st.title("BMI Calculator 🏋️")

height = st.number_input("Enter your height (cm):", min_value=1.0, step=0.1)
weight = st.number_input("Enter your weight (kg):", min_value=1.0, step=0.1)

if st.button("Calculate BMI"):
    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"

    st.success(f"Your BMI is **{bmi:.2f}** — {category}")
