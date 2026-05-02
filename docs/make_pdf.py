from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted, Image
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

DOC = "design-document.pdf"
W, H = letter

doc = SimpleDocTemplate(
    DOC,
    pagesize=letter,
    leftMargin=1.1 * inch,
    rightMargin=1.1 * inch,
    topMargin=1.0 * inch,
    bottomMargin=1.0 * inch,
)

base = getSampleStyleSheet()

# ── Custom styles ──────────────────────────────────────────────────────────
title_style = ParagraphStyle(
    "DocTitle",
    parent=base["Title"],
    fontSize=20,
    leading=26,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=8,
    alignment=TA_CENTER,
)
subtitle_style = ParagraphStyle(
    "SubTitle",
    parent=base["Normal"],
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#444444"),
    spaceAfter=4,
    alignment=TA_CENTER,
)
meta_style = ParagraphStyle(
    "Meta",
    parent=base["Normal"],
    fontSize=10,
    leading=15,
    textColor=colors.HexColor("#555555"),
    spaceAfter=6,
    alignment=TA_CENTER,
)
h2_style = ParagraphStyle(
    "H2",
    parent=base["Heading2"],
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#1a1a2e"),
    spaceBefore=18,
    spaceAfter=6,
    borderPadding=(0, 0, 3, 0),
)
h3_style = ParagraphStyle(
    "H3",
    parent=base["Heading3"],
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#2c3e50"),
    spaceBefore=12,
    spaceAfter=4,
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle(
    "Body",
    parent=base["Normal"],
    fontSize=10.5,
    leading=16,
    spaceAfter=8,
    alignment=TA_JUSTIFY,
    fontName="Times-Roman",
)
code_style = ParagraphStyle(
    "Code",
    parent=base["Code"],
    fontSize=8.5,
    leading=12,
    fontName="Courier",
    backColor=colors.HexColor("#f5f5f5"),
    borderColor=colors.HexColor("#cccccc"),
    borderWidth=0.5,
    borderPadding=6,
    spaceBefore=6,
    spaceAfter=8,
)

TH_BG   = colors.HexColor("#2c3e50")
TH_FG   = colors.white
ROW_ALT = colors.HexColor("#f4f6f8")

def h2(text):
    return [
        Paragraph(text, h2_style),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cccccc"), spaceAfter=6),
    ]

def h3(text):
    return [Paragraph(text, h3_style)]

def p(text):
    return [Paragraph(text, body_style)]

def code(text):
    return [Preformatted(text, code_style)]

def spacer(n=8):
    return [Spacer(1, n)]

def mk_table(headers, rows, col_widths=None):
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle(
        "TH", parent=body_style, fontSize=10, textColor=TH_FG, fontName="Helvetica-Bold",
        alignment=TA_LEFT)) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, ParagraphStyle(
            "TD", parent=body_style, fontSize=9.5, leading=13)) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  TH_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  TH_FG),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ])
    t.setStyle(style)
    return [t, Spacer(1, 10)]

# ── Build content ──────────────────────────────────────────────────────────
story = []

# Cover
story += [
    Spacer(1, 0.6 * inch),
    Paragraph("Design Document", title_style),
    Paragraph("Agentic AI Extension of the Student Survey System", subtitle_style),
    Paragraph("Using LangGraph and FastMCP", subtitle_style),
    Spacer(1, 0.25 * inch),
    HRFlowable(width="60%", thickness=1.5, color=colors.HexColor("#2c3e50"), hAlign="CENTER"),
    Spacer(1, 0.2 * inch),
    Paragraph("Course: SWE 645 &mdash; Extra Credit Assignment", meta_style),
    Paragraph("Team: Mann Desai &nbsp;&nbsp;|&nbsp;&nbsp; Tisha &nbsp;&nbsp;|&nbsp;&nbsp; Aakash &nbsp;&nbsp;|&nbsp;&nbsp; Yash", meta_style),
    Paragraph("Date: April 2026", meta_style),
    Spacer(1, 0.5 * inch),
]

