import json
from llama_index.core.tools.function_tool import FunctionTool

def get_order_logs(order_id: int) -> list[dict]:
    """
    Retrieve all logs related to a specific order ID.

    Parameters:
        order_id (int): The ID of the order to search for.

    Returns:
        list: Filtered logs matching the given order ID.
    """
    with open("logs.json", "r") as f:
        logs = json.load(f)
    return [
        log for log in logs
        if log.get("item", {}).get("type") == "order"
        and log["item"].get("itemId") == order_id
    ]


order_log_tool = FunctionTool.from_defaults(
    fn=get_order_logs,
    name="get_order_logs",
    description="Fetch all log entries related to a specific order ID."
)
