#!/bin/sh
# Jev quickstart via curl. Needs TYPESAFE_API_KEY in the environment.
# Usage: TYPESAFE_API_KEY=ts_... sh curl.sh
set -eu

: "${TYPESAFE_API_KEY:?Set TYPESAFE_API_KEY first}"

curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jev-latest",
    "state": "Help! My payments have been failing for 3 days and nobody answers support.",
    "questions": {
      "is_urgent": {
        "type": "noul",
        "instructions": "Does this message express urgency?"
      },
      "department": {
        "type": "choice",
        "instructions": "Which team should handle this?",
        "criteria": {
          "billing": "Payments, invoicing, refunds",
          "technical": "Bugs, outages, integrations",
          "sales": "Pricing, upgrades, new accounts"
        }
      }
    }
  }'
echo
