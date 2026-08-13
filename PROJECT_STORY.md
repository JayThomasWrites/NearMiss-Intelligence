# NearMiss Intelligence: Project Story

## Problem

Organizations can collect near-miss reports without actually learning from them. A report may be documented, assigned, and closed while the underlying exposure remains. Low reporting counts can also create false confidence when employees have learned that speaking up produces little response.

## Design thesis

Near-miss reports should be treated as operational intelligence.

The prototype asks three questions:

1. What almost happened?
2. What possible system conditions contributed?
3. What should management learn before the same exposure produces a loss?

## Human-centered AI design

The AI is intentionally framed as decision support rather than an automated safety authority.

It:
- separates observations from hypotheses
- avoids declaring a root cause from one narrative
- asks questions before assigning blame
- surfaces possible system contributors
- highlights recurrence
- creates management summaries
- recommends verification of corrective actions

A human remains responsible for investigation, controls, compliance, and final decisions.

## Portfolio talking points

- Designed from an operations-management perspective rather than as a generic chatbot.
- Connects AI analysis to leading indicators, corrective action, organizational learning, and reporting culture.
- Includes transparent demo logic and an optional LLM-powered analysis layer.
- Uses structured output so the AI response can populate repeatable management fields.
- Designed with privacy warnings and explicit human-review boundaries.

## Future roadmap

### v1.1
- persistent SQLite database
- corrective-action due dates and status
- CSV upload
- trend filters by department and location
- downloadable leadership brief

### v1.2
- semantic similarity for recurrence detection
- risk matrix
- role-based access
- verification workflow
- audit history

### v2
- multi-site dashboards
- organization-specific taxonomy
- integration with EHS or work-order systems
- anonymization / PII redaction
- evaluation dataset and accuracy benchmarks
