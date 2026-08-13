import os
import json
import re
from datetime import date
import pandas as pd
import streamlit as st

APP_TITLE = "NearMiss Intelligence"
APP_SUBTITLE = "AI-Assisted Safety and Organizational Learning"

st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)
st.write(
    "Turn near-miss reports into operational intelligence. "
    "Analyze risk signals, surface possible system contributors, track corrective actions, "
    "and create a concise leadership brief."
)

with st.expander("Important use note", expanded=False):
    st.write(
        "This prototype is a decision-support tool. It does not replace a competent safety "
        "professional, required incident investigations, regulatory reporting, or site-specific "
        "hazard controls. Do not enter personal health information, confidential employee data, "
        "or other sensitive information into a public demo."
    )

# -----------------------------
# Session state
# -----------------------------
if "reports" not in st.session_state:
    st.session_state.reports = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

HAZARD_KEYWORDS = {
    "Vehicle / Mobile Equipment": ["vehicle", "forklift", "truck", "backed", "backing", "traffic", "loader", "cart"],
    "Slip / Trip / Fall": ["fall", "slip", "trip", "ladder", "stair", "wet floor", "edge"],
    "Equipment / Machinery": ["machine", "equipment", "guard", "tool", "jammed", "conveyor"],
    "Electrical": ["electrical", "wire", "outlet", "breaker", "shock", "cord"],
    "Fire / Emergency": ["fire", "smoke", "alarm", "extinguisher", "evacuation"],
    "Material Handling": ["shelf", "rack", "load", "lifting", "stack", "pallet"],
    "Sanitation / Environmental": ["sanitation", "spill", "chemical", "waste", "cleaning", "leak"],
    "Behavioral / Security": ["threat", "aggressive", "security", "violence", "conflict"],
}

SYSTEM_KEYWORDS = {
    "Training": ["training", "not trained", "new employee", "procedure"],
    "Equipment": ["broken", "damaged", "malfunction", "guard", "maintenance"],
    "Environment": ["lighting", "dark", "wet", "noise", "visibility", "weather", "clutter"],
    "Workflow / Process": ["workflow", "route", "process", "shortcut", "procedure", "handoff"],
    "Staffing / Workload": ["staffing", "short staffed", "overtime", "fatigue", "rushed", "workload"],
    "Supervision": ["supervisor", "foreman", "manager", "oversight"],
    "Communication": ["communication", "did not know", "not told", "handoff", "warning"],
    "Policy / Control": ["policy", "inspection", "control", "corrective action", "prior report"],
}

SEVERITY_TERMS = {
    "High": ["struck", "crushed", "fall from", "electrocution", "explosion", "fire", "vehicle", "forklift", "collapse", "chemical exposure"],
    "Medium": ["slip", "trip", "cut", "sprain", "collision", "spill", "damaged equipment"],
}

def detect_category(text: str) -> str:
    lower = text.lower()
    scores = {}
    for cat, words in HAZARD_KEYWORDS.items():
        scores[cat] = sum(1 for w in words if w in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] else "Other / Needs Review"

def detect_system_factors(text: str):
    lower = text.lower()
    factors = []
    for factor, words in SYSTEM_KEYWORDS.items():
        if any(w in lower for w in words):
            factors.append(factor)
    if not factors:
        factors = ["Needs investigation"]
    return factors[:5]

def detect_potential_severity(text: str) -> str:
    lower = text.lower()
    for sev, terms in SEVERITY_TERMS.items():
        if any(t in lower for t in terms):
            return sev
    return "Low to Medium"

