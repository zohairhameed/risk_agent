from crewai import Agent, Task, Process, Crew, LLM
import sqlite3


#LLM Object from crewai package
llm=LLM(model="ollama/gemma2:2b", base_url="http://localhost:11434")

# Initialize the CrewAI agent
agent = Agent(
    role="Risk Analyst",
    goal="Analyze supplier risks and provide concise risk notes",
    backstory="I analyze supplier data and generate risk notes.",
    verbose=True,
    allow_delegation=True,
    llm=llm
)

# Connect to the database
conn = sqlite3.connect('risk.db')
cursor = conn.cursor()

# Fetch supplier data
cursor.execute("SELECT supplier_name, delivery_days FROM suppliers")
suppliers = cursor.fetchall()

# Close the database connection
conn.close()

# Format suppliers as plain text
supplier_text = "\n".join([f"{name}: {days} days" for name, days in suppliers])

task = Task(
    description=f"""Analyze supplier risks for the following suppliers and their delivery days:
{supplier_text}

Provide concise risk notes for each supplier.""",
    expected_output="A list of concise risk notes for each supplier",
    agent=agent
)

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

results = crew.kickoff()

print(results)