# ── Section 1 ──────────────────────────────────────────────────────────────
story += h2("1. Introduction")
story += p(
    "For this extra credit assignment, we took the Student Survey system we built in "
    "Homework 3 and added an AI-powered layer on top of it. The original system let users "
    "submit and manage surveys through a standard React form and a FastAPI REST backend. "
    "What we added here is a completely separate conversational interface so that a user "
    "can type something like <i>\"delete John Doe's survey\"</i> and the system will figure "
    "out what they mean, find the right record, ask for confirmation, and carry out the "
    "action — all without the user clicking through any forms."
)
story += p(
    "The core idea was to keep everything we already had intact and build the AI "
    "orchestration layer on top of it. We didn't rewrite the backend or touch the existing "
    "REST routes; we just exposed the same database operations as MCP tools so the agent "
    "could call them."
)
story += p("The overall architecture is shown in Figure 1 below:")
story += [
    Image("arch-diagram.png", width=6.0 * inch, height=3.5 * inch, hAlign="CENTER"),
    Paragraph("Figure 1 — System Architecture: three Kubernetes pods with LangGraph agent, FastMCP backend, and MySQL RDS.",
              ParagraphStyle("Caption", parent=base["Normal"], fontSize=8.5,
                             textColor=colors.HexColor("#6b7280"), alignment=1,
                             spaceAfter=10, spaceBefore=4, fontName="Times-Italic")),
]
story += p(
    "Each of those three pods is independently deployed on Kubernetes and managed via Helm "
    "charts. The agent communicates with the MCP backend over HTTP inside the cluster, and "
    "the React frontend talks to the agent through a simple REST endpoint we exposed at "
    "<font face='Courier' size=9>POST /agent/query</font>."
)

# ── Section 2 ──────────────────────────────────────────────────────────────
story += h2("2. LangGraph Graph Design")
story += p(
    "The agent is built as a LangGraph <font face='Courier' size=9>StateGraph</font>. "
    "We chose LangGraph because it lets you define exactly what happens at each step and "
    "how decisions are made, rather than relying on the LLM to figure all of that out on "
    "its own. For a system that can delete database records, that level of control matters."
)

story += h3("State Object")
story += p(
    "All the information the agent needs across a conversation is stored in a typed "
    "dictionary called <font face='Courier' size=9>AgentState</font>. "
    "The most important fields are:"
)
story += mk_table(
    ["Field", "What it holds"],
    [
        ["<font face='Courier' size=9>messages</font>", "Full chat history so the LLM has context"],
        ["<font face='Courier' size=9>intent</font>", "What the user wants: create / read / update / delete / confirm / cancel"],
        ["<font face='Courier' size=9>draft_survey</font>", "Partially filled survey during a multi-turn create flow"],
        ["<font face='Courier' size=9>missing_fields</font>", "Which fields the agent still needs to ask about"],
        ["<font face='Courier' size=9>target_survey_id</font>", "ID of the survey being updated or deleted"],
        ["<font face='Courier' size=9>update_changes</font>", "Specific fields to change in an update"],
        ["<font face='Courier' size=9>awaiting</font>", "Whether we're waiting for user confirmation before executing"],
        ["<font face='Courier' size=9>response_text</font>", "The final message to send back to the user"],
    ],
    col_widths=[2.0 * inch, 3.8 * inch],
)
story += p(
    "The <font face='Courier' size=9>awaiting</font> field is what makes the "
    "human-in-the-loop safety work. When the agent identifies a survey to delete and "
    "displays its details, it sets <font face='Courier' size=9>awaiting = \"delete_confirm\"</font> "
    "and returns to the user. On the next message, the router checks that field before doing "
    "anything — if the user said \"yes,\" it routes to "
    "<font face='Courier' size=9>delete_execute</font>; otherwise it cancels."
)

story += h3("Graph Topology")
story += [
    Image("langgraph-diagram.png", width=6.2 * inch, height=3.95 * inch, hAlign="CENTER"),
    Paragraph("Figure 2 — LangGraph workflow: intent classification routes into four CRUD branches, each with a confirmation gate before destructive operations.",
              ParagraphStyle("Caption", parent=base["Normal"], fontSize=8.5,
                             textColor=colors.HexColor("#6b7280"), alignment=1,
                             spaceAfter=10, spaceBefore=4, fontName="Times-Italic")),
]

story += h3("How Routing Works")
story += p(
    "After the intent node runs, a conditional edge function called "
    "<font face='Courier' size=9>_route_from_intent</font> decides where to go next. "
    "It first checks whether <font face='Courier' size=9>awaiting</font> is set — if the "
    "user just replied \"yes\" to a pending delete confirmation, it routes straight to "
    "<font face='Courier' size=9>delete_execute</font> regardless of how the LLM "
    "interpreted the word \"yes.\" That check takes priority over everything else. Only if "
    "there's no pending confirmation does it route based on the classified intent."
)

