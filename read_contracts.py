import fitz
from crewai import Agent, Task, Crew, Process, LLM

# 0) Initialize the LLM
llm = LLM(model="ollama/gemma2:2b", base_url="http://localhost:11434")

# 1) Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

# 2) Initialize the Agent
agent = Agent(
    role="Contract Scanner",
    goal="Find risky words in contracts",
    backstory="Scans contracts for risky words",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 3) Create Task dynamically with extracted text
pdf_text = extract_text_from_pdf("sample_contract.pdf")
prompt = f"""
Below is a supplier contract.
List exactly 10 words that indicate risk (one word per line, followed by a short sentence about why each word is risky).:
{pdf_text[:1500]}...
"""

task = Task(
    description=prompt,
    expected_output="A list of exactly 10 risky words with explanations.",
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

# 5) Execute and save results in .txt file
results = crew.kickoff()
output_text = results.raw
risky_words = output_text.strip().splitlines()
with open("risky_contract_words.txt", "w") as f:
    f.write("\n".join(risky_words))

print("Risky words saved:", risky_words)