def demo_analyze(report_text, location, department, prior_reports):
    category = detect_category(report_text)
    factors = detect_system_factors(report_text)
    severity = detect_potential_severity(report_text)

    # recurrence check across saved reports
    recurrence_matches = []
    for r in prior_reports:
        if r.get("hazard_category") == category and (not location or r.get("location") == location):
            recurrence_matches.append(r)

    recurrence = "Possible recurrence" if recurrence_matches else "No matching prior report in current demo data"
    primary_factor = factors[0]

    questions = [
        "Has a similar event or hazard been reported before?",
        "What changed in the environment, workflow, staffing, equipment, or supervision before the event?",
        "Was a prior corrective action assigned, completed, and verified?",
        "Could the same condition exist in another department, shift, or location?",
        "Does the initial explanation focus on individual behavior while overlooking system conditions?",
    ]

    actions = [
        {
            "action": f"Verify and control the immediate {category.lower()} hazard.",
            "owner": "Operations / Safety",
            "priority": "High" if severity == "High" else "Medium",
            "verification": "Document hazard removal or control and confirm effectiveness."
        },
        {
            "action": f"Review possible contributing factor: {primary_factor}.",
            "owner": "Responsible manager",
            "priority": "Medium",
            "verification": "Record evidence reviewed and any control changes."
        },
        {
            "action": "Check prior reports and corrective actions for recurrence or incomplete closure.",
            "owner": "Safety / Quality",
            "priority": "Medium",
            "verification": "Compare current event with prior reports and confirm lesson transfer."
        }
    ]

    return {
        "hazard_category": category,
        "potential_severity": severity,
        "system_factors": factors,
        "recurrence_signal": recurrence,
        "management_summary": (
            f"This near miss is categorized as {category} with {severity.lower()} potential severity. "
            f"Possible system contributors include {', '.join(factors)}. "
            f"{recurrence}. Management should verify the immediate control, review whether the first explanation "
            "captures the full operating context, and confirm that any corrective action is assigned, completed, and verified."
        ),
        "root_cause_questions": questions,
        "corrective_actions": actions,
        "learning_review": (
            "Treat the report as a weak signal. Determine whether this is an isolated event, a repeat exposure, "
            "or evidence of a broader process condition. If the same type of event has occurred before, investigate "
            "why the organization did not learn from the earlier report."
        )
    }

def ai_analyze(report_text, location, department, prior_reports):
    try:
        from openai import OpenAI
    except Exception:
        raise RuntimeError("The OpenAI package is not installed. Run: pip install -r requirements.txt")

    client = OpenAI()

    prior_context = [
        {
            "date": r.get("date"),
            "location": r.get("location"),
            "department": r.get("department"),
            "hazard_category": r.get("hazard_category"),
            "summary": r.get("management_summary"),
        }
        for r in prior_reports[-10:]
    ]

    schema = {
        "type": "object",
        "properties": {
            "hazard_category": {"type": "string"},
            "potential_severity": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
            "system_factors": {"type": "array", "items": {"type": "string"}},
            "recurrence_signal": {"type": "string"},
            "management_summary": {"type": "string"},
            "root_cause_questions": {"type": "array", "items": {"type": "string"}},
            "corrective_actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "owner": {"type": "string"},
                        "priority": {"type": "string"},
                        "verification": {"type": "string"}
                    },
                    "required": ["action", "owner", "priority", "verification"],
                    "additionalProperties": False
                }
            },
            "learning_review": {"type": "string"}
        },
        "required": [
            "hazard_category", "potential_severity", "system_factors", "recurrence_signal",
            "management_summary", "root_cause_questions", "corrective_actions", "learning_review"
        ],
        "additionalProperties": False
    }

    instructions = """
You are the analytical engine for NearMiss Intelligence, a safety and organizational-learning prototype.

Analyze near-miss reports as management information, not as a substitute for a formal investigation.
Distinguish observed facts from hypotheses. Do not assert a root cause from one narrative.
Look for potential system contributors across training, equipment, environment, workflow, staffing,
supervision, communication, policy, and prior corrective actions.

A key management question is:
"Is this an isolated event, or is it evidence of a larger system problem?"

Use neutral, non-blaming language. Preserve accountability for deliberate misconduct or reckless behavior,
but do not default to individual blame when system contributors may exist.

Corrective actions must be framed as actions for human review, not authoritative safety instructions.
Do not invent laws, regulations, measurements, or site conditions.
"""

    user_payload = {
        "report": report_text,
        "location": location,
        "department": department,
        "recent_reports_for_pattern_check": prior_context
    }

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5"),
        instructions=instructions,
        input=json.dumps(user_payload),
        text={
            "format": {
                "type": "json_schema",
                "name": "near_miss_analysis",
                "schema": schema,
                "strict": True
            }
        },
        store=False
    )
    return json.loads(response.output_text)

# -----------------------------
# Sidebar / mode
# -----------------------------
st.sidebar.header("Analysis mode")
api_available = bool(os.getenv("OPENAI_API_KEY"))
default_mode = 1 if api_available else 0
mode = st.sidebar.radio(
    "Choose mode",
    ["Demo mode", "OpenAI mode"],
    index=default_mode,
    help="Demo mode uses transparent rules. OpenAI mode uses the OpenAI Responses API."
)

if mode == "OpenAI mode" and not api_available:
    st.sidebar.warning("Set OPENAI_API_KEY in your environment or Streamlit secrets before using OpenAI mode.")

st.sidebar.divider()
st.sidebar.metric("Reports in session", len(st.session_state.reports))
if st.sidebar.button("Clear session data"):
    st.session_state.reports = []
    st.session_state.analysis_result = None
    st.rerun()

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Report Intake", "2. Analysis", "3. Corrective Actions", "4. Leadership Brief"]
)

