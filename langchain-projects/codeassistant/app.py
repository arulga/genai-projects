import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    model="gpt-4o-mini"
)

prompt = PromptTemplate(
    input_variables=["code_task"],
    template=(
        "You are a professional code assistant. Help the user with the following task: "
        "{code_task}. Provide clean, well-commented code and explanations if needed."
    )
)

# NEW LANGCHAIN SYNTAX
chain = prompt | llm

st.title("Code Assistant")

code_task = st.text_area("Describe your coding task:")

if st.button("Generate Code"):
    if code_task.strip() == "":
        st.warning("Please enter a task description.")
    else:
        # Use invoke() in new LangChain
        response = chain.invoke({"code_task": code_task})

        # Extract the model output content
        final_output = response.content  

        st.subheader("Assistant Response")
        st.code(final_output, language='python')
