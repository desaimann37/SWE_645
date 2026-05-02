# FastAPI wrapper that exposes the LangGraph agent as a REST endpoint.
# The React chat UI will POST to /agent/query.

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from .graph import agent_graph

load_dotenv()

app = FastAPI(title="Student Survey AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory per-session state store. Enough for this assignment.
# Keyed by session_id sent from the frontend.
_SESSIONS: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class QueryRequest(BaseModel):
    session_id: str
    message: str


class QueryResponse(BaseModel):
    session_id: str
    reply: str
    awaiting: Optional[str] = None
    last_tool_result: Optional[Dict[str, Any]] = None


def _rehydrate_messages(history: List[Dict[str, str]]) -> List[BaseMessage]:
    out: List[BaseMessage] = []
    for m in history:
        if m["role"] == "user":
            out.append(HumanMessage(content=m["content"]))
        else:
            out.append(AIMessage(content=m["content"]))
    return out


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agent/query", response_model=QueryResponse)
async def agent_query(req: QueryRequest):
    session = _SESSIONS.get(req.session_id, {})

    # --- DEBUG ---
    print(f"\n========== [/agent/query] session={req.session_id!r} ==========")
    print(f"[LOAD] _SESSIONS has keys: {list(_SESSIONS.keys())}")
    print(f"[LOAD] loaded session.awaiting = {session.get('awaiting')!r}")
    print(f"[LOAD] loaded session.draft_survey = {session.get('draft_survey', {})}")
    print(f"[LOAD] user message: {req.message!r}")
    # --- /DEBUG ---

    history: List[Dict[str, str]] = session.get("history", [])
    history.append({"role": "user", "content": req.message})

    incoming_state = {
        "messages": _rehydrate_messages(history),
        "draft_survey": session.get("draft_survey", {}),
        "missing_fields": session.get("missing_fields", []),
        "target_survey_id": session.get("target_survey_id"),
        "update_changes": session.get("update_changes", {}),
        "awaiting": session.get("awaiting"),
    }

    final_state = await agent_graph.ainvoke(incoming_state)

    reply = final_state.get("response_text", "Sorry, something went wrong.")
    history.append({"role": "assistant", "content": reply})

    _SESSIONS[req.session_id] = {
        "history": history,
        "draft_survey": final_state.get("draft_survey", {}),
        "missing_fields": final_state.get("missing_fields", []),
        "target_survey_id": final_state.get("target_survey_id"),
        "update_changes": final_state.get("update_changes", {}),
        "awaiting": final_state.get("awaiting"),
    }

    # --- DEBUG ---
    print(f"[SAVE] final_state.awaiting = {final_state.get('awaiting')!r}")
    print(f"[SAVE] final_state.draft_survey keys: {list(final_state.get('draft_survey', {}).keys())}")
    print(f"[SAVE] _SESSIONS now has keys: {list(_SESSIONS.keys())}")
    print(f"========================================================\n")
    # --- /DEBUG ---

    return QueryResponse(
        session_id=req.session_id,
        reply=reply,
        awaiting=final_state.get("awaiting"),
        last_tool_result=final_state.get("last_tool_result"),
    )

@app.delete("/agent/session/{session_id}")
def reset_session(session_id: str):
    _SESSIONS.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}