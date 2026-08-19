import json
import time
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "services.json"


def restart_service(
    service_name: str,
    simulate_failure: bool = False,
    simulate_timeout: bool = False,
) -> dict[str, Any]:
    """
    Mocked restart action.

    This only modifies synthetic data.
    No real infrastructure is touched.
    """

    # Simulate timeout
    if simulate_timeout:
        time.sleep(2)
        raise TimeoutError("Mock action timed out.")

    # Simulate tool failure
    if simulate_failure:
        raise RuntimeError("Mock restart tool failed.")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        services = json.load(file)

    if service_name not in services:
        raise ValueError(f"Unknown service: {service_name}")

    # Update synthetic service state
    services[service_name]["status"] = "healthy"
    services[service_name]["cpu"] = 35
    services[service_name]["memory"] = 45
    services[service_name]["error_rate"] = 0.2

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(services, file, indent=4)

    return {
        "service": service_name,
        "action": "restart",
        "status": "success",
        "message": f"{service_name} restarted successfully (mocked).",
    }