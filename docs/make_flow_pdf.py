from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUT = "flow-document.pdf"
W, H = letter

doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=1.1 * inch,
    rightMargin=1.1 * inch,
    topMargin=1.0 * inch,
    bottomMargin=1.0 * inch,
)

base = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle", parent=base["Title"],
    fontSize=22, leading=28,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=8, alignment=TA_CENTER,
)
subtitle_style = ParagraphStyle(
    "SubTitle", parent=base["Normal"],
    fontSize=12, leading=16,
    textColor=colors.HexColor("#444444"),
    spaceAfter=4, alignment=TA_CENTER,
)
meta_style = ParagraphStyle(
    "Meta", parent=base["Normal"],
    fontSize=10, leading=15,
    textColor=colors.HexColor("#555555"),
    spaceAfter=6, alignment=TA_CENTER,
)
h2_style = ParagraphStyle(
    "H2", parent=base["Heading2"],
    fontSize=13, leading=17,
    textColor=colors.HexColor("#1a1a2e"),
    spaceBefore=20, spaceAfter=6,
)
h3_style = ParagraphStyle(
    "H3", parent=base["Heading3"],
    fontSize=11, leading=14,
    textColor=colors.HexColor("#2c3e50"),
    spaceBefore=14, spaceAfter=4,
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle(
    "Body", parent=base["Normal"],
    fontSize=10.5, leading=16,
    spaceAfter=8, alignment=TA_JUSTIFY,
    fontName="Times-Roman",
)
code_style = ParagraphStyle(
    "Code", parent=base["Code"],
    fontSize=8.2, leading=12,
    fontName="Courier",
    backColor=colors.HexColor("#f5f5f5"),
    borderColor=colors.HexColor("#cccccc"),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=6, spaceAfter=8,
)
note_style = ParagraphStyle(
    "Note", parent=base["Normal"],
    fontSize=9.5, leading=14,
    fontName="Times-Italic",
    textColor=colors.HexColor("#555555"),
    spaceAfter=8,
    leftIndent=12,
)

TH_BG   = colors.HexColor("#2c3e50")
TH_FG   = colors.white
ROW_ALT = colors.HexColor("#f4f6f8")


def h2(text):
    return [
        Paragraph(text, h2_style),
        HRFlowable(width="100%", thickness=0.8,
                   color=colors.HexColor("#cccccc"), spaceAfter=6),
    ]

def h3(text):
    return [Paragraph(text, h3_style)]

def p(text):
    return [Paragraph(text, body_style)]

def note(text):
    return [Paragraph(f"<i>{text}</i>", note_style)]

def code(text):
    return [Preformatted(text, code_style)]

def spacer(n=8):
    return [Spacer(1, n)]

def mk_table(headers, rows, col_widths=None):
    th_para = ParagraphStyle(
        "TH", parent=body_style, fontSize=9.5,
        textColor=TH_FG, fontName="Helvetica-Bold", alignment=TA_LEFT,
    )
    td_para = ParagraphStyle(
        "TD", parent=body_style, fontSize=9.2, leading=13,
    )
    data = [[Paragraph(f"<b>{h}</b>", th_para) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, td_para) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  TH_BG),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  TH_FG),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]))
    return [t, Spacer(1, 10)]

def step_banner(num, label):
    banner_style = ParagraphStyle(
        "Banner", parent=base["Normal"],
        fontSize=10.5, leading=14,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        backColor=colors.HexColor("#003366"),
        borderPadding=(5, 8, 5, 8),
        spaceBefore=14, spaceAfter=4,
    )
    return [Paragraph(f"  Step {num} — {label}", banner_style)]


# ── Story ──────────────────────────────────────────────────────────────────
story = []

