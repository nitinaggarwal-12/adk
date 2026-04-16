# Configuration
PROJECT_ID="project53758"
PROJECT_NUMBER="88799445578"
GEMINI_ENTERPRISE_APP_ID="gemini-enterprise-17759345_1775934564639"
AGENT_DISPLAY_NAME="Clinical Trial Decision Agent"

# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# API endpoint for listing agents
LIST_ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${GEMINI_ENTERPRISE_APP_ID}/assistants/default_assistant/agents"

# List agents
echo "Listing agents in Gemini Enterprise app..."
AGENTS_RESPONSE=$(curl -s -X GET \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "${LIST_ENDPOINT}")

# Extract agent resource names with matching display name
AGENT_NAMES=$(echo "${AGENTS_RESPONSE}" | grep -A 10 '"displayName": "'${AGENT_DISPLAY_NAME}'"' | grep '"name":' | cut -d'"' -f4)

if [[ -z "${AGENT_NAMES}" ]]; then
  echo "No agents found with display name: ${AGENT_DISPLAY_NAME}"
  exit 0
fi

# Delete each agent
echo "Deregistering agents..."
for AGENT_NAME in ${AGENT_NAMES}; do
  echo "Deleting agent: ${AGENT_NAME}"
  DELETE_RESPONSE=$(curl -s -X DELETE \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "https://discoveryengine.googleapis.com/v1alpha/${AGENT_NAME}")
  
  if [[ $? -eq 0 ]]; then
    echo "✓ Agent ${AGENT_NAME} deregistered successfully"
  else
    echo "✗ Failed to deregister agent ${AGENT_NAME}"
  fi
done

echo "Deregistration complete."