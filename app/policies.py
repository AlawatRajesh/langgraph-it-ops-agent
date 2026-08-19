from typing import Final


ALLOWED_SERVICES: Final = {
    "payment-service",
    "auth-service",
    "notification-service",
}

ALLOWED_ACTIONS: Final = {
    "health_check",
    "restart",
}

AUTHORIZED_USERS: Final = {
    "admin",
    "operator",
}


def validate_service(service: str) -> bool:
    return service in ALLOWED_SERVICES


def validate_action(action: str) -> bool:
    return action in ALLOWED_ACTIONS


def check_permission(user: str, action: str) -> bool:
    if action == "health_check":
        return True

    return user in AUTHORIZED_USERS
PROCESSED_REQUESTS: set[str] = set()


def is_duplicate_request(request_id: str) -> bool:
    """
    Check whether a request has already been processed.
    """

    if request_id in PROCESSED_REQUESTS:
        return True

    PROCESSED_REQUESTS.add(request_id)

    return False