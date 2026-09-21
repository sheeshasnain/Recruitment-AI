# AI Recruitment & Interview Operations Agent

An end-to-end AI-powered recruitment operations platform that assists recruiters with candidate screening, structured interviews, scheduling, candidate communication, evaluation, and final hiring decisions.

The system combines **FastAPI**, **Streamlit**, **LangGraph/LangChain**, **Groq**, **Google Calendar**, **Gmail**, **LangSmith**, **SQLAlchemy**, **Alembic**, and **Docker**.

The platform follows a human-in-the-loop architecture:

> AI recommends and automates preparation; recruiters retain control over consequential actions and final hiring decisions.

---

## Features

### Candidate & Job Management

- Create and manage job openings
- Upload candidate resumes
- Parse PDF, DOCX, and TXT resumes
- Store candidate and application records
- Track application status throughout the recruitment lifecycle

### AI Candidate Screening

The Screening Agent analyzes candidate information against job requirements.

The LLM extracts semantic evidence while deterministic Python logic calculates the final score.

Scoring:

- Skills Match — 65%
- Experience — 35%

Screening routes:

- `shortlist`
- `manual_review`
- `reject`

The AI screening result is a recommendation only. A recruiter must approve a candidate before interview preparation.

### Structured Interview Operations

The Interview Preparation Agent generates structured interview questions based on the candidate and job.

The platform supports:

- Interview preparation
- Interview start/completion lifecycle
- Structured questions
- Candidate answer recording
- AI-generated follow-up questions
- Interview evaluation

Evaluation dimensions:

- Technical
- Problem Solving
- Experience
- Communication

Final evaluation scoring is calculated deterministically from the AI-generated evidence.

### Human Recruiter Decisions

Human approval gates are used before consequential actions.

Recruiters control:

- Candidate interview approval
- Schedule approval
- Candidate email approval
- Final hiring decision

Final decisions:

- Hire
- Reject
- Hold

The AI does not make the final hiring decision.

### Interview Scheduling

The Scheduling Agent prepares interview scheduling information.

After recruiter approval, the Google Calendar integration can:

- Create Calendar events
- Invite candidates
- Generate Google Meet links
- Store event information
- Record external tool actions

### Candidate Communication

The Communication Agent generates candidate email drafts.

Recruiters can:

- Review drafts
- Edit subject/body
- Approve delivery
- Reject drafts

Only approved emails are sent through Gmail.

### Observability & Audit Trail

The project includes multiple observability layers:

**LangSmith**

Used for LLM/agent tracing.

**Application Logging**

Used for backend and workflow diagnostics.

**Tool Action Logs**

External actions such as Google Calendar and Gmail operations are recorded in the database.

---

## System Architecture

```text
                         Recruiter
                            |
                            v
                    +----------------+
                    | Streamlit UI   |
                    +----------------+
                            |
                            v
                    +----------------+
                    | FastAPI API    |
                    +----------------+
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
   Recruitment         AI Agents         Recruiter
   Services            / LangGraph       Approval Gates
          |                 |
          |                 v
          |             Groq LLM
          |
          +-----------------+-----------------+
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          Google Calendar            Gmail
                 |                     |
                 +----------+----------+
                            |
                            v
                     Tool Audit Logs

                    SQLAlchemy / SQLite
                            |
                         Alembic

                    LangSmith Tracing
```

---

## Recruitment Workflow

```text
Job Created
    |
Candidate Resume Uploaded
    |
Resume Parsing
    |
Candidate Application
    |
AI Intake & Screening
    |
Deterministic Scoring
    |
Recruiter Review
    |
Recruiter Approves Interview
    |
Interview Preparation Agent
    |
Structured Interview
    |
Candidate Answers
    |
AI Follow-up Questions
    |
Interview Completion
    |
Evaluation Agent
    |
Deterministic Evaluation Score
    |
Recruiter Final Review
    |
Hire / Reject / Hold
```

Scheduling and candidate communication operate through separate human-approval workflows before Google Calendar or Gmail side effects occur.

---

## Technology Stack

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

### Frontend

- Streamlit
- Pandas

### AI / Agents

- Groq
- LangChain
- LangGraph
- LangSmith

### External Integrations

- Google Calendar API
- Gmail API

### Resume Processing

- PyMuPDF
- python-docx

### Infrastructure

- Docker
- Docker Compose
- Docker Hub

---

## Project Structure

