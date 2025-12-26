import streamlit as st
import requests
import base64

st.set_page_config("SEO AutoGen Writer", layout="wide")

st.title("🚀 SEO Content Writer (Multi-Agent AI)")

topic = st.text_input("SEO Topic")
rounds = st.slider("Refinement Rounds", 1, 5, 3)

if st.button("Generate Article"):
    with st.spinner("Agents working..."):
        response = requests.post(
    "http://127.0.0.1:8000/write",
    json={"topic": topic, "rounds": rounds}
    )

        if response.status_code != 200:
            st.error("Backend error")
            st.text(response.text)
            st.stop()

        try:
            res = response.json()
        except Exception:
            st.error("Invalid JSON received from backend")
            st.text(response.text)
            st.stop()


    # ---- STATUS ----
    st.subheader("🧠 Agent Status")

    status = res.get("status")

    if status:
        cols = st.columns(len(status))
        for i, (k, v) in enumerate(status.items()):
            cols[i].metric(k, v)
    else:
        st.info("Agent status tracking not enabled.")

    # ---- SCORES ----
    # st.subheader("📊 Quality Scores")
    # s = res["scores"]
    # st.progress(s["overall"] / 100)
    # st.write(s)

    # ---- ARTICLE ----
    st.subheader("📝 Final Article")
    st.markdown(res["article"])

    # ---- EXPORT HTML ----
    # html = f"""
    # <html>
    # <head><title>{topic}</title></head>
    # <body>
    # <h1>{topic}</h1>
    # {res['article']}
    # </body>
    # </html>
    # """

    # b64 = base64.b64encode(html.encode()).decode()
    # st.download_button(
    #     "📥 Export as HTML",
    #     data=html,
    #     file_name=f"{topic}.html",
    #     mime="text/html"
    # )
