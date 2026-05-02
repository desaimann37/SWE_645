# LangGraph node functions. Each node takes AgentState and returns a partial
# update to that state.
import json
import os
from datetime import date, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load .env BEFORE importing ChatAnthropic so the API key is available
# when the module-level LLM instance is created below.
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from .state import AgentState, REQUIRED_SURVEY_FIELDS
from .mcp_client import get_mcp_tools, get_tool_by_name
from .prompts import (
    INTENT_CLASSIFIER_PROMPT,
    CREATE_EXTRACTOR_PROMPT,
    READ_FILTER_EXTRACTOR_PROMPT,
    UPDATE_EXTRACTOR_PROMPT,
    DELETE_TARGET_EXTRACTOR_PROMPT,
    RESPONSE_FORMATTER_PROMPT,
)


# Shared LLM instance. Haiku is fast and strong enough for classification
# and extraction. Switch to Sonnet if you need higher reasoning quality.
LLM = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

def _unwrap_tool_result(result: Any) -> Dict[str, Any]:
    """MCP tools via langchain-mcp-adapters may return either:
      - a dict (ideal)
      - a JSON string
      - a list of MCP content blocks: [{'type': 'text', 'text': '...'}]
    Normalize all three into a plain dict.
    """
    # Already a dict
    if isinstance(result, dict):
        return result
    # List of content blocks
    if isinstance(result, list) and result:
        first = result[0]
        if isinstance(first, dict) and first.get("type") == "text":
            return _safe_json(first.get("text", ""))
        # Fallback: try to parse first item as string
        return _safe_json(str(first))
    # Plain string
    if isinstance(result, str):
        return _safe_json(result)
    # Anything else — stringify and try
    return _safe_json(str(result))