with tab1:
    st.subheader("Near-Miss Report Intake")
    col1, col2, col3 = st.columns(3)
    with col1:
        report_date = st.date_input("Date", value=date.today())
    with col2:
        location = st.text_input("Location", placeholder="e.g., Loading Dock A")
    with col3:
        department = st.text_input("Department / Workgroup", placeholder="e.g., Facilities")

    report_text = st.text_area(
        "Describe what almost happened",
        height=180,
        placeholder=(
            "Example: An employee stepped into the loading area as a delivery vehicle backed toward the dock. "
            "The employee stopped before entering the vehicle's path. The driver reported limited visibility "
            "because temporary storage had been placed near the corner."
        )
    )

    sample = (
        "An employee stepped into the loading area as a delivery vehicle backed toward the dock. "
        "The employee stopped before entering the vehicle's path. The driver reported limited visibility "
        "because temporary storage had been placed near the corner. Staff said the travel route had changed "
        "earlier in the week but no new warning signs had been installed."
    )
    if st.button("Load sample report"):
        st.session_state["sample_text"] = sample
        st.rerun()

    if "sample_text" in st.session_state and not report_text:
        st.info("Sample text loaded. Copy it into the report box above:\n\n" + st.session_state["sample_text"])

    analyze = st.button("Analyze near miss", type="primary", use_container_width=True)

    if analyze:
        if len(report_text.strip()) < 30:
            st.error("Enter a fuller near-miss description before analysis.")
        else:
            try:
                if mode == "OpenAI mode":
                    if not api_available:
                        st.error("OPENAI_API_KEY is not configured.")
                        st.stop()
                    result = ai_analyze(report_text, location, department, st.session_state.reports)
                else:
                    result = demo_analyze(report_text, location, department, st.session_state.reports)

                result["date"] = str(report_date)
                result["location"] = location
                result["department"] = department
                result["report_text"] = report_text
                st.session_state.analysis_result = result
                st.session_state.reports.append(result)
                st.success("Analysis complete. Open the Analysis tab.")
            except Exception as e:
                st.error(f"Analysis failed: {e}")

with tab2:
    st.subheader("Operational Intelligence Review")
    result = st.session_state.analysis_result
    if not result:
        st.info("Analyze a report first.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Hazard category", result["hazard_category"])
        c2.metric("Potential severity", result["potential_severity"])
        c3.metric("Recurrence signal", result["recurrence_signal"])

        st.markdown("### Management summary")
        st.write(result["management_summary"])

        st.markdown("### Possible system contributors")
        for item in result["system_factors"]:
            st.write(f"• {item}")

        st.markdown("### Root-cause questions for human review")
        for q in result["root_cause_questions"]:
            st.write(f"• {q}")

        st.markdown("### Organizational learning review")
        st.write(result["learning_review"])

with tab3:
    st.subheader("Corrective-Action Review")
    result = st.session_state.analysis_result
    if not result:
        st.info("Analyze a report first.")
    else:
        actions = pd.DataFrame(result["corrective_actions"])
        st.dataframe(actions, use_container_width=True, hide_index=True)

        st.caption(
            "Suggested actions are decision-support prompts. A qualified human should determine actual controls, "
            "responsibilities, deadlines, and verification requirements."
        )

with tab4:
    st.subheader("Leadership Brief")
    if not st.session_state.reports:
        st.info("Add at least one report.")
    else:
        df = pd.DataFrame(st.session_state.reports)
        st.metric("Near misses reviewed", len(df))

        if "hazard_category" in df:
            st.markdown("### Reports by category")
            st.bar_chart(df["hazard_category"].value_counts())

        high_count = int(df["potential_severity"].isin(["High", "Critical"]).sum())
        st.metric("High / critical potential", high_count)

        latest = st.session_state.reports[-1]
        st.markdown("### Latest management brief")
        st.write(latest["management_summary"])

        st.markdown("### Leadership questions")
        st.write("• Which hazards are recurring?")
        st.write("• Which corrective actions are being closed without verified risk reduction?")
        st.write("• Where is reporting volume unusually low, and does that reflect lower exposure or lower willingness to report?")
        st.write("• Which lessons need to move across departments, shifts, or locations?")
        st.write("• Are managers receiving bad news early enough to act before the organization pays the full cost of failure?")

st.divider()
st.caption(
    "NearMiss Intelligence | Prototype by Jay Thomas | AI-Assisted Safety and Organizational Learning"
)
