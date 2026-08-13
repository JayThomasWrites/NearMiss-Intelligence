# NearMiss Intelligence

**AI-Assisted Safety and Organizational Learning**

NearMiss Intelligence is a portfolio prototype designed to turn near-miss reports into useful management information. It helps a user classify reported hazards, surface possible system contributors, check for recurrence, structure root-cause questions, review corrective actions, and create a short leadership brief.

## Core management question

> Is this an isolated event, or is it evidence of a larger system problem?

## Why this project exists

Near-miss reporting is often treated as an administrative safety function. This project explores a different approach: using near-miss data as operational intelligence. It is built around concepts including:

- leading and lagging indicators
- safety climate
- employee voice and psychological safety
- emotional intelligence and information flow
- corrective-action follow-through
- root-cause analysis
- organizational memory
- single-loop and double-loop learning

## Features in v1

1. Near-miss report intake
2. Hazard and potential-severity classification
3. Possible system-factor identification
4. Recurrence signal
5. Root-cause questions for human review
6. Corrective-action suggestions and verification prompts
7. Session-level leadership dashboard
8. Demo mode that runs without an API key
9. Optional OpenAI-powered analysis using the Responses API

## Run locally

```bash
python -m venv .venv
```

Activate the environment.

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

## Enable OpenAI mode

Create an API key and store it as an environment variable. Do **not** paste an API key directly into the source code.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
streamlit run app.py
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your-key"
streamlit run app.py
```

Optionally set a model:

```bash
export OPENAI_MODEL="gpt-5"
```

The prototype sends `store=False` with OpenAI Responses API calls.

## Deploy

A simple deployment path is Streamlit Community Cloud:

1. Put these files in a GitHub repository.
2. Create a Streamlit Community Cloud app from the repository.
3. Add `OPENAI_API_KEY` as a secret/environment variable if you want OpenAI mode enabled.
4. Use the public app URL as the project URL on Handshake AI Showcase.

## Privacy and safety

This is a portfolio prototype, not a production EHS system.

Do not enter:
- protected health information
- employee medical information
- Social Security numbers
- confidential HR data
- trade secrets
- sensitive incident evidence

A qualified human must determine actual hazard controls, regulatory obligations, investigation conclusions, and corrective actions.

## Suggested Handshake title

**NearMiss Intelligence: AI-Assisted Safety and Organizational Learning**

## Suggested Handshake description

NearMiss Intelligence is an AI-assisted decision-support prototype designed to help organizations turn near-miss reports into useful operational intelligence. The system analyzes reported events, identifies recurring hazards and possible system-level contributors, structures root-cause questions, reviews corrective actions, and produces concise management summaries. The project draws on safety management, organizational learning, psychological safety, root-cause analysis, and operational risk.

## Author

Jay Thomas
