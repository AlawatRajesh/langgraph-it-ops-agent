from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between all LangGraph nodes.
    """

    # ---------------------------------------------------------
    # Request information
    # ---------------------------------------------------------
    request_id: str
    user: str
    request: str

    # ---------------------------------------------------------
    # Parsed request
    # ---------------------------------------------------------
    service: str
    action: str

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    validation_status: str
    validation_error: str
    permission_status: str

    # ---------------------------------------------------------
    # Retrieved service context
    # ---------------------------------------------------------
    context: dict[str, Any]

    # ---------------------------------------------------------
    # AI-generated proposal
    # ---------------------------------------------------------
    plan: str

    # ---------------------------------------------------------
    # Human approval
    # ---------------------------------------------------------
    approval_required: bool
    approval_result: str

    # ---------------------------------------------------------
    # Tool execution
    # ---------------------------------------------------------
    tool_calls: list[dict[str, Any]]
    execution_status: str
    execution_result: dict[str, Any]

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------
    verification_status: str
    verification_result: dict[str, Any]

    # ---------------------------------------------------------
    # Error handling
    # ---------------------------------------------------------
    error_type: str
    error_message: str

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    final_status: str

    # ---------------------------------------------------------
    # Observability / audit trace
    # ---------------------------------------------------------
    trace: list[dict[str, Any]]