# ── Cover ──────────────────────────────────────────────────────────────────
story += [
    Spacer(1, 0.7 * inch),
    Paragraph("Full Request Flow", title_style),
    Paragraph("User Types → LangGraph → MCP → Response", subtitle_style),
    Spacer(1, 0.2 * inch),
    HRFlowable(width="60%", thickness=1.5,
               color=colors.HexColor("#2c3e50"), hAlign="CENTER"),
    Spacer(1, 0.2 * inch),
    Paragraph("Course: SWE 645 — Agentic AI Extension", meta_style),
    Paragraph("Student Survey System", meta_style),
    Paragraph("Date: April 2026", meta_style),
    Spacer(1, 0.5 * inch),
]

# ── Overview ───────────────────────────────────────────────────────────────
story += h2("Overview")
story += p(
    "This document traces every hop a user message makes from the moment it is typed "
    "in the React chat UI through the LangGraph agent and MCP tool layer, all the way "
    "to the database — and back. We use a concrete, worked example throughout: "
    "<b>\"Delete John Doe's survey\"</b> followed by the user confirming with "
    "<b>\"yes\"</b>. This covers the most complete path (two HTTP round-trips, two LLM "
    "calls, two MCP tool calls) so all the moving parts are visible."
)

story += mk_table(
    ["Layer", "Technology", "Port"],
    [
        ["React chat UI",      "React 19, Axios",                       "3000 (browser)"],
        ["AI Agent",           "FastAPI + LangGraph + Claude Haiku 4.5", "9000"],
        ["MCP Tool Server",    "FastAPI + FastMCP 2.10",                 "8000 /mcp"],
        ["REST API",           "FastAPI (same process as MCP server)",   "8000 /surveys"],
        ["Database",           "SQLite (dev) / MySQL RDS (prod)",        "n/a"],
    ],
    col_widths=[1.7*inch, 2.6*inch, 1.5*inch],
)

# ── Architecture text diagram ───────────────────────────────────────────────
story += h2("Architecture at a Glance")
story += code(
    "  [Browser]\n"
    "      │  POST /agent/query  {session_id, message}\n"
    "      ▼\n"
    "  [Agent Service  :9000]  (FastAPI wrapper around LangGraph)\n"
    "      │  agent_graph.ainvoke(AgentState)\n"
    "      ▼\n"
    "  [LangGraph Graph]\n"
    "      START\n"
    "        → input_node          reads user_query from messages\n"
    "        → intent_node         LLM → classify intent\n"
    "        → <branch>_node(s)    per-intent logic, calls MCP tools\n"
    "        → response_node       format final reply\n"
    "      END\n"
    "      │  (some nodes make HTTP calls to MCP)\n"
    "      ▼\n"
    "  [Backend Service  :8000/mcp]  (FastMCP server)\n"
    "      │  runs Python tool function, hits DB\n"
    "      ▼\n"
    "  [SQLite / MySQL RDS]\n"
    "      │\n"
    "      └─ JSON result flows back up through MCP → LangGraph → FastAPI → Browser"
)

# ── Turn 1 ─────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("Turn 1: \"Delete John Doe's survey\"")

# Step 1
story += step_banner(1, "React UI — HTTP POST to Agent")
story += p(
    "The user types the message and presses Enter (or Send). "
    "<font face='Courier' size=9>AISurveyAssistant.jsx</font> calls:"
)
story += code(
    "axios.post(`${AGENT_URL}/agent/query`, {\n"
    "  session_id: 'sess-abc123',   // UUID generated when tab opened\n"
    "  message:    \"Delete John Doe's survey\"\n"
    "})"
)
story += note(
    "File: frontend/src/components/AISurveyAssistant.jsx — line 47. "
    "AGENT_URL = http://localhost:9000 in dev, or the K8s Service DNS in prod."
)

