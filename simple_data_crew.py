import sqlite3
from crewai import Agent, Task, Process, Crew, LLM

# 0) Initialize the LLM
llm=LLM(model="ollama/gemma2:2b", base_url="http://localhost:11434")

# 1) Connect to the database and fetch supplier data
conn = sqlite3.connect('risk.db')
suppliers = conn.execute("SELECT supplier_name, delivery_days, country FROM suppliers").fetchall()
supplier_text = "\n".join([f"{name}: {days} days from {location}" for name, days, location in suppliers])
conn.close()

# 2) Initialize the CrewAI agent
agent = Agent(
    role="Risk Analyst",
    goal="Analyze supplier risks and provide concise risk notes",
    backstory="I analyze supplier data and generate risk notes.",
    verbose=True,
    allow_delegation=True,
    llm=llm
)

# 3) Create the task
task = Task(
    description=f"""Analyze supplier risks for the following supplier info:
{supplier_text}
Provide concise risk notes for each supplier (<= 12 words).""",
    expected_output="A list of concise risk notes for each supplier (<= 12 words)",
    agent=agent
)

# 4) Create and run the Crew
crew = Crew(
     agents=[agent],
     model="ollama/gemma2:2b",
     tasks= [task],
     cache=True,
     verbose=True,
     process=Process.sequential,
     planning=False,
     planning_llm=llm
 )

# 5) Kickoff the crew and get results
results = crew.kickoff()
print(results)