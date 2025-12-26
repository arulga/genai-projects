from fastapi import FastAPI
from pydantic import BaseModel
from autogen import AssistantAgent, GroupChat, GroupChatManager
import re, json
import os
from dotenv import load_dotenv
load_dotenv()


os.getenv("OPENAI_API_KEY")
app = FastAPI()

class WriteRequest(BaseModel):
    topic: str
    rounds: int = 3

llm_config = {
    "model": "gpt-4o-mini",
    "temperature": 0.7
}

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group())
    except Exception:
        return {
            "accuracy": 0,
            "seo": 0,
            "readability": 0,
            "overall": 0,
            "comments": "Invalid scoring JSON"
        }

# ---- AGENTS ----
seo_writer = AssistantAgent(
    name="SEO_Writer",
    system_message="""You are a professional SEO content writer with 10+ years of experience.

Rules:
- Write high-quality, original, human-like content
- Minimum output length: 1000 characters (strict)
- Use clear headings and subheadings
- Avoid repetition and filler
- Ensure factual accuracy
- Do not mention being an AI
""",
    llm_config=llm_config
)

editor = AssistantAgent(
    name="Editor",
    system_message="Improve clarity and structure.",
    llm_config=llm_config
)

fact_checker = AssistantAgent(
    name="Fact_Checker",
    system_message="Verify facts and fix inaccuracies.",
    llm_config=llm_config
)

optimizer = AssistantAgent(
    name="SEO_Optimizer",
    system_message="Optimize for SEO best practices.",
    llm_config=llm_config
)

qa_scorer = AssistantAgent(
    name="QA_Scorer",
    system_message="""
Return ONLY JSON:
{
 "accuracy":0,
 "seo":0,
 "readability":0,
 "overall":0,
 "comments":""
}
""",
    llm_config=llm_config
)
AGENT_STATUS = {}
def set_status(agent, state):
    AGENT_STATUS[agent] = state

@app.post("/write")
def write_article(req: WriteRequest):
    AGENT_STATUS.clear()

    set_status("SEO_Writer", "running")

    groupchat = GroupChat(
        agents=[seo_writer, editor, fact_checker, optimizer],
        messages=[],
        max_round=req.rounds,
        speaker_selection_method="round_robin"
    )

    manager = GroupChatManager(groupchat=groupchat)

    manager.initiate_chat(
        seo_writer,
        message=f"Write an SEO article about {req.topic}"
    )

    set_status("SEO_Writer", "completed")
    set_status("Editor", "completed")
    set_status("Fact_Checker", "completed")
    set_status("SEO_Optimizer", "completed")

    article = groupchat.messages[-1]["content"]

    score_response = qa_scorer.generate_reply(
        messages=[{"role": "user", "content": article}]
    )

    scores = extract_json(score_response)

    return {
        "article": article,
        "scores": scores,
        "status": AGENT_STATUS   # ✅ NOW EXISTS
    }
