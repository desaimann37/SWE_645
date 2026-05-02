# Shared state that flows through every node in the LangGraph workflow.
# LangGraph passes this dict between nodes; nodes read fields they need
# and return partial updates.

from typing import Annotated, Optional, List, Dict, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


# Required fields for a complete survey (matches backend SurveyBase model)
REQUIRED_SURVEY_FIELDS = [
    "first_name",
    "last_name",
    "street_address",
    "city",
    "state",
    "zip",
    "telephone",
    "email",
    "date_of_survey",
    "liked_most",
    "interested_via",
    "recommend_likelihood",
]


Intent = Literal["create", "read", "update", "delete", "confirm", "cancel", "unknown"]


class AgentState(TypedDict, total=False):
    # Full chat history (user + assistant). LangGraph appends via add_messages.
    messages: Annotated[List[BaseMessage], add_messages]

    # The latest user input (for convenience — always == last user message)
    user_query: str

    # Classified intent for this turn
    intent: Intent

    # --- CREATE workflow state ---
    # Draft survey being built up over multiple turns
    draft_survey: Dict[str, Any]
    # Fields still missing before we can create
    missing_fields: List[str]
    # Whether user has confirmed the create
    create_confirmed: bool

    # --- READ workflow state ---
    read_filters: Dict[str, Any]

    # --- UPDATE workflow state ---
    target_survey_id: Optional[int]
    update_changes: Dict[str, Any]
    update_confirmed: bool

    # --- DELETE workflow state ---
    # (target_survey_id reused from update)
    delete_confirmed: bool

    # --- Workflow control ---
    # What the agent is currently awaiting from the user
    awaiting: Optional[Literal["create_fields", "create_confirm", "update_confirm", "delete_confirm"]]

    # Raw tool result from the last MCP call (for response formatting)
    last_tool_result: Optional[Dict[str, Any]]

    # Final text to send back to the user this turn
    response_text: str