#!/bin/bash

# Sample curl script
# This script demonstrates a basic curl GET request to RunPod API
# Run this script with the API token as an environment variable
# Usage: RUNPOD_API_TOKEN=your_token_here ./sample_curl.sh

# Check if API token is provided
if [ -z "$RUNPOD_API_KEY" ]; then
  echo "Error: RUNPOD_API_KEY environment variable is not set"
  echo "Usage: RUNPOD_API_KEY=your_token_here ./sample_curl.sh"
  exit 1
fi

# Execute GET request, format JSON with Python, and save to response.json
echo "Fetching data from RunPod API..."
curl 'https://rest.runpod.io/v1/pods?computeType=GPU&includeMachine=true&includeNetworkVolume=true&includeSavingsPlans=true' \
  --header "Authorization: Bearer $RUNPOD_API_KEY" |
  python -m json.tool >running_pods_response.json

echo "Response saved to running_pods_response.json"
