import sqlite3, json, re
from crewai import Agent, Task, Process, LLM, Crew

# 1) Initialize the LLM
llm = LLM(model="ollama/gemma2:2b", base_url="http://localhost:11434")

# 2) Fetch real data from SQLite
conn = sqlite3.connect('risk.db')
suppliers = conn.execute("SELECT supplier_name, delivery_days, country FROM suppliers").fetchall()
outside = conn.execute("SELECT data FROM outside_data WHERE source='sanctions'").fetchone()[0]
conn.close()

# 3) Prepare input for Task 1
input_data = {
    "suppliers": [{"name": n, "days": d, "country": c} for n, d, c in suppliers],
    "sanctions": json.loads(outside)
}

# 4) Define Agents
gatherer = Agent(
    role="Data Gatherer",
    goal="Format supplier and sanctions data for scoring",
    backstory="I take raw data and structure it for analysis",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

scorer = Agent(
    role="Risk Scorer",
    goal="Assign numeric scores from 1 to 10 to suppliers based on risk factors",
    backstory="I analyze structured supplier data and generate risk scores from 1 (lowest risk) to 10 (highest risk)",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

fixer = Agent(
    role="Mitigation Planner",
    goal="Suggest one low-cost mitigation action per supplier based on risk scores",
    backstory="I propose simple fixes based on risk scores",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 5) Define Tasks with chaining

# Task 1: Format real data
t1 = Task(
    description=f"""
Format a structured summary suitable for scoring.
Use only the provided data.
Return a clear, structured text listing each supplier with delivery days, country, and sanctions status.
Do not introduce new data.
Data:
{json.dumps(input_data)}
""",
    expected_output="Structured text summary of suppliers and sanctions",
    agent=gatherer
)

# Task 2: Score suppliers using Task 1 output (improved prompt)
t2 = Task(
    description="""
Assign each supplier a risk score from 1 (lowest risk) to 10 (highest risk).
Consider factors like:
- Delivery days (longer = higher risk)
- Country geopolitical stability
- Sanctions status (sanctioned suppliers = higher risk)

Use only the structured summary provided from the previous task.
Return ONLY a valid JSON object with supplier names as keys and risk scores (1-10) as values.
Do not include any markdown formatting, commentary, or explanations.
Example format: {"Supplier A": 3, "Supplier B": 7}
""",
    expected_output="Clean JSON object mapping supplier_name to risk_score (1-10)",
    context=[t1],
    agent=scorer
)

# Task 3: Suggest mitigations using Task 2 output (improved prompt)
t3 = Task(
    description="""
Suggest one practical, low-cost mitigation action per supplier based on their risk scores.
Higher risk suppliers need more comprehensive mitigation actions.
Use only the risk scores provided from the previous task.
Return ONLY a valid JSON object with supplier names as keys and mitigation actions as values.
Do not include any markdown formatting, commentary, or explanations.
Example format: {"Supplier A": "Implement backup supplier", "Supplier B": "Increase safety stock"}
""",
    expected_output="Clean JSON object mapping supplier_name to mitigation_action",
    context=[t2],
    agent=fixer
)

# 6) Crew orchestration
crew = Crew(
    agents=[gatherer, scorer, fixer],
    tasks=[t1, t2, t3],
    cache=True,
    verbose=True,
    process=Process.sequential,
    planning=False,
    planning_llm=llm
)

# 7) Execute the pipeline
results = crew.kickoff()

# 8) Helper function to clean JSON output
def clean_json_output(raw_output):
    """Clean markdown formatting from JSON output"""
    # Convert to string if it's not already
    text = str(raw_output)
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    try:
        # Parse and reformat the JSON for clean display
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        # If parsing fails, return cleaned text
        return text

# 9) Display results with clean formatting
task_outputs = results.tasks_output

clean_scores = clean_json_output(task_outputs[1])
clean_mitigations = clean_json_output(task_outputs[2])
scores_dict = json.loads(clean_scores)
mitigations_dict = json.loads(clean_mitigations)

print("\n--- Combined Results (Table Format) ---")    
print(f"{'Supplier':<15} {'Risk Score':<12} {'Mitigation Action'}")
print("-" * 80)    
for supplier in scores_dict:
    score = scores_dict.get(supplier, "N/A")
    mitigation = mitigations_dict.get(supplier, "N/A")
    print(f"{supplier:<15} {score:<12} {mitigation}")