# Step 2
story += step_banner(2, "FastAPI (Agent) — Load Session, Build AgentState")
story += p(
    "The <font face='Courier' size=9>POST /agent/query</font> endpoint in "
    "<font face='Courier' size=9>agent/app/main.py</font> runs. It looks up "
    "<font face='Courier' size=9>_SESSIONS[session_id]</font>. On the first "
    "turn this is empty. It assembles the typed state dict that LangGraph will receive:"
)
story += code(
    "incoming_state = {\n"
    "    'messages':         [HumanMessage('Delete John Doe\\'s survey')],\n"
    "    'draft_survey':     {},\n"
    "    'missing_fields':   [],\n"
    "    'target_survey_id': None,\n"
    "    'update_changes':   {},\n"
    "    'awaiting':         None,   # nothing pending from a previous turn\n"
    "}"
)
story += p(
    "It then calls the compiled LangGraph graph and awaits the result:"
)
story += code(
    "final_state = await agent_graph.ainvoke(incoming_state)"
)
story += note(
    "File: agent/app/main.py — line 64. "
    "Everything below happens inside this single await."
)

# Step 3
story += step_banner(3, "LangGraph — input_node")
story += p(
    "<font face='Courier' size=9>input_node</font> is the first node after START. "
    "It scans the messages list for the latest "
    "<font face='Courier' size=9>HumanMessage</font> and copies its text into "
    "<font face='Courier' size=9>user_query</font> for convenience:"
)
story += code(
    "def input_node(state: AgentState) -> AgentState:\n"
    "    last_user = next(\n"
    "        (m.content for m in reversed(state['messages'])\n"
    "         if isinstance(m, HumanMessage)), ''\n"
    "    )\n"
    "    return {'user_query': last_user}\n"
    "# state['user_query'] = \"Delete John Doe's survey\""
)
story += note("File: agent/app/nodes.py — line 74.")

# Step 4
story += step_banner(4, "LangGraph — intent_node (LLM Call #1)")
story += p(
    "<font face='Courier' size=9>intent_node</font> invokes Claude Haiku 4.5 with a "
    "system prompt that lists the seven valid intents. Because "
    "<font face='Courier' size=9>state['awaiting']</font> is "
    "<font face='Courier' size=9>None</font>, the context is "
    "<i>\"starting a new request.\"</i>"
)
story += code(
    "System:\n"
    "  \"Classify into: create / read / update / delete / confirm / cancel / unknown.\n"
    "   Context: the user is starting a new request.\n"
    "   Respond with ONLY the intent word.\"\n"
    "\n"
    "User: \"Delete John Doe's survey\"\n"
    "\n"
    "Claude Haiku responds: \"delete\"\n"
    "\n"
    "→  state['intent'] = 'delete'"
)
story += note("File: agent/app/nodes.py — line 87. Prompt: agent/app/prompts.py — INTENT_CLASSIFIER_PROMPT.")

# Step 5
story += step_banner(5, "LangGraph — Router: _route_from_intent")
story += p(
    "The conditional edge function checks "
    "<font face='Courier' size=9>awaiting</font> first (it is "
    "<font face='Courier' size=9>None</font>), then "
    "<font face='Courier' size=9>intent</font>:"
)
story += code(
    "def _route_from_intent(state):\n"
    "    awaiting = state.get('awaiting')   # None\n"
    "    intent   = state.get('intent')     # 'delete'\n"
    "    if intent == 'delete':\n"
    "        return 'delete_resolve'        # ← chosen branch"
)
story += note("File: agent/app/graph.py — line 28.")

