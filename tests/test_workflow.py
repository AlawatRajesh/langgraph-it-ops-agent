from app.graph import build_graph


def make_request(request="Restart payment-service", request_id="TEST-001"):
    return {
        "request_id": request_id,
        "user": "operator",
        "request": request,
    }


def test_happy_path(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yes",
    )

    graph = build_graph()

    result = graph.invoke(
        make_request(
            request_id="TEST-HAPPY-001"
        )
    )

    assert result["approval_result"] == "approved"
    assert result["execution_status"] == "success"
    assert result["verification_status"] == "success"
    assert result["final_status"] == "success"


def test_rejection(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "no",
    )

    graph = build_graph()

    result = graph.invoke(
        make_request(
            request_id="TEST-REJECT-001"
        )
    )

    assert result["approval_result"] == "rejected"
    assert result.get("execution_status") is None
def test_invalid_input():
    graph = build_graph()

    result = graph.invoke(
        make_request(
            request="Restart unknown-service",
            request_id="TEST-INVALID-001",
        )
    )

    assert result["validation_status"] == "invalid"
    assert result["final_status"] == "rejected"
    assert result["error_type"] == "unknown_service"

def test_permission_failure(monkeypatch):
    monkeypatch.setattr(
        "app.nodes.check_permission",
        lambda user, action: False,
    )

    graph = build_graph()

    result = graph.invoke(
        make_request(
            request_id="TEST-PERMISSION-001"
        )
    )

    assert result["permission_status"] == "denied"
    assert result["final_status"] == "rejected"
    assert result["error_type"] == "permission_denied"
def test_duplicate_request(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yes",
    )

    graph = build_graph()

    request_id = "TEST-DUPLICATE-001"

    # First request
    first_result = graph.invoke(
        make_request(
            request_id=request_id
        )
    )

    assert first_result["final_status"] == "success"

    # Same request ID again
    second_result = graph.invoke(
        make_request(
            request_id=request_id
        )
    )

    assert second_result["final_status"] == "rejected"
    assert second_result["error_type"] == "duplicate_request"

def test_tool_failure(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yes",
    )

    def failing_restart_service(service_name):
        raise RuntimeError("Mock restart tool failed.")

    monkeypatch.setattr(
        "app.nodes.restart_service",
        failing_restart_service,
    )

    graph = build_graph()

    result = graph.invoke(
        make_request(
            request_id="TEST-TOOL-FAILURE-001"
        )
    )

    assert result["execution_status"] == "failed"
    assert result["error_type"] == "action_tool_failure"
    assert result["final_status"] == "failed"
def test_timeout(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yes",
    )

    def timeout_restart_service(service_name):
        raise TimeoutError("Mock action timed out.")

    monkeypatch.setattr(
        "app.nodes.restart_service",
        timeout_restart_service,
    )

    graph = build_graph()

    result = graph.invoke(
        make_request(
            request_id="TEST-TIMEOUT-001"
        )
    )

    assert result["execution_status"] == "failed"
    assert result["error_type"] == "timeout"
    assert result["final_status"] == "failed"
from app.nodes import execution_node


def test_missing_approval():
    state = make_request(
        request_id="TEST-NO-APPROVAL-001"
    )

    state["service"] = "payment-service"
    state["action"] = "restart"
    state["approval_required"] = True
    state["approval_result"] = "rejected"

    result = execution_node(state)

    assert result["execution_status"] == "blocked"
    assert result["error_type"] == "missing_approval"
    assert result["final_status"] == "rejected"