def _safe_json(text: str) -> Dict[str, Any]:
    """LLMs sometimes wrap JSON in code fences; strip them."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


# ----------------------------------------------------------------------
# 1. Input node — read the latest user message into user_query
# ----------------------------------------------------------------------

def input_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    last_user = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
        "",
    )
    return {"user_query": last_user}


# ----------------------------------------------------------------------
# 2. Intent classifier node
# ----------------------------------------------------------------------

def intent_node(state: AgentState) -> AgentState:
    awaiting = state.get("awaiting")
    awaiting_context = {
        "create_confirm": "confirming a create operation",
        "update_confirm": "confirming an update operation",
        "delete_confirm": "confirming a delete operation",
        "create_fields": "providing more fields for a new survey",
        None: "starting a new request",
    }.get(awaiting, "starting a new request")

    system = INTENT_CLASSIFIER_PROMPT.format(awaiting_context=awaiting_context)

    # If awaiting create_fields, treat ANY new info as continuation of create
    # (unless the user clearly cancels)
    if awaiting == "create_fields":
        # Quick keyword shortcut for cancel
        if any(w in state["user_query"].lower() for w in ["cancel", "stop", "never mind", "abort"]):
            return {"intent": "cancel"}
        return {"intent": "create"}

    resp = LLM.invoke([SystemMessage(content=system), HumanMessage(content=state["user_query"])])
    intent = resp.content.strip().lower().strip('".')
    if intent not in ("create", "read", "update", "delete", "confirm", "cancel", "unknown"):
        intent = "unknown"
    return {"intent": intent}


# ----------------------------------------------------------------------
# 3. CREATE workflow: extract fields, check missing, ask or confirm, create
# ----------------------------------------------------------------------

def create_extract_node(state: AgentState) -> AgentState:
    draft = state.get("draft_survey", {})
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    system = CREATE_EXTRACTOR_PROMPT.format(
        current_draft=json.dumps(draft),
        today=today,
        yesterday=yesterday,
    )
    resp = LLM.invoke([SystemMessage(content=system), HumanMessage(content=state["user_query"])])
    new_fields = _safe_json(resp.content)

    merged = {**draft, **{k: v for k, v in new_fields.items() if v is not None and v != ""}}
    missing = [f for f in REQUIRED_SURVEY_FIELDS if f not in merged or not merged[f]]
    return {"draft_survey": merged, "missing_fields": missing}


def create_ask_or_confirm_node(state: AgentState) -> AgentState:
    missing = state.get("missing_fields", [])
    draft = state.get("draft_survey", {})

    if missing:
        # Ask for missing fields
        friendly_names = {
            "first_name": "first name",
            "last_name": "last name",
            "street_address": "street address",
            "zip": "ZIP code",
            "telephone": "phone number",
            "date_of_survey": "date of the survey (YYYY-MM-DD)",
            "liked_most": "what they liked most (e.g. Dorms, Campus, Atmosphere, Sports)",
            "interested_via": "how they heard about the university (e.g. Friends, Internet, Television)",
            "recommend_likelihood": "recommendation likelihood (Very Likely, Likely, Neutral, Unlikely, Very Unlikely)",
        }
        asks = [friendly_names.get(f, f.replace("_", " ")) for f in missing[:5]]
        text = "I still need a few details to create this survey:\n- " + "\n- ".join(asks)
        if len(missing) > 5:
            text += f"\n...and {len(missing) - 5} more."
        return {
            "response_text": text,
            "awaiting": "create_fields",
        }

    # All fields collected — summarize and ask confirm
    summary_lines = [f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in draft.items()]
    text = (
        "Here's the survey I'm about to create:\n"
        + "\n".join(summary_lines)
        + "\n\nShould I go ahead and save it? (yes / no)"
    )
    return {
        "response_text": text,
        "awaiting": "create_confirm",
    }


async def create_execute_node(state: AgentState) -> AgentState:
    print(f"\n[create_execute_node] CALLED")
    print(f"[create_execute_node] draft_survey keys: {list(state.get('draft_survey', {}).keys())}")
    print(f"[create_execute_node] draft_survey: {state.get('draft_survey')}")
    tools = await get_mcp_tools()
    tool = get_tool_by_name(tools, "create_survey")
    try:
        result = await tool.ainvoke(state["draft_survey"])
        print(f"[create_execute_node] tool returned: {result}")
    except Exception as e:
        print(f"[create_execute_node] TOOL ERROR: {type(e).__name__}: {e}")
        raise
    result_dict = _unwrap_tool_result(result)
    return {
        "last_tool_result": result_dict,
        "draft_survey": {},
        "missing_fields": [],
        "awaiting": None,
        "create_confirmed": False,
    }

# ----------------------------------------------------------------------
# 4. READ workflow: extract filters, run search, format
# ----------------------------------------------------------------------

async def read_execute_node(state: AgentState) -> AgentState:
    system = READ_FILTER_EXTRACTOR_PROMPT.format(user_query=state["user_query"])
    resp = LLM.invoke([
        SystemMessage(content=system),
        HumanMessage(content=state["user_query"]),
    ])
    filters = _safe_json(resp.content)
    tools = await get_mcp_tools()
    if filters:
        tool = get_tool_by_name(tools, "search_surveys")
        result = await tool.ainvoke(filters)
    else:
        tool = get_tool_by_name(tools, "list_surveys")
        result = await tool.ainvoke({})

    result_dict = _unwrap_tool_result(result)
    return {"read_filters": filters, "last_tool_result": result_dict}


# ----------------------------------------------------------------------
# 5. UPDATE workflow: find target, extract changes, confirm, update
# ----------------------------------------------------------------------

async def update_resolve_node(state: AgentState) -> AgentState:
    system = UPDATE_EXTRACTOR_PROMPT.format(user_query=state["user_query"])
    resp = LLM.invoke([
        SystemMessage(content=system),
        HumanMessage(content=state["user_query"]),
    ])
    parsed = _safe_json(resp.content)
    target = parsed.get("target", {}) or {}
    changes = parsed.get("changes", {}) or {}

    tools = await get_mcp_tools()
    target_id = target.get("id")

    # If no explicit ID, try to find by name
    if target_id is None and (target.get("first_name") or target.get("last_name")):
        search = get_tool_by_name(tools, "search_surveys")
        search_args = {k: v for k, v in target.items() if k in ("first_name", "last_name") and v}
        search_result = await search.ainvoke(search_args)
        search_result = _unwrap_tool_result(search_result)
        surveys = search_result.get("surveys", [])
        if len(surveys) == 1:
            target_id = surveys[0]["id"]
        elif len(surveys) == 0:
            return {
                "response_text": f"I couldn't find a survey matching {target}. Can you give me the survey ID?",
                "awaiting": None,
            }
        else:
            lines = [f"- #{s['id']} {s['first_name']} {s['last_name']}" for s in surveys[:5]]
            return {
                "response_text": (
                    "I found multiple matching surveys. Which one do you mean? Please give me the ID:\n"
                    + "\n".join(lines)
                ),
                "awaiting": None,
            }

    if target_id is None:
        return {
            "response_text": "Which survey should I update? Please provide a name or ID.",
            "awaiting": None,
        }

    # Fetch full record for confirmation summary
    get_tool = get_tool_by_name(tools, "get_survey_by_id")
    full = await get_tool.ainvoke({"survey_id": target_id})
    full = _unwrap_tool_result(full)

    change_lines = [f"- **{k.replace('_',' ').title()}**: {v}" for k, v in changes.items()]
    text = (
        f"Found survey #{target_id} for {full.get('survey', {}).get('first_name', '')} "
        f"{full.get('survey', {}).get('last_name', '')}. I'll update:\n"
        + "\n".join(change_lines)
        + "\n\nProceed? (yes / no)"
    )
    return {
        "target_survey_id": target_id,
        "update_changes": changes,
        "response_text": text,
        "awaiting": "update_confirm",
    }


async def update_execute_node(state: AgentState) -> AgentState:
    tools = await get_mcp_tools()
    tool = get_tool_by_name(tools, "update_survey")
    args = {"survey_id": state["target_survey_id"], **state["update_changes"]}
    result = await tool.ainvoke(args)
    result_dict = _unwrap_tool_result(result)
    return {
        "last_tool_result": result_dict,
        "target_survey_id": None,
        "update_changes": {},
        "awaiting": None,
    }


# ----------------------------------------------------------------------
# 6. DELETE workflow: find target, show details, confirm, delete
# ----------------------------------------------------------------------

async def delete_resolve_node(state: AgentState) -> AgentState:
    system = DELETE_TARGET_EXTRACTOR_PROMPT.format(user_query=state["user_query"])
    resp = LLM.invoke([
        SystemMessage(content=system),
        HumanMessage(content=state["user_query"]),
    ])
    target = _safe_json(resp.content)

    tools = await get_mcp_tools()
    target_id = target.get("id")

    if target_id is None and (target.get("first_name") or target.get("last_name")):
        search = get_tool_by_name(tools, "search_surveys")
        search_args = {k: v for k, v in target.items() if k in ("first_name", "last_name") and v}
        search_result = await search.ainvoke(search_args)
        search_result = _unwrap_tool_result(search_result)
        surveys = search_result.get("surveys", [])
        if len(surveys) == 1:
            target_id = surveys[0]["id"]
        elif len(surveys) == 0:
            return {
                "response_text": f"No survey found for {target.get('first_name','')} {target.get('last_name','')}.",
                "awaiting": None,
            }
        else:
            lines = [f"- #{s['id']} {s['first_name']} {s['last_name']}" for s in surveys[:5]]
            return {
                "response_text": "Multiple matches — which ID?\n" + "\n".join(lines),
                "awaiting": None,
            }

    if target_id is None:
        return {
            "response_text": "Which survey should I delete? Please give me a name or ID.",
            "awaiting": None,
        }

    get_tool = get_tool_by_name(tools, "get_survey_by_id")
    full = await get_tool.ainvoke({"survey_id": target_id})
    full = _unwrap_tool_result(full)
    s = full.get("survey", {})

    text = (
        f"I found survey #{target_id}:\n"
        f"- Name: {s.get('first_name','')} {s.get('last_name','')}\n"
        f"- Email: {s.get('email','')}\n"
        f"- Date: {s.get('date_of_survey','')}\n"
        f"- Liked Most: {s.get('liked_most','')}\n\n"
        "Do you want me to delete it? (yes / no)"
    )
    return {
        "target_survey_id": target_id,
        "response_text": text,
        "awaiting": "delete_confirm",
    }


async def delete_execute_node(state: AgentState) -> AgentState:
    tools = await get_mcp_tools()
    tool = get_tool_by_name(tools, "delete_survey")
    result = await tool.ainvoke({"survey_id": state["target_survey_id"]})
    result_dict = _unwrap_tool_result(result)
    return {
        "last_tool_result": result_dict,
        "target_survey_id": None,
        "awaiting": None,
    }


# ----------------------------------------------------------------------
# 7. Cancel node
# ----------------------------------------------------------------------

def cancel_node(state: AgentState) -> AgentState:
    return {
        "response_text": "Okay, I've cancelled that. Anything else?",
        "draft_survey": {},
        "missing_fields": [],
        "target_survey_id": None,
        "update_changes": {},
        "awaiting": None,
    }


# ----------------------------------------------------------------------
# 8. Final response formatter
# ----------------------------------------------------------------------

def response_node(state: AgentState) -> AgentState:
    # If a node already set response_text (e.g. ask_missing, confirm prompt,
    # multiple-match dialog), use it as-is
    if state.get("response_text"):
        text = state["response_text"]
    else:
        # Format tool result via LLM
        system = RESPONSE_FORMATTER_PROMPT.format(
            user_query=state.get("user_query", ""),
            action=state.get("intent", ""),
            tool_result=json.dumps(state.get("last_tool_result", {}))[:4000],
        )
        resp = LLM.invoke([
            SystemMessage(content=system),
            HumanMessage(content="Please format the response now."),
        ])
        text = resp.content.strip()

    return {
        "response_text": text,
        "messages": [AIMessage(content=text)],
        # Clear last_tool_result so the next turn starts fresh
        "last_tool_result": None,
    }


# ----------------------------------------------------------------------
# 9. Unknown intent fallback
# ----------------------------------------------------------------------

def unknown_node(state: AgentState) -> AgentState:
    text = (
        "I can help you with student surveys. You can ask me to:\n"
        "- Create a new survey\n"
        "- Show or search existing surveys\n"
        "- Update a survey's details\n"
        "- Delete a survey\n\n"
        "What would you like to do?"
    )
    return {"response_text": text}