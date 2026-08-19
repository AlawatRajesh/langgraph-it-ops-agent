from app.graph import build_graph


def main():
    graph = build_graph()

    initial_state = {
        "request_id": "REQ-001",
        "user": "operator",
        "request": "Restart payment-service",
    }

    result = graph.invoke(initial_state)

    print("\nFinal State:")
    print(result)


if __name__ == "__main__":
    main()