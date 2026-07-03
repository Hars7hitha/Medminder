# MedMinder

MedMinder is an AI-powered medication coordination and safety agent system built for the Kaggle x Google AI Agents Intensive Capstone (2026). It helps elderly patients and their caregivers manage medications safely through natural language interaction.

The system checks for dangerous drug interactions before adding any new medication, maintains a daily schedule, generates privacy-filtered caregiver reports, and logs every action with a timestamp for accountability.

**Live demo:** https://medminder-np1u.onrender.com

---

## The Problem

Medication errors are one of the leading causes of harm in elderly and chronically ill patients. The average patient over 65 takes five or more medications daily, and dangerous drug interactions are frequently missed at the point of prescribing. MedMinder addresses this by putting a safety-first AI agent between the patient and their medication schedule.

---

## Architecture

```
User (natural language input)
          |
          v
Gemini 2.5 Flash (intent parser)
          |
          v
Orchestrator (routes to correct agent)
          |
    ------|------
    |     |     |
    v     v     v
Scheduler  Safety  Caregiver
Agent      Agent   Agent
    |         |
    v         v
patient_  openFDA
data.json  MCP Server
```

**Three-Agent System:**
- **Scheduler Agent** – Add, remove, and display medication schedules with dosage and timing
- **Safety Agent** – Calls openFDA and RxNorm APIs through MCP server to check drug-drug interactions; blocks unsafe additions
- **Caregiver Agent** – Generates privacy-filtered reports based on patient consent level

Every action is logged to `security/audit_log.json` with timestamp and user ID.

---

## Key Concepts

✅ **Multi-agent system using ADK** – Three independent agents coordinated by an orchestrator  
✅ **MCP Server** – Custom FastMCP server wrapping openFDA and RxNorm APIs  
✅ **Security features** – Consent-based access control and comprehensive audit logging  
✅ **Containerization** – Docker support for easy deployment  
✅ **Live deployment** – Running on Render

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Gemini 2.5 Flash |
| Agent Framework | Google ADK |
| Drug APIs | openFDA, RxNorm (free) |
| MCP | FastMCP |
| Web Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Docker, Render |

---

## Project Structure

```
medminder/
├── app.py                      # Flask web server
├── gemini_brain.py             # Natural language intent parser
├── orchestrator.py             # Routes intents to agents
├── run_adk.py                  # ADK CLI runner
├── Dockerfile                  # Container definition
├── requirements.txt            # Dependencies
├── agents/
│   ├── scheduler_agent.py      # Medication scheduling
│   ├── safety_agent.py         # Interaction checking
│   └── caregiver_agent.py      # Privacy-filtered reports
├── mcp_server/
│   ├── server.py               # FastMCP server
│   └── fda_tool.py             # API wrappers
├── adk_agents/
│   └── medminder_adk.py        # ADK agent definition
├── security/
│   ├── audit_log.py            # Action logging
│   └── consent.py              # Caregiver access control
├── data/
│   └── patient_data.json       # Patient profile
├── antigravity/
│   └── system_prompt.txt       # System prompt
└── templates/
    └── index.html              # Web UI
```

---

## Setup Instructions

**Prerequisites**
- Python 3.10+
- Google AI Studio API key (free at [aistudio.google.com](https://aistudio.google.com))
- Docker (optional)

**Local Setup**

```bash
git clone https://github.com/Hars7hitha/MedMinder
cd MedMinder

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Create `.env` in root:
```
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

**Run Web App**
```bash
python app.py
```
Open http://localhost:8080

**Run with ADK (CLI)**
```bash
python run_adk.py
```

**Run with Docker**
```bash
docker build -t medminder .
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key_here medminder
```

---

## Example Usage

```
User: what is my schedule today
MedMinder: Schedule for Mr. A - 2026-07-03
  08:00 -> Aspirin 100mg
  08:00 -> Metformin 500mg
  09:00 -> Lisinopril 10mg
  20:00 -> Metformin 500mg

User: is warfarin safe for me
MedMinder: Warfarin has interactions with existing medications.
Conflicts: Aspirin (bleeding risk)

User: show caregiver report
MedMinder: Patient ID: patient_001, Total Meds: 4, Next Dose: 20:00
(Full details restricted by consent level)
```

---

## Security

- No real patient data is stored
- API keys excluded via `.gitignore`
- Caregiver access controlled by consent flag
- Complete audit trail of all agent actions

---

## APIs Used

- [openFDA Drug Label API](https://api.fda.gov/drug/label.json) – Free, no auth required
- [RxNorm API](https://rxnav.nlm.nih.gov) – Free, no auth required

---

## License

MIT