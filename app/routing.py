from app.state import AgentState


def route_after_validation(state: AgentState) -> str:
    """
    Decide where the workflow goes after validation.
    """

    if state.get("validation_status") != "valid":
        return "reject"

    if state.get("permission_status") != "allowed":
        return "reject"

    return "context"


def route_after_approval(state: AgentState) -> str:
    """
    Only approved requests can reach execution.
    """

    if state.get("approval_result") == "approved":
        return "execute"

    return "reject"
def route_after_planning(state: AgentState) -> str:
    """
    Route restart requests to approval.
    Route health checks directly to verification.
    """

    if state.get("action") == "health_check":
        return "health_check"

    return "approval"