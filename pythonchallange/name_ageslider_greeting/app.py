import streamlit as st

st.set_page_config(page_title="Greeting App", page_icon="❄️")

st.title("🎉 Greeting Form")

name = st.text_input("Enter your name:")
age = st.slider("Select your age:", 1, 100, 25)

if st.button("Submit"):
    if name:
        st.info(f"Hello, {name}! You are {age} years young 🎂")
        st.toast(f"👋 Hello, {name}! You are {age} years young 🎂", icon="🎉")
        st.balloons()  # ❄️ Snow animation
    else:
        st.toast("⚠️ Please enter your name first.", icon="⚠️")

# ---- Footer ----
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f0f2f6;
    color: #555;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
}
</style>
<div class="footer">
Python Challenge 1-15, Made with ❤️ using Streamlit | NeoForge © 2025
</div>
"""
st.markdown(footer, unsafe_allow_html=True)