```text
.
├── backend/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── tools/
│   └── main.py
│
├── frontend/
│   ├── pages/
│   ├── api_client.py
│   └── app.py
│
├── migrations/
│   └── versions/
│
├── tests/
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── backend-entrypoint.sh
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

# Running the Project with Docker

## Prerequisites

Install:

- Docker
- Docker Compose

Clone the repository:

```bash
git clone https://github.com/sheeshasnain/Recruitment-AI.git
cd <YOUR_REPOSITORY_DIRECTORY>
```

---

## Environment Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required environment variables.

Example:

```env
APP_NAME=Recruitment AI
APP_ENV=development
DEBUG=true

DATABASE_URL=sqlite:///./data/recruitment.db

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=AI Recruitment Agent
```

Never commit `.env` to source control.

---

# Google API Configuration

The scheduling and communication integrations require Google OAuth credentials.

Enable:

- Google Calendar API
- Gmail API

Create an OAuth Desktop application through Google Cloud Console.

Place the OAuth credentials file in the project root as:

```text
credentials.json
```

After completing OAuth authorization, the application uses:

```text
token.json
```

Required scopes:

```text
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/gmail.send
```

Both files are intentionally excluded from Git and Docker images.

---

## Start the Application

Build and start both containers:

```bash
docker compose up --build -d
```

Check container status:

```bash
docker compose ps
```

The backend health status should eventually show:

```text
healthy
```

---

## Access the Application

Streamlit:

```text
http://localhost:8501
```

FastAPI:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/health
```

---

## Database Migrations

Database migrations run automatically when the backend container starts.

The backend startup sequence is:

```text
Container Start
      |
      v
alembic upgrade head
      |
      v
FastAPI / Uvicorn
```

To check the current migration manually:

```bash
docker compose exec backend alembic current
```

---

# Docker Hub Images

Prebuilt images are available on Docker Hub:

Backend:

```text
sheeshasnain/recruitment-ai-backend:latest
```

Frontend:

```text
sheeshasnain/recruitment-ai-frontend:latest
```

The Docker images intentionally contain no API keys, OAuth credentials, OAuth tokens, or `.env` files.

---

# Security

The project follows several security practices:

- API keys are stored in environment variables
- `.env` is excluded from Git
- Google OAuth credentials are excluded from Git
- OAuth tokens are excluded from Git
- Secrets are not embedded in Docker images
- External actions require human approval
- OAuth tokens are never written to application audit logs
- Tool actions are logged without exposing authentication secrets

---

# Human-in-the-Loop Design

The platform intentionally separates AI recommendations from recruiter decisions.

The AI can:

- Analyze resumes
- Generate screening evidence
- Generate interview questions
- Generate follow-up questions
- Evaluate interview evidence
- Draft schedules
- Draft candidate communications

A human recruiter controls:

- Interview approval
- Calendar event approval
- Email delivery approval
- Final hiring decision

This ensures the system supports recruitment operations without delegating final employment decisions to the AI.

---

# Testing

The application has been tested through the complete recruitment lifecycle:

```text
Job Creation
     ↓
Candidate Upload
     ↓
AI Screening
     ↓
Recruiter Approval
     ↓
Interview Preparation
     ↓
Interview
     ↓
Follow-up Questions
     ↓
Evaluation
     ↓
Scheduling
     ↓
Google Calendar
     ↓
Candidate Communication
     ↓
Gmail
     ↓
Final Recruiter Decision
     ↓
Audit Logs
```

Docker testing includes:

- Backend health checks
- Frontend-to-backend communication
- Database migrations
- SQLite volume persistence
- Groq connectivity
- Google OAuth authentication
- Google Calendar API connectivity
- Gmail send authorization
- Secret exclusion verification

---

# API Documentation

When the backend is running, interactive API documentation is available at:

```text
http://localhost:8000/docs
```

Primary API areas include:

- Jobs
- Candidates
- Applications
- Recruiter decisions
- Interviews
- Scheduling
- Communications
- Tool audit logs

---

# Observability

LangSmith can be enabled with:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=AI Recruitment Agent
```

This provides tracing for LLM and agent execution.

External Calendar and Gmail actions are separately recorded through the application's tool audit log.

---

# Docker Submission

This project supports container-based evaluation.

After configuring `.env`, `credentials.json`, and Google OAuth, the complete application can be started with:

```bash
docker compose up --build -d
```

Then open:

```text
http://localhost:8501
```

---

## Author

AI Recruitment & Interview Operations Agent

Built as an end-to-end agentic recruitment operations project.
