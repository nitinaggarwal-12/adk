from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel
import os
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools import load_artifacts
from dotenv import load_dotenv
load_dotenv() 

client = bigquery.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
print(os.getenv('GOOGLE_CLOUD_PROJECT'))

import requests
import os

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")  # store in .env

def send_to_slack(message: str) -> dict:
    """Send a message to Slack channel via webhook."""
    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json={"text": message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {"status": "success"}
        else:
            return {"status": "error", "message": response.text}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------- TOOL: BIGQUERY --------
def run_bigquery(query: str) -> dict:
    """Runs a SQL query on BigQuery and returns results."""
    try:
        results = client.query(query).result()
        rows = [dict(row) for row in results]
        return {"status": "success", "rows": rows[:5]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------- AGENT --------
root_agent = Agent(
    model="gemini-2.5-flash",
    name="clinical_data_agent",
    description="Agent that queries clinical trial data and can notify Slack.",
    instruction="""
    You are a clinical data assistant.

    - Convert user questions into SQL queries.
    - Use 'run_bigquery' to fetch data.
    - Summarize results clearly.

    - If the user asks to notify, alert, or send results:
        → use 'send_to_slack'

    - Dataset name: 53758
    - Tables:
        - PersonList
        - Treatment
    """,
    tools=[
        FunctionTool(run_bigquery),
        FunctionTool(send_to_slack)
    ],
)
