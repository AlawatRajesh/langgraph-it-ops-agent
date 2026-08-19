# Approval-Gated IT Operations Assistant

## 1. Overview

This repository implements a safe, approval-gated IT operations assistant built with LangGraph. It demonstrates a typed workflow that ingests user requests, validates them deterministically, retrieves read-only context, generates a proposed plan, requires human approval for impactful actions, and then executes a mocked action followed by verification. All actions use synthetic data only.

## 2. Key Features

- LangGraph workflow with typed `AgentState`.
- Deterministic validation and permission checks.
- Read-only context retrieval tool (`app.tools.context_tool`).
- Mocked action tool (`app.tools.action_tool`) that only modifies synthetic data.
- Human approval gate before execution.
- Verification step after execution.
- Duplicate request protection and simple timeout/tool-failure handling.
- Trace/audit events recorded for every node via `app.tracing.add_trace`.
- Automated tests exercising happy, failure, and edge cases.

## 3. Architecture

See the diagram: [diagrams/architecture.png](diagrams/architecture.png)

## 4. Workflow

The workflow follows these steps:

Intake → Validation → Context Retrieval → Planning → Human Approval → Execute → Verification → Final Status

- Validation or approval rejection terminates the workflow safely.
- `health_check` actions route directly to verification (no approval required).
- `restart` actions require approval.

## 5. Safety Design

Safety is paramount:

- No operational action runs before explicit human approval.
- Graph-level routing prevents `execute` unless approval is `approved`.
- `execution_node` performs a defense-in-depth approval check and blocks execution if approval is missing.
- Permission checks are deterministic (no LLM decisions affect permissions).
- Tools operate on synthetic data only; no credentials or production endpoints are used.
- The action tool is mocked and writes only to `data/services.json`.

## 6. Project Structure

```
langgraph-it-ops-agent/
├── app/
│   ├── graph.py
│   ├── nodes.py
│   ├── policies.py
│   ├── routing.py
│   ├── state.py
│   ├── tracing.py
│   └── tools/
│       ├── action_tool.py
│       └── context_tool.py
├── data/
│   └── services.json
├── diagrams/
│   └── architecture.png
├── presentation/
│   └── README.md
├── tests/
├── main.py
├── README.md
├── requirements.txt
└── SUBMISSION_CHECKLIST.md
```

## 7. Requirements

- Python 3.9+ (typing `TypedDict` and modern stdlib features used).
- Install dependencies from `requirements.txt` (LangGraph and test tooling).

Actual `requirements.txt` contents are used — do not invent versions.

## 8. Setup (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 9. Run

Run the example agent from `main.py`:

```powershell
python main.py
```

This will run a sample `Restart payment-service` request and prompt for human approval in the console.

## 10. Testing

Run the automated tests:

```powershell
pytest -v
```

The test suite covers at least 8 scenarios: happy path, approval rejection, invalid input, permission failure, duplicate request, tool failure, timeout, and missing approval.

## 11. Example

Request: "Restart payment-service"

- The agent generates a plan and prompts for approval.
- On approval, the mocked restart runs and returns success.
- Verification reads the synthetic `services.json` and ensures `status == healthy`.

## 12. Failure Handling

The agent handles:

- Invalid input → validation rejection and safe termination.
- Permission failure → rejection and no execution.
- Duplicate request → rejected with a trace entry.
- Missing approval → execution blocked and rejected.
- Tool failure → captured in trace and final status set to `failed`.
- Timeouts from mocked tools → captured as `timeout` and final state `failed`.

## 13. Observability / Trace

Each node adds structured trace entries via `app.tracing.add_trace` that include:

- `request_id` — the original request identifier.
- `event` — node or tool event name.
- `details` — contextual details (tool calls, reasons, errors).

Traces appear on the final `AgentState` under `trace` for audit.

## 14. Design Trade-offs

This assessment emphasizes deterministic safety. Decisions such as permission checks and approval routing are deterministic to avoid letting an LLM directly authorize actions. The approval gate is explicit and human-driven, with defense-in-depth checks in the execution node.

## 15. Future Improvements (not implemented here)

- Persistent checkpoints (Redis/Postgres) for durable workflows.
- Production authentication and authorization.
- More robust observability integration.
- Secure LLM adapters and Bedrock integrations.
- Retry policies and durable idempotency store.


---

If you want, I can now generate the architecture diagram PNG from the draw.io file, or create a PowerPoint draft for the presentation slides. Please tell me which to do next.