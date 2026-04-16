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
    description="Agent that queries clinical trial data from BigQuery.",
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
    - Use the 'run_bigquery' tool to execute queries.
    - Dataset name: diabetes
    - Tables:
        - patients
        - patient_treatements

    - Always write correct SQL before calling the tool.
    - Return clear and concise answers.
  
    - If the user asks to notify, alert, or send results:
        → use 'send_to_slack'

    """,
    tools=[run_bigquery],
)


# -- another use case -- 
# def predict_treatment(patient_data: dict) -> dict:
#     job_config = bigquery.QueryJobConfig(
#         default_dataset="project53758.53758"
#     )

#     query = f"""
#     WITH patient AS (
#       SELECT
#         {patient_data['hba1c_start']} AS hba1c_start,
#         {patient_data['starting_dosage']} AS starting_dosage,
#         '{patient_data['assigned_sex']}' AS assigned_sex,
#         {patient_data['bmi']} AS bmi
#     ),
#     treatments AS (
#       SELECT 'auralin' AS medicine_type UNION ALL
#       SELECT 'novodra'
#     )

#     SELECT
#       medicine_type,
#       predicted_has_adverse_effect_probs[OFFSET(1)].prob AS adverse_risk
#     FROM ML.PREDICT(
#       MODEL `project53758.53758.person_treatment_logistic_regression_model`,
#       (
#         SELECT *
#         FROM patient
#         CROSS JOIN treatments
#       )
#     )
#     """

#     df = client.query(query, job_config=job_config, project=os.getenv('GOOGLE_CLOUD_PROJECT')).to_dataframe()

#     result = {}
#     for _, row in df.iterrows():
#         prob = float(row["adverse_risk"])  # now this will work

#         result[row["medicine_type"]] = {
#             "adverse_effect": "No" if prob > 0.5 else "Yes",
#             "probability": round(prob, 3)
#         }

#     return result

# def explain_recommendation(prediction: dict, patient_data: str) -> str:
#     prompt = f"""
#     Patient Data: {patient_data}
#     Prediction: {prediction}

#     Explain which treatment (Auralin vs Novodra) is better and why.
#     Keep it clinical, natural language and concise
#     """

#     model = GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content(prompt)
#     return response.text

# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='Clinical trial decision agent for recommending treatments.',
    
#     generate_content_config={
#         "temperature": 0,
#     },
    
#     instruction="""
#     You are a clinical agent.

#     Step 1: Extract patient data into JSON using load artifact tool:
#     {"hba1c_start": float, "starting_dosage": int, "assigned_sex": string, "bmi": float}

#     Step 2: Call predict_treatment with extracted JSON.

#     Step 3: Call explain_recommendation using prediction output.

#     ALWAYS call one function at a time.
#     NEVER combine multiple function calls.
#     """,
    
#     tools=[
#         FunctionTool(predict_treatment),
#         FunctionTool(explain_recommendation),
#         load_artifacts
#     ]
# )