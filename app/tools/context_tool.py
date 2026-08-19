import json
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "services.json"


def get_service_context(service_name: str) -> dict[str, Any]:
    """
    Read-only tool that retrieves synthetic service health information.

    This tool does not modify any data or perform any operational action.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        services = json.load(file)

    if service_name not in services:
        raise ValueError(f"Unknown service: {service_name}")

    return services[service_name]