story += h3("Session Persistence")
story += p(
    "LangGraph graphs don't carry state between HTTP requests by themselves. We handle "
    "this with an in-memory Python dictionary keyed by "
    "<font face='Courier' size=9>session_id</font>. Every time the user sends a message, "
    "the server rehydrates the stored state, runs the graph, and saves the updated state "
    "back. It's simple and works well for a per-session conversation without needing a "
    "full external state store."
)

# ── Section 3 ──────────────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("3. MCP Tools Implemented")
story += p(
    "The tool layer lives in <font face='Courier' size=9>backend/mcp_tools.py</font> and "
    "is served by FastMCP, which is mounted as a sub-app inside our existing FastAPI backend "
    "at the path <font face='Courier' size=9>/mcp</font>. The agent connects to it using "
    "<font face='Courier' size=9>langchain-mcp-adapters</font>. "
    "We implemented all six tools the assignment required:"
)
story += mk_table(
    ["Tool", "Parameters", "What it does"],
    [
        ["<font face='Courier' size=9>create_survey</font>", "All 12 required fields", "Inserts a new survey and returns it with its assigned ID"],
        ["<font face='Courier' size=9>list_surveys</font>", "None", "Returns every survey record in the database"],
        ["<font face='Courier' size=9>get_survey_by_id</font>", "<font face='Courier' size=9>survey_id</font>", "Fetches a single survey by its numeric ID"],
        ["<font face='Courier' size=9>search_surveys</font>", "9 optional filters", "Case-insensitive partial-match search by name, city, state, liked_most, interested_via, recommendation, and date range"],
        ["<font face='Courier' size=9>update_survey</font>", "survey_id + any subset of fields", "Patches only the provided fields, leaves others unchanged"],
        ["<font face='Courier' size=9>delete_survey</font>", "<font face='Courier' size=9>survey_id</font>", "Deletes the survey and returns a snapshot of what was deleted"],
    ],
    col_widths=[1.6 * inch, 1.5 * inch, 2.7 * inch],
)
story += p(
    "All tools reuse the same SQLModel ORM session that the REST API uses, so there's "
    "one source of truth for the database schema. Each tool has a docstring describing its "
    "behavior — this matters because the LLM uses those descriptions to decide which "
    "tool to call."
)

# ── Section 4 ──────────────────────────────────────────────────────────────
story += h2("4. React Chat Interface")
story += p(
    "We added a new page called \"AI Survey Assistant\" to the existing React app, accessible "
    "from a new nav link. The layout follows the suggested design from the assignment spec, "
    "with three panels:"
)
story += p(
    "<b>Left panel</b> — explains what the agent can do, lists all the fields needed to "
    "create a survey, and includes eight clickable example prompts users can try without "
    "having to type anything."
)
story += p(
    "<b>Main chat area</b> — a scrollable message thread with user messages on the right "
    "(dark blue bubbles) and agent responses on the left (white bubbles). It shows a "
    "\"Thinking...\" indicator while waiting for the agent and supports Enter-to-send."
)
story += p(
    "<b>Right panel</b> — a small log of recent agent actions (created, updated, deleted, "
    "queried) so the user can track what's been done without scrolling back through the "
    "conversation."
)
story += p(
    "The component generates a UUID session ID when it first loads and sends it with "
    "every message. This is how the server knows which in-memory state to load for that "
    "conversation. Multi-turn state — like remembering we're halfway through collecting "
    "fields for a new survey — is handled entirely on the server side. The frontend just "
    "sends messages and renders responses."
)

# ── Section 5 ──────────────────────────────────────────────────────────────
story += h2("5. Kubernetes and Helm Deployment")
story += p(
    "We created a Helm chart at "
    "<font face='Courier' size=9>helm/student-survey/</font> that deploys the full "
    "system as three separate pods, matching exactly what the assignment requires:"
)
story += mk_table(
    ["Pod", "Image", "Service Type"],
    [
        ["Frontend (React + Nginx)", "<font face='Courier' size=9>student-survey-frontend</font>", "LoadBalancer — port 80"],
        ["Agent (LangGraph)", "<font face='Courier' size=9>student-survey-agent</font>", "ClusterIP — port 9000"],
        ["Backend (FastAPI + MCP)", "<font face='Courier' size=9>student-survey-backend</font>", "ClusterIP — port 8000"],
    ],
    col_widths=[1.9 * inch, 2.1 * inch, 1.8 * inch],
)
story += p(
    "Sensitive values — the Anthropic API key and the database connection string — are "
    "stored as Kubernetes Secrets and injected as environment variables at pod startup. "
    "No credentials are hardcoded anywhere in the Helm chart templates. The "
    "<font face='Courier' size=9>values.yaml</font> has placeholder fields for "
    "base64-encoded secrets that get passed in at deploy time via "
    "<font face='Courier' size=9>--set</font>."
)
story += p(
    "The agent deployment reads "
    "<font face='Courier' size=9>MCP_SERVER_URL</font> pointing to the backend "
    "service's cluster-internal DNS name, so all communication between the agent and "
    "the backend stays inside the cluster. Only the frontend is exposed externally "
    "through the LoadBalancer."
)

