from typing import Any

from app.state import AgentState


def add_trace(
    state: AgentState,
    event: str,
    details: dict[str, Any] | None = None,
) -> AgentState:
    """
    Add an event to the workflow trace.
    """

    trace = state.get("trace", [])

    trace_entry = {
        "request_id": state.get("request_id", ""),
        "event": event,
        "details": details or {},
    }

    return {
        **state,
        "trace": trace + [trace_entry],
    }