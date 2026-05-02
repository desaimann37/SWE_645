# Design Document — Agentic AI Student Survey System
**Course:** SWE 645 — Extra Credit Assignment  
**Team:** Mann Desai, Tisha, Aakash, Yash  
**Date:** April 2026

---

## 1. Overview

This project extends a traditional CRUD Student Survey application into an Agentic AI system.
Users interact with the survey database through natural language via a chat interface. An AI agent
interprets each request, reasons about intent, calls the appropriate tools, and returns a
conversational response — without the user ever clicking a form or knowing which API was called.

**Architecture:**

```
React Chat UI  →  LangGraph Agent (Claude Haiku 4.5)  →  FastMCP Tool Server  →  MySQL RDS
   Pod 1                    Pod 2                               Pod 3              AWS RDS
```

---

## 2. LangGraph Graph Design

The agent is implemented as a compiled `StateGraph` using LangGraph. The graph has a single
entry point and fans out into four CRUD branches based on classified intent.

### State Object (`AgentState`)

The shared state passed between all nodes contains:

| Field | Purpose |
|-------|---------|
| `messages` | Full chat history (HumanMessage + AIMessage) |
| `user_query` | Latest user input |
| `intent` | Classified intent: create / read / update / delete / confirm / cancel / unknown |
| `draft_survey` | Partially built survey during multi-turn create flow |
| `missing_fields` | Fields still needed before create can execute |
| `target_survey_id` | Resolved survey ID for update/delete |
| `update_changes` | Extracted field changes for update |
| `awaiting` | Gate that pauses execution: `create_confirm`, `update_confirm`, `delete_confirm` |
| `last_tool_result` | Raw MCP response from the last tool call |
| `response_text` | Final message returned to the user |

### Graph Topology

```
START
  │
  ▼
[input]          ← extract latest user message
  │
  ▼
[intent]         ← LLM classifies: create / read / update / delete / confirm / cancel / unknown
  │
  ├──create──► [create_extract] → [create_ask_or_confirm] → [response]
  │                                        ↓ (after confirm)
  │                               [create_execute] → [response]
  │
  ├──read────► [read_execute] → [response]
  │
  ├──update──► [update_resolve] → [response]
  │                    ↓ (after confirm)
  │            [update_execute] → [response]
  │
  ├──delete──► [delete_resolve] → [response]
  │                    ↓ (after confirm)
  │            [delete_execute] → [response]
  │
  ├──confirm─► (re-routes to *_execute based on `awaiting` field)
  ├──cancel──► [cancel] → [response]
  └──unknown─► [unknown] → [response]
                               │
                               ▼
                              END
```

### Conditional Routing

The `_route_from_intent` function implements human-in-the-loop safety. When `awaiting` is set
(e.g., `delete_confirm`), a subsequent "yes" routes to `delete_execute`; anything else cancels.
This ensures destructive operations never execute without explicit user approval.

### Session State Management

State is kept per-session in an in-memory Python dict keyed by `session_id`. Each HTTP request
to `POST /agent/query` rehydrates the prior state, runs the graph, and saves the updated state
back. This is sufficient for per-session multi-turn conversation as required by the assignment.

---

## 3. Tools Implemented (FastMCP Tool Layer)

The backend (`backend/mcp_tools.py`) exposes a FastMCP server mounted at `/mcp`. The agent
connects to it via `langchain-mcp-adapters`. All tools return structured JSON.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `create_survey` | 12 required fields | Creates a new survey record and returns it with assigned ID |
| `list_surveys` | none | Returns all surveys in the database |
| `get_survey_by_id` | `survey_id: int` | Fetches one survey by its numeric ID |
| `search_surveys` | 9 optional filters | Case-insensitive partial-match search across name, city, state, liked_most, interested_via, recommend_likelihood, date range |
| `update_survey` | `survey_id` + any subset of 12 fields | Patches only the provided fields; leaves others unchanged |
| `delete_survey` | `survey_id: int` | Deletes survey and returns a snapshot of the deleted record |

