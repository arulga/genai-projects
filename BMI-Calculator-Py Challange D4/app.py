import streamlit as st

def calculate_bmi(weight, height_cm):
    """
    Calculate BMI from weight (kg) and height (cm)
    BMI = weight / (height in meters)²
    """
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    """
    Categorize BMI according to WHO standards
    """
    if bmi < 18.5:
        return "Underweight", "🔵"
    elif 18.5 <= bmi < 25:
        return "Normal weight", "🟢"
    elif 25 <= bmi < 30:
        return "Overweight", "🟡🟢"
    else:
        return "Obese", "🔴"

def get_health_tip(category):
    """
    Provide health tips based on BMI category
    """
    tips = {
        "Underweight": "Consider consulting a healthcare provider for a nutrition plan to reach a healthy weight.",
        "Normal weight": "Great! Maintain your healthy lifestyle with balanced diet and regular exercise.",
        "Overweight": "Consider incorporating regular physical activity and a balanced diet to reach a healthy weight.",
        "Obese": "Consult with a healthcare provider for a personalized weight management plan."
    }
    return tips.get(category, "")

# Page configuration
st.set_page_config(
    page_title="BMI Calculator",
    page_icon="🏋️",
    layout="centered"
)

# Main title with emoji
st.title("🏋️ BMI Calculator")
st.markdown("### Calculate your Body Mass Index")
st.markdown("---")

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=300.0,
        value=70.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    height = st.number_input(
        "Height (cm)",
        min_value=50.0,
        max_value=250.0,
        value=170.0,
        step=0.1,
        format="%.1f"
    )

# Calculate button
if st.button("Calculate BMI", type="primary", use_container_width=True):
    # Calculate BMI
    bmi = calculate_bmi(weight, height)
    category, emoji = get_bmi_category(bmi)
    health_tip = get_health_tip(category)
    
    # Display results
    st.markdown("---")
    st.markdown("### Results")
    
    # BMI value in a metric display
    st.metric(label="Your BMI", value=f"{bmi}")
    
    # Category with emoji
    st.markdown(f"### {emoji} Category: **{category}**")
    
    # Health tip
    st.info(health_tip)
    
    # BMI scale visualization
    st.markdown("---")
    st.markdown("### BMI Scale Reference")
    
    # Create a visual scale
    scale_data = {
        "Category": ["Underweight", "Normal", "Overweight", "Obese"],
        "Range": ["< 18.5", "18.5 - 24.9", "25.0 - 29.9", "≥ 30.0"],
        "Status": ["🔵", "🟢", "🟡", "🔴"]
    }
    
    # Display as a nice table
    for i in range(len(scale_data["Category"])):
        if scale_data["Category"][i] == category:
            st.markdown(f"**{scale_data['Status'][i]} {scale_data['Category'][i]}: {scale_data['Range'][i]}** ← You are here")
        else:
            st.markdown(f"{scale_data['Status'][i]} {scale_data['Category'][i]}: {scale_data['Range'][i]}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>BMI is a screening tool and not a diagnostic of body fatness or health.</p>
    <p>Consult with healthcare professionals for personalized health advice.</p>
</div>
""", unsafe_allow_html=True)