# Step 6
story += step_banner(6, "LangGraph — delete_resolve_node (LLM Call #2 + MCP Calls #1 & #2)")
story += p(
    "This is the busiest node. It runs three sub-steps:"
)
story += h3("6a — LLM extracts target from message")
story += code(
    "System: \"Identify the target survey by ID or by name.\"\n"
    "User:   \"Delete John Doe's survey\"\n"
    "\n"
    "Claude responds:\n"
    "{\"id\": null, \"first_name\": \"John\", \"last_name\": \"Doe\"}"
)
story += h3("6b — MCP Call #1: search_surveys")
story += p(
    "No ID was provided, so the node searches by name. "
    "<font face='Courier' size=9>get_mcp_tools()</font> connects to "
    "<font face='Courier' size=9>http://backend:8000/mcp</font> via the MCP "
    "streamable-HTTP transport and fetches all available tool definitions "
    "(this is cached after the first call):"
)
story += code(
    "tools  = await get_mcp_tools()              # MCP handshake / cache hit\n"
    "tool   = get_tool_by_name(tools, 'search_surveys')\n"
    "result = await tool.ainvoke({'first_name': 'John', 'last_name': 'Doe'})\n"
    "\n"
    "# HTTP request goes to backend:8000/mcp\n"
    "# Backend runs: SELECT * FROM survey WHERE first_name ILIKE '%John%'\n"
    "#                                     AND last_name  ILIKE '%Doe%'\n"
    "# Returns: {\"status\": \"success\", \"count\": 1,\n"
    "#           \"surveys\": [{\"id\": 7, \"first_name\": \"John\", ...}]}"
)
story += h3("6c — MCP Call #2: get_survey_by_id")
story += p(
    "Exactly one match → target_id = 7. The node fetches the full record "
    "so it can show the user what will be deleted:"
)
story += code(
    "tool = get_tool_by_name(tools, 'get_survey_by_id')\n"
    "full = await tool.ainvoke({'survey_id': 7})\n"
    "# Returns full row: name, email, address, date_of_survey, liked_most, ..."
)
story += h3("6d — Build confirmation message, set awaiting")
story += code(
    "return {\n"
    "    'target_survey_id': 7,\n"
    "    'response_text': (\n"
    "        'I found survey #7:\\n'\n"
    "        '- Name: John Doe\\n'\n"
    "        '- Email: john@example.com\\n'\n"
    "        '- Date: 2025-03-15\\n\\n'\n"
    "        'Do you want me to delete it? (yes / no)'\n"
    "    ),\n"
    "    'awaiting': 'delete_confirm',   # ← key for next turn\n"
    "}"
)
story += note("File: agent/app/nodes.py — line 304. MCP client: agent/app/mcp_client.py.")

# Step 7
story += step_banner(7, "LangGraph — response_node")
story += p(
    "<font face='Courier' size=9>response_text</font> is already populated by "
    "<font face='Courier' size=9>delete_resolve_node</font>, so "
    "<font face='Courier' size=9>response_node</font> passes it through unchanged "
    "and appends it as an "
    "<font face='Courier' size=9>AIMessage</font> to the message history."
)
story += code(
    "def response_node(state):\n"
    "    if state.get('response_text'):\n"
    "        text = state['response_text']   # use as-is\n"
    "    else:\n"
    "        text = LLM.invoke(...)           # format tool result via LLM\n"
    "    return {'response_text': text,\n"
    "            'messages': [AIMessage(content=text)]}"
)
story += note("File: agent/app/nodes.py — line 392.")

# Step 8
story += step_banner(8, "FastAPI (Agent) — Save Session, Return HTTP Response")
story += p(
    "Control returns to <font face='Courier' size=9>main.py</font>. The "
    "updated state is saved to "
    "<font face='Courier' size=9>_SESSIONS</font> so the next turn can resume "
    "where this one left off:"
)
story += code(
    "_SESSIONS['sess-abc123'] = {\n"
    "    'history':          [...],\n"
    "    'target_survey_id': 7,\n"
    "    'awaiting':         'delete_confirm',   # persisted!\n"
    "    'draft_survey':     {},\n"
    "    ...\n"
    "}"
)
story += p("The HTTP response sent back to the browser:")
story += code(
    "{\n"
    "  \"session_id\": \"sess-abc123\",\n"
    "  \"reply\":      \"I found survey #7:\\n- Name: John Doe\\n...\\n\"\n"
    "                  \"Do you want me to delete it? (yes / no)\",\n"
    "  \"awaiting\":   \"delete_confirm\"\n"
    "}"
)
story += note("File: agent/app/main.py — line 92.")

# ── Turn 2 ─────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("Turn 2: \"yes\" (Confirmation)")