All tools reuse the same SQLModel ORM models and database session used by the REST API,
ensuring a single source of truth for the database schema.

---

## 4. React Chat Interface

A new page, **AI Survey Assistant**, was added at route `/chat`. The layout matches the
suggested design from the assignment:

- **Left panel:** What-you-can-do list, required fields for create, clickable example prompt chips
- **Main chat panel:** Scrollable message thread with user/agent bubbles, real-time "Thinking..."
  indicator, Enter-to-send keyboard shortcut
- **Right panel:** Recent AI Actions log (tracks creates, updates, deletes, reads)

The component generates a UUID `session_id` on mount, posts every user message to
`POST /agent/query`, and renders the agent's reply. Multi-turn state (draft surveys,
pending confirmations) is handled entirely server-side via the session store.

---

## 5. Kubernetes & Helm Deployment

Three pods are deployed via a Helm chart (`helm/student-survey/`):

| Pod | Image | Service Type | Notes |
|-----|-------|-------------|-------|
| `student-survey-frontend` | React + Nginx | LoadBalancer (port 80) | Serves SPA including chat UI |
| `student-survey-agent` | FastAPI + LangGraph | ClusterIP (port 9000) | Reads `ANTHROPIC_API_KEY` from K8s Secret |
| `student-survey-backend` | FastAPI + FastMCP | ClusterIP (port 8000) | Reads `DATABASE_URL` from K8s Secret; connects to AWS RDS |

Kubernetes Secrets (`secrets.yaml`) store the Anthropic API key and database connection
string as base64-encoded values, injected as environment variables at pod startup.

**Deploy command:**
```bash
helm install survey ./helm/student-survey \
  --set secrets.anthropicApiKeyB64=$(echo -n 'sk-ant-...' | base64 -w 0) \
  --set secrets.databaseUrlB64=$(echo -n 'mysql+pymysql://...' | base64 -w 0)
```

---

## 6. Challenges Faced

### 1. MCP Tool Result Normalization
The `langchain-mcp-adapters` library returns tool results in three different formats depending
on the version: a plain `dict`, a JSON string, or a list of MCP content blocks
`[{"type": "text", "text": "..."}]`. A `_unwrap_tool_result()` utility was written to normalize
all three shapes before the agent nodes process them.

### 2. Multi-Turn Confirmation State
LangGraph graphs are stateless between invocations by design. Persisting the `awaiting` field
across HTTP requests (so a later "yes" correctly triggers `delete_execute` rather than
re-classifying the message as a new intent) required careful rehydration of the full state dict
from the in-memory session store on every call.

### 3. Vite Build-Time Environment Variables
Vite bakes `VITE_*` variables at build time, not runtime. For Docker Compose and Kubernetes,
the React app uses safe fallback values (`http://localhost:8000`, `http://localhost:9000`) which
work correctly when the browser accesses the exposed host ports.

### 4. FastMCP Lifespan Integration
Mounting the FastMCP sub-app inside FastAPI required wrapping both the REST API lifespan
and the MCP lifespan in a single `asynccontextmanager`, otherwise the MCP session manager
failed to initialize and tool calls returned connection errors.

### 5. Intent Ambiguity for Confirmations
User responses like "yes", "go ahead", or "sure" had to be classified as `confirm` intent
rather than triggering a new CRUD branch. This was handled by including `confirm` and `cancel`
as explicit intent classes in the LLM classification prompt, and by checking the `awaiting`
field before routing — so the graph always routes `confirm` to the correct pending operation.

---

## 7. Technologies Used

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, React Router, Axios, Vite, Nginx |
| Agent | LangGraph, LangChain, Claude Haiku 4.5 (Anthropic), FastAPI |
| MCP Tools | FastMCP 2.10+, langchain-mcp-adapters |
| Backend ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | MySQL 8 on AWS RDS |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes, Helm 3 |
