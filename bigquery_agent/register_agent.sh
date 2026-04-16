#!/bin/bash
# Register ADK Agent to Gemini Enterprise

# Configuration
PROJECT_ID="project53758"
PROJECT_NUMBER="88799445578"
GEMINI_ENTERPRISE_APP_ID="gemini-enterprise-17759345_1775934564639"

# Read ADK_DEPLOYMENT_ID from .agent_engine_resource.json
RESOURCE_FILE="../.agent_engine_resource.json"
if [[ ! -f "${RESOURCE_FILE}" ]]; then
  echo "✗ Error: ${RESOURCE_FILE} not found"
  exit 1
fi
ADK_DEPLOYMENT_ID=$(grep -o '"resource_name": "[^"]*' "${RESOURCE_FILE}" | cut -d'"' -f4)
if [[ -z "${ADK_DEPLOYMENT_ID}" ]]; then
  echo "✗ Error: Could not extract resource_name from ${RESOURCE_FILE}"
  exit 1
fi

AGENT_DISPLAY_NAME="Clinical Trial Decision Agent"
AGENT_DESCRIPTION="AI agent for recommending clinical trial treatments"

# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# API endpoint
API_ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${GEMINI_ENTERPRISE_APP_ID}/assistants/default_assistant/agents"

# Payload
PAYLOAD=$(cat <<EOF
{
  "displayName": "${AGENT_DISPLAY_NAME}",
  "description": "${AGENT_DESCRIPTION}",
  "adk_agent_definition": {
    "provisioned_reasoning_engine": {
      "reasoning_engine": "${ADK_DEPLOYMENT_ID}"
    }
  }
}
EOF
)

# Make POST request
echo "Registering agent to Gemini Enterprise..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  -d "${PAYLOAD}" \
  "${API_ENDPOINT}")

echo "Response:"
echo "${RESPONSE}"

# Extract agent resource name using grep and sed
AGENT_NAME=$(echo "${RESPONSE}" | grep -o '"name": "[^"]*' | cut -d'"' -f4)
if [[ -n "${AGENT_NAME}" ]]; then
  echo ""
  echo "✓ Agent registered successfully!"
  echo "Agent Resource Name: ${AGENT_NAME}"
else
  echo ""
  echo "✗ Registration failed. Check response above."
  exit 1
fi
