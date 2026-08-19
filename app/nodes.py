import re

from app.policies import (
    check_permission,
    is_duplicate_request,
    validate_action,
    validate_service,
)
from app.state import AgentState
from app.tools.action_tool import restart_service
from app.tools.context_tool import get_service_context
from app.tracing import add_trace


def intake_node(state: AgentState) -> AgentState:
    """
    Extract service and action from the user's request.
    Also checks for duplicate request IDs.
    """

    request_id = state["request_id"]

    # Duplicate request protection
    if is_duplicate_request(request_id):
        return add_trace(
            {
                **state,
                "final_status": "rejected",
                "error_type": "duplicate_request",
                "error_message": (
                    f"Request {request_id} has already been processed."
                ),
            },
            "duplicate_request",
            {
                "request_id": request_id,
            },
        )

    request = state["request"].strip().lower()

    service_match = re.search(
        r"(payment-service|auth-service|notification-service)",
        request,
    )

    if service_match:
        service = service_match.group(1)
    else:
        service = ""

    if "restart" in request:
        action = "restart"
    elif "health" in request or "check" in request:
        action = "health_check"
    else:
        action = ""

    return add_trace(
        {
            **state,
            "service": service,
            "action": action,
        },
        "intake",
        {
            "service": service,
            "action": action,
        },
    )


def validation_node(state: AgentState) -> AgentState:
    """
    Validate service, action, and user permission.
    """

    # If a previous node already finalized the request, don't overwrite it.
    if state.get("final_status"):
        return state

    service = state.get("service", "")
    action = state.get("action", "")
    user = state.get("user", "")

    # Validate service
    if not validate_service(service):
        return add_trace(
            {
                **state,
                "validation_status": "invalid",
                "validation_error": f"Unknown service: {service}",
                "error_type": "unknown_service",
                "error_message": f"Unknown service: {service}",
                "final_status": "rejected",
            },
            "validation",
            {
                "status": "invalid",
                "reason": "unknown_service",
            },
        )

    # Validate action
    if not validate_action(action):
        return add_trace(
            {
                **state,
                "validation_status": "invalid",
                "validation_error": f"Invalid action: {action}",
                "error_type": "invalid_action",
                "error_message": f"Invalid action: {action}",
                "final_status": "rejected",
            },
            "validation",
            {
                "status": "invalid",
                "reason": "invalid_action",
            },
        )

    # Check permission
    if not check_permission(user, action):
        return add_trace(
            {
                **state,
                "validation_status": "valid",
                "permission_status": "denied",
                "validation_error": "User does not have permission.",
                "error_type": "permission_denied",
                "error_message": "User does not have permission.",
                "final_status": "rejected",
            },
            "validation",
            {
                "status": "permission_denied",
                "user": user,
                "action": action,
            },
        )

    return add_trace(
        {
            **state,
            "validation_status": "valid",
            "permission_status": "allowed",
            "validation_error": "",
        },
        "validation",
        {
            "status": "valid",
            "permission": "allowed",
        },
    )


def context_node(state: AgentState) -> AgentState:
    """
    Retrieve service context using the read-only context tool.
    """

    service = state["service"]

    try:
        context = get_service_context(service)

        return add_trace(
            {
                **state,
                "context": context,
            },
            "context_retrieved",
            {
                "service": service,
                "tool": "get_service_context",
            },
        )

    except Exception as exc:
        return add_trace(
            {
                **state,
                "error_type": "context_tool_failure",
                "error_message": str(exc),
                "final_status": "failed",
            },
            "context_tool_failure",
            {
                "service": service,
                "error": str(exc),
            },
        )


def planning_node(state: AgentState) -> AgentState:
    """
    Create a proposed operational plan.
    """

    service = state["service"]
    action = state["action"]
    context = state["context"]

    if action == "restart":
        plan = (
            f"Proposed plan: restart {service} because its current "
            f"status is {context['status']}. After the restart, "
            f"verify that the service is healthy."
        )

    elif action == "health_check":
        plan = (
            f"Proposed plan: check the current health of {service} "
            f"and report the service status."
        )

    else:
        plan = f"No supported plan available for action: {action}"

    return add_trace(
        {
            **state,
            "plan": plan,
            "approval_required": action == "restart",
        },
        "plan_created",
        {
            "approval_required": action == "restart",
        },
    )


def approval_node(state: AgentState) -> AgentState:
    """
    Request human approval before any operational action.
    """

    service = state["service"]
    action = state["action"]
    plan = state["plan"]

    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Service : {service}")
    print(f"Action  : {action}")
    print(f"Plan    : {plan}")
    print("=" * 60)

    approval = input("Approve this action? (yes/no): ").strip().lower()

    if approval in {"yes", "y"}:
        result = "approved"
    else:
        result = "rejected"

    return add_trace(
        {
            **state,
            "approval_required": True,
            "approval_result": result,
        },
        "approval",
        {
            "result": result,
        },
    )


def execution_node(state: AgentState) -> AgentState:
    """
    Execute the mocked action only after human approval.
    """

    # Critical safety check
    if state.get("approval_result") != "approved":
        return add_trace(
            {
                **state,
                "execution_status": "blocked",
                "error_type": "missing_approval",
                "error_message": (
                    "Action cannot execute without human approval."
                ),
                "final_status": "rejected",
            },
            "execution_blocked",
            {
                "reason": "missing_approval",
            },
        )

    service = state["service"]

    try:
        result = restart_service(service)

        tool_call = {
            "tool": "restart_service",
            "service": service,
            "status": "success",
        }

        return add_trace(
            {
                **state,
                "tool_calls": state.get("tool_calls", []) + [tool_call],
                "execution_status": "success",
                "execution_result": result,
            },
            "execution",
            {
                "tool": "restart_service",
                "status": "success",
            },
        )

    except TimeoutError as exc:
            return add_trace(
                {
                    **state,
                    "execution_status": "failed",
                    "error_type": "timeout",
                    "error_message": str(exc),
                    "final_status": "failed",
                },
                "execution_timeout",
                {
                    "tool": "restart_service",
                    "error": str(exc),
                },
            )

    except Exception as exc:
        return add_trace(
            {
                **state,
                "execution_status": "failed",
                "error_type": "action_tool_failure",
                "error_message": str(exc),
                "final_status": "failed",
            },
            "execution_failed",
            {
                "tool": "restart_service",
                "error": str(exc),
            },
        )


def verification_node(state: AgentState) -> AgentState:
    """
    Verify the service after execution.
    """

    service = state["service"]

    try:
        context = get_service_context(service)

        if context.get("status") == "healthy":
            verification_status = "success"
        else:
            verification_status = "failed"
        # Do not overwrite an existing failure/rejection final_status
        computed_final = (
            "success" if verification_status == "success" else "failed"
        )

        final_status = state.get("final_status") or computed_final

        return add_trace(
            {
                **state,
                "verification_status": verification_status,
                "verification_result": context,
                "final_status": final_status,
            },
            "verification",
            {
                "status": verification_status,
                "service": service,
            },
        )

    except Exception as exc:
        return add_trace(
            {
                **state,
                "verification_status": "failed",
                "error_type": "verification_failure",
                "error_message": str(exc),
                "final_status": "failed",
            },
            "verification_failed",
            {
                "service": service,
                "error": str(exc),
            },
        )