story += step_banner(9, "React UI — HTTP POST with \"yes\"")
story += p(
    "The agent's question is displayed in the chat bubble. The user types "
    "<b>\"yes\"</b> and sends. The same "
    "<font face='Courier' size=9>session_id</font> is sent again:"
)
story += code(
    "axios.post(`${AGENT_URL}/agent/query`, {\n"
    "  session_id: 'sess-abc123',\n"
    "  message:    'yes'\n"
    "})"
)

story += step_banner(10, "FastAPI (Agent) — Reload Session")
story += p(
    "The endpoint loads the saved session. This is what makes stateful "
    "multi-turn conversation work across stateless HTTP:"
)
story += code(
    "session = _SESSIONS['sess-abc123']\n"
    "# session['awaiting']         == 'delete_confirm'\n"
    "# session['target_survey_id'] == 7\n"
    "\n"
    "incoming_state = {\n"
    "    'messages':         [..., HumanMessage('yes')],\n"
    "    'awaiting':         'delete_confirm',\n"
    "    'target_survey_id': 7,\n"
    "    ...\n"
    "}"
)

story += step_banner(11, "LangGraph — input_node + intent_node (LLM Call #3)")
story += p(
    "<font face='Courier' size=9>input_node</font> sets "
    "<font face='Courier' size=9>user_query = 'yes'</font>. "
    "<font face='Courier' size=9>intent_node</font> sees "
    "<font face='Courier' size=9>awaiting = 'delete_confirm'</font> and passes "
    "that as context to the classifier prompt:"
)
story += code(
    "System: \"Context: the user is confirming a delete operation.\"\n"
    "User:   \"yes\"\n"
    "\n"
    "Claude responds: \"confirm\"\n"
    "\n"
    "→  state['intent'] = 'confirm'"
)

story += step_banner(12, "LangGraph — Router: awaiting takes priority")
story += p(
    "The router checks "
    "<font face='Courier' size=9>awaiting</font> before "
    "<font face='Courier' size=9>intent</font>. This is intentional — "
    "it avoids any ambiguity if the LLM misclassifies a short reply:"
)
story += code(
    "def _route_from_intent(state):\n"
    "    awaiting = state.get('awaiting')   # 'delete_confirm'\n"
    "    intent   = state.get('intent')     # 'confirm'\n"
    "\n"
    "    if awaiting == 'delete_confirm':\n"
    "        return 'delete_execute' if intent == 'confirm' else 'cancel'\n"
    "    # → 'delete_execute'"
)

story += step_banner(13, "LangGraph — delete_execute_node (MCP Call #3)")
story += p(
    "The final destructive operation. The node uses the already-resolved "
    "<font face='Courier' size=9>target_survey_id</font> from state:"
)
story += code(
    "async def delete_execute_node(state):\n"
    "    tools  = await get_mcp_tools()\n"
    "    tool   = get_tool_by_name(tools, 'delete_survey')\n"
    "    result = await tool.ainvoke({'survey_id': 7})"
)
story += p(
    "The MCP call hits the backend at "
    "<font face='Courier' size=9>http://backend:8000/mcp</font>. "
    "FastMCP dispatches to the registered "
    "<font face='Courier' size=9>delete_survey</font> Python function:"
)
story += code(
    "# backend/mcp_tools.py — delete_survey(survey_id=7)\n"
    "with Session(engine) as session:\n"
    "    survey         = session.get(Survey, 7)\n"
    "    deleted_snapshot = _serialize(survey)\n"
    "    session.delete(survey)\n"
    "    session.commit()\n"
    "    return {'status': 'success', 'deleted': deleted_snapshot}"
)
story += p(
    "Result comes back to the node:"
)
story += code(
    "result_dict = {'status': 'success',\n"
    "               'deleted': {'id': 7, 'first_name': 'John', 'last_name': 'Doe', ...}}\n"
    "\n"
    "return {\n"
    "    'last_tool_result': result_dict,\n"
    "    'target_survey_id': None,    # cleared\n"
    "    'awaiting':         None,    # cleared\n"
    "}"
)
story += note("File: agent/app/nodes.py — line 361. Tool definition: backend/mcp_tools.py — line 220.")

