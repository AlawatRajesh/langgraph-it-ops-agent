from langgraph.graph import END, START, StateGraph

from app.nodes import (
    approval_node,
    context_node,
    execution_node,
    intake_node,
    planning_node,
    validation_node,
    verification_node,
)

from app.routing import (
    route_after_approval,
    route_after_validation,
    route_after_planning,
)

from app.state import AgentState


def build_graph():
    """
    Build the LangGraph workflow.
    """

    builder = StateGraph(AgentState)

    # -------------------------
    # Nodes
    # -------------------------
    builder.add_node("intake", intake_node)
    builder.add_node("validate", validation_node)
    builder.add_node("context", context_node)
    builder.add_node("planning", planning_node)
    builder.add_node("approval", approval_node)
    builder.add_node("execute", execution_node)
    builder.add_node("verify", verification_node)

    # -------------------------
    # Start → Intake → Validate
    # -------------------------
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "validate")

    # -------------------------
    # Validation routing
    # -------------------------
    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "reject": END,
            "context": "context",
        },
    )

    # -------------------------
    # Context → Planning → Approval
    # -------------------------
    builder.add_edge("context", "planning")

    builder.add_conditional_edges(
        "planning",
        route_after_planning,
        {
            "approval": "approval",
            "health_check": "verify",
        },
    )

    # -------------------------
    # Approval routing
    # -------------------------
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "reject": END,
            "execute": "execute",
        },
    )

    # -------------------------
    # Execute → Verify → End
    # -------------------------
    builder.add_edge("execute", "verify")
    builder.add_edge("verify", END)

    return builder.compile()
