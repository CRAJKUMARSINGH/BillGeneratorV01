# Phase 9 — SaaS, Mobile & AI Plan (summary)

This PR adds a minimal API gateway, AI predictor stub, migration helper, plugin example,
Dockerfile and dev docker-compose to run the API locally.

## To test locally
1. Build & run:
   docker-compose -f docker-compose.phase9.yml up --build
2. Call:
   curl -X POST "http://localhost:8080/generate" -H "Content-Type: application/json" -d '{"input_data": {"sample":"data"}}'

## Next actions (after merging)
- Wire actual core function path in api.gateway to call internal code.
- Add JWT/OAuth auth in api.auth for production.
- Train model offline and place in `ai/models/compliance_model.pkl`.
- Create `billgenerator-mobile` repo for React Native.