story += step_banner(14, "LangGraph — response_node (LLM Call #4)")
story += p(
    "This time <font face='Courier' size=9>response_text</font> is not set, "
    "so <font face='Courier' size=9>response_node</font> asks the LLM to "
    "format the raw tool result into a friendly reply:"
)
story += code(
    "System:\n"
    "  \"You are a friendly survey assistant. Format the following as a concise reply.\n"
    "   User asked: 'yes'\n"
    "   Action: delete\n"
    "   Tool result: {\\\"status\\\": \\\"success\\\", \\\"deleted\\\": {\\\"id\\\": 7, ...}}\"\n"
    "\n"
    "Claude responds:\n"
    "  \"Done! I've deleted John Doe's survey (ID #7). Is there anything else I can help you with?\""
)
story += note("Prompt: agent/app/prompts.py — RESPONSE_FORMATTER_PROMPT.")

story += step_banner(15, "FastAPI (Agent) — Clear State, Return Final Reply")
story += code(
    "_SESSIONS['sess-abc123'] = {\n"
    "    'history':          [...],\n"
    "    'target_survey_id': None,      # cleared\n"
    "    'awaiting':         None,      # cleared\n"
    "    ...\n"
    "}\n"
    "\n"
    "# HTTP response:\n"
    "{\n"
    "  \"session_id\": \"sess-abc123\",\n"
    "  \"reply\":      \"Done! I've deleted John Doe's survey (ID #7)...\",\n"
    "  \"awaiting\":   null\n"
    "}"
)

# ── Summary table ───────────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("Complete Step Summary")

story += mk_table(
    ["Step", "Node / Layer", "What happens", "LLM / MCP?"],
    [
        ["1",  "React UI",              "User types; axios POSTs to :9000/agent/query",           "—"],
        ["2",  "FastAPI (Agent)",       "Load session, build AgentState, call ainvoke()",          "—"],
        ["3",  "input_node",            "Extract user_query from messages list",                   "—"],
        ["4",  "intent_node",           "Classify intent: 'delete'",                               "LLM #1"],
        ["5",  "Router",                "awaiting=None + intent=delete → delete_resolve",          "—"],
        ["6a", "delete_resolve_node",   "LLM extracts {first_name, last_name} from message",       "LLM #2"],
        ["6b", "delete_resolve_node",   "MCP: search_surveys → finds survey id=7",                 "MCP #1"],
        ["6c", "delete_resolve_node",   "MCP: get_survey_by_id(7) → full record",                  "MCP #2"],
        ["6d", "delete_resolve_node",   "Build confirmation text, set awaiting=delete_confirm",    "—"],
        ["7",  "response_node",         "Pass response_text through, append AIMessage",            "—"],
        ["8",  "FastAPI (Agent)",       "Save session (awaiting persisted), return HTTP reply",    "—"],
        ["9",  "React UI",              "Show reply; user types 'yes', axios POSTs again",         "—"],
        ["10", "FastAPI (Agent)",       "Reload session: awaiting=delete_confirm, id=7",           "—"],
        ["11", "intent_node",           "Classify 'yes' in context of pending delete → confirm",   "LLM #3"],
        ["12", "Router",                "awaiting=delete_confirm + confirm → delete_execute",      "—"],
        ["13", "delete_execute_node",   "MCP: delete_survey(7) → DB row removed",                  "MCP #3"],
        ["14", "response_node",         "LLM formats tool result into friendly message",           "LLM #4"],
        ["15", "FastAPI (Agent)",       "Clear session state, return final HTTP reply",            "—"],
    ],
    col_widths=[0.4*inch, 1.5*inch, 2.8*inch, 0.9*inch],
)

# ── Key Concepts ────────────────────────────────────────────────────────────
story += h2("Key Design Decisions Explained")

story += h3("Why awaiting is checked before intent in the router")
story += p(
    "Short replies like \"yes\" or \"no\" can be ambiguous without context. By saving "
    "<font face='Courier' size=9>awaiting</font> in the session and checking it first, "
    "the router never needs to trust that the LLM correctly interprets a one-word reply. "
    "Even if the classifier returns 'unknown' for 'yes', the "
    "<font face='Courier' size=9>awaiting == 'delete_confirm'</font> branch would route "
    "to cancel — a safe fallback."
)

story += h3("Why MCP tools are cached after the first call")
story += p(
    "<font face='Courier' size=9>get_mcp_tools()</font> in "
    "<font face='Courier' size=9>mcp_client.py</font> stores the tool list in a "
    "module-level variable after the first HTTP handshake with the backend MCP server. "
    "Every subsequent call in the same process lifetime gets the cached list instantly. "
    "This avoids a round-trip on every single node invocation."
)

story += h3("Why the agent has its own FastAPI process separate from the backend")
story += p(
    "The backend runs the MCP server and the REST API. The agent runs LangGraph and "
    "calls those MCP tools. Keeping them in separate containers means each can be scaled "
    "independently, restarted without affecting the other, and deployed with its own "
    "resource limits and secrets. In the Helm chart, the agent pod gets the Anthropic "
    "API key while the backend pod gets only the database URL."
)

story += h3("How session state survives across stateless HTTP")
story += p(
    "LangGraph itself has no built-in persistence across invocations. The "
    "<font face='Courier' size=9>_SESSIONS</font> dict in "
    "<font face='Courier' size=9>agent/app/main.py</font> is an in-process store "
    "keyed by <font face='Courier' size=9>session_id</font> (a UUID the React component "
    "generates on first load). On every request, the endpoint loads the saved fields "
    "(awaiting, draft_survey, target_survey_id, update_changes, history) into the "
    "incoming AgentState, runs the graph, then saves the output fields back. This is "
    "enough for a single-replica deployment. For multi-replica, this would be replaced "
    "with Redis or a similar shared store."
)

# ── MCP tool reference ──────────────────────────────────────────────────────
story += [PageBreak()]
story += h2("MCP Tools Reference")
story += p(
    "All six tools are defined in "
    "<font face='Courier' size=9>backend/mcp_tools.py</font> and served at "
    "<font face='Courier' size=9>http://backend:8000/mcp</font> via FastMCP."
)
story += mk_table(
    ["Tool name", "Key parameters", "Used by node(s)"],
    [
        ["<font face='Courier' size=9>create_survey</font>",    "All 12 required survey fields",           "<font face='Courier' size=9>create_execute_node</font>"],
        ["<font face='Courier' size=9>list_surveys</font>",     "None",                                    "<font face='Courier' size=9>read_execute_node</font>"],
        ["<font face='Courier' size=9>get_survey_by_id</font>", "<font face='Courier' size=9>survey_id</font>",     "<font face='Courier' size=9>update_resolve_node, delete_resolve_node</font>"],
        ["<font face='Courier' size=9>search_surveys</font>",   "9 optional filters (name, city, date…)",  "<font face='Courier' size=9>read_execute_node, update_resolve_node, delete_resolve_node</font>"],
        ["<font face='Courier' size=9>update_survey</font>",    "<font face='Courier' size=9>survey_id</font> + any subset of fields", "<font face='Courier' size=9>update_execute_node</font>"],
        ["<font face='Courier' size=9>delete_survey</font>",    "<font face='Courier' size=9>survey_id</font>",                        "<font face='Courier' size=9>delete_execute_node</font>"],
    ],
    col_widths=[1.6*inch, 2.2*inch, 2.0*inch],
)

story += p(
    "The tools are discovered by the agent via the MCP protocol handshake "
    "(<font face='Courier' size=9>MultiServerMCPClient.get_tools()</font>). "
    "Each tool's Python docstring becomes the description the LLM reads when "
    "the agent decides which tool to call. No manual registration is needed in "
    "the agent code — adding a new "
    "<font face='Courier' size=9>@mcp.tool()</font> in the backend automatically "
    "makes it available to the agent on the next process start."
)

# ── Build PDF ───────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF saved to {OUT}")
