import json
import os
import sys

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from google.adk.artifacts import InMemoryArtifactService
# Add the project root to sys.path to allow importing brand_aligner_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from .agent import root_agent

load_dotenv(override=True)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=f"gs://{STAGING_BUCKET}",
)

adk_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
    artifact_service_builder=InMemoryArtifactService
)

if os.path.exists(".agent_engine_resource.json"):
    with open(".agent_engine_resource.json") as f:
        app_resource_data = json.load(f)
        existing_resource_name = app_resource_data.get("resource_name")
else:
    existing_resource_name = None

requirements = r"/Users/sohamkshirsagar/Projects/Agent-Pharma/requirements.txt"
common_args = {
    "agent_engine": adk_app,
    "extra_packages": ["clinical_trial_decision_agent"],
    "requirements": requirements,
    "env_vars": {
        "PROJECT_ID": PROJECT_ID,
        "LOCATION": LOCATION,
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv(
            "GOOGLE_GENAI_USE_VERTEXAI", "true"
        ),
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": os.getenv(
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", "true"
        ),
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": os.getenv(
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true"
        ),
        "GCS_BUCKET_NAME": GCS_BUCKET,
        "MODEL_NAME": os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        "MODE": "production",
    },
    "gcs_dir_name": "build-dev",
    "display_name": "Clinical Trial Decision Agent",
    "description": "Evaluates clinical trial data and provides intelligent decision support for trial management and patient enrollment decisions.",
}

if existing_resource_name:
    print(f"Updating existing Agent Engine resource: {existing_resource_name}")
    remote_app = agent_engines.update(
        resource_name=existing_resource_name,
        **common_args,
    )
else:
    print("Creating new Agent Engine resource")
    remote_app = agent_engines.create(
        **common_args,
    )

print("Deployment finished!")

app_resource_data = {"resource_name": remote_app.resource_name}
with open(".agent_engine_resource.json", "w") as f:
    json.dump(app_resource_data, f, indent=2)

print(f"Resource Name: {remote_app.resource_name}")
