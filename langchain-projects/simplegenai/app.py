from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    model="gpt-4o-mini"
)

prompt = PromptTemplate(
    input_variables=["user_input"],
    template="You are a helpful assistant. Answer: {user_input}"
)

chain = prompt | llm | StrOutputParser()

print("ask me anything")
user_input = input()

response = chain.invoke({"user_input": user_input})

print(response)