# ── Section 6 ──────────────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("6. Challenges We Ran Into")

story += h3("MCP Tool Result Format")
story += p(
    "This one took a while to figure out. Depending on the version of "
    "<font face='Courier' size=9>langchain-mcp-adapters</font>, the same tool call "
    "could return a plain Python dict, a JSON string, or a list of MCP content blocks "
    "that looked like "
    "<font face='Courier' size=9>[{\"type\": \"text\", \"text\": \"...\"}]</font>. "
    "The agent nodes were breaking because they expected a dict but kept getting a list. "
    "We ended up writing a small "
    "<font face='Courier' size=9>_unwrap_tool_result()</font> utility that normalizes "
    "all three formats before any node tries to read from the result."
)

story += h3("Keeping Confirmation State Across HTTP Requests")
story += p(
    "The trickiest part of the whole project was making multi-turn confirmation work "
    "reliably. When the agent says \"I found John Doe's survey. Do you want to delete it?\" "
    "and the user replies \"yes,\" the server receives a brand new HTTP request with no "
    "built-in memory. If we just ran intent classification on \"yes,\" it would come back "
    "as <font face='Courier' size=9>confirm</font> — but the router also needs to know "
    "it's confirming a <i>delete</i>, not a create or update. The fix was to save the "
    "<font face='Courier' size=9>awaiting</font> field in the session store and check it "
    "before routing, so the router always knows what confirmation is pending."
)

story += h3("FastMCP Lifespan Inside FastAPI")
story += p(
    "FastMCP requires its own lifespan context to initialize the MCP session manager. "
    "When we mounted it as a sub-app inside FastAPI, the session manager wasn't starting "
    "and every tool call was failing with a connection error. The fix was to nest the MCP "
    "lifespan inside our FastAPI lifespan using "
    "<font face='Courier' size=9>asynccontextmanager</font>, so both start up together. "
    "Once we figured that out it worked perfectly, but it wasn't obvious from the "
    "FastMCP docs."
)

story += h3("Intent Classification for Short Replies")
story += p(
    "Early on, when a user typed \"yes\" after a delete confirmation prompt, the LLM would "
    "sometimes classify it as <font face='Courier' size=9>unknown</font> or even "
    "<font face='Courier' size=9>create</font> depending on the conversation context. "
    "We fixed this by adding <font face='Courier' size=9>confirm</font> and "
    "<font face='Courier' size=9>cancel</font> as explicit intent classes in the "
    "classification prompt with worked examples, and by always routing based on "
    "<font face='Courier' size=9>awaiting</font> first before trusting the classifier."
)

story += h3("Vite Environment Variables at Build Time")
story += p(
    "We wanted to pass the agent URL into the React app via Docker Compose, but Vite "
    "bakes <font face='Courier' size=9>VITE_*</font> variables at image build time, not "
    "at container runtime. So environment variables set in "
    "<font face='Courier' size=9>docker-compose.yaml</font> under the frontend service "
    "don't actually get picked up. We resolved this by setting safe fallback values "
    "in the component code "
    "(<font face='Courier' size=9>http://localhost:8000</font> and "
    "<font face='Courier' size=9>http://localhost:9000</font>), which work correctly "
    "when running locally since those ports are exposed on the host."
)

# ── Section 7 ──────────────────────────────────────────────────────────────
story += h2("7. Tech Stack Summary")
story += mk_table(
    ["Layer", "Technology"],
    [
        ["Frontend",        "React 19, React Router, Axios, Vite, Nginx"],
        ["AI Agent",        "LangGraph, LangChain, Claude Haiku 4.5 (Anthropic), FastAPI"],
        ["Tool Server",     "FastMCP 2.10+, langchain-mcp-adapters"],
        ["Backend ORM",     "SQLModel (SQLAlchemy + Pydantic)"],
        ["Database",        "MySQL 8 on AWS RDS"],
        ["Containers",      "Docker, Docker Compose"],
        ["Orchestration",   "Kubernetes, Helm 3"],
    ],
    col_widths=[1.8 * inch, 4.0 * inch],
)

# ── Build PDF ──────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF saved to {DOC}")
