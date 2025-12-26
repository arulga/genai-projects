from autogen.agentchat import Agent, Team, Message

# Define agents
seo_agent = Agent(name="SEO Writer", description="Generate the initial article.")
style_agent = Agent(name="Style Agent", description="Improve flow and readability.")
fact_agent = Agent(name="Fact-Check Agent", description="Verify and correct facts.")
opt_agent = Agent(name="SEO Optimize Agent", description="Optimize for search engines.")

# Round-robin function
def round_robin_refine(team, topic, rounds):
    # Initial draft
    seo_msg = Message(role="user", content=f"Write an SEO article about: {topic}")
    team.send(seo_agent, seo_msg)

    latest = None
    for i in range(rounds):
        # iterate agents in order
        for agent in [style_agent, fact_agent, opt_agent]:
            # send last output to next agent
            if latest:
                team.send(agent, Message(role="assistant", content=latest))
            resp = team.chat(agent)
            latest = resp.content
    return latest

# Orchestrator
def write_article(topic, rounds):
    team = Team(agents=[seo_agent, style_agent, fact_agent, opt_agent])
    output = round_robin_refine(team, topic, rounds)
    return output
