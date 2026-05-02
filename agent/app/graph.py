# LangGraph workflow wiring.
# Matches the candidate workflow in Section 11 of the assignment:
#   START -> input -> intent -> {create | read | update | delete | cancel | unknown}
#   create: extract -> ask_or_confirm -> [awaiting] OR execute -> response
#   read: execute -> response
#   update: resolve -> [awaiting] OR execute -> response
#   delete: resolve -> [awaiting] OR execute -> response

from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import (
    input_node,
    intent_node,
    create_extract_node,
    create_ask_or_confirm_node,
    create_execute_node,
    read_execute_node,
    update_resolve_node,
    update_execute_node,
    delete_resolve_node,
    delete_execute_node,
    cancel_node,
    unknown_node,
    response_node,
)


def _route_from_intent(state: AgentState) -> str:
    awaiting = state.get("awaiting")
    intent = state.get("intent")
    print(f"\n[route] intent={intent!r} awaiting={awaiting!r}")

    # Confirmation branch
    if awaiting == "create_confirm":
        return "create_execute" if intent == "confirm" else "cancel"
    if awaiting == "update_confirm":
        return "update_execute" if intent == "confirm" else "cancel"
    if awaiting == "delete_confirm":
        return "delete_execute" if intent == "confirm" else "cancel"

    # Normal routing
    if intent == "create":
        return "create_extract"
    if intent == "read":
        return "read_execute"
    if intent == "update":
        return "update_resolve"
    if intent == "delete":
        return "delete_resolve"
    if intent == "cancel":
        return "cancel"
    return "unknown"


def _route_after_create_extract(state: AgentState) -> str:
    """After extracting create fields, always ask or confirm."""
    return "create_ask_or_confirm"


def _route_after_create_ask(state: AgentState) -> str:
    """After ask_or_confirm, go to response (we're waiting for user)."""
    return "response"


def _route_after_resolve(state: AgentState) -> str:
    """After resolving update/delete target, go to response (waiting for confirm)."""
    return "response"


def build_graph():
    g = StateGraph(AgentState)

    # Register all nodes
    g.add_node("input", input_node)
    g.add_node("intent", intent_node)
    g.add_node("create_extract", create_extract_node)
    g.add_node("create_ask_or_confirm", create_ask_or_confirm_node)
    g.add_node("create_execute", create_execute_node)
    g.add_node("read_execute", read_execute_node)
    g.add_node("update_resolve", update_resolve_node)
    g.add_node("update_execute", update_execute_node)
    g.add_node("delete_resolve", delete_resolve_node)

    g.add_node("delete_execute", delete_execute_node)
    g.add_node("cancel", cancel_node)
    g.add_node("unknown", unknown_node)
    g.add_node("response", response_node)

    # Edges
    g.add_edge(START, "input")
    g.add_edge("input", "intent")

    # Conditional routing after intent
    g.add_conditional_edges(
        "intent",
        _route_from_intent,
        {
            "create_extract": "create_extract",
            "create_execute": "create_execute",
            "read_execute": "read_execute",
            "update_resolve": "update_resolve",
            "update_execute": "update_execute",
            "delete_resolve": "delete_resolve",
            "delete_execute": "delete_execute",
            "cancel": "cancel",
            "unknown": "unknown",
        },
    )

    # Create branch
    g.add_edge("create_extract", "create_ask_or_confirm")
    g.add_edge("create_ask_or_confirm", "response")
    g.add_edge("create_execute", "response")

    # Read branch
    g.add_edge("read_execute", "response")

    # Update branch
    g.add_edge("update_resolve", "response")
    g.add_edge("update_execute", "response")

    # Delete branch
    g.add_edge("delete_resolve", "response")
    g.add_edge("delete_execute", "response")

    # Cancel / unknown
    g.add_edge("cancel", "response")
    g.add_edge("unknown", "response")

    g.add_edge("response", END)

    return g.compile()


# Exposed module-level compiled graph
agent_graph = build_graph()