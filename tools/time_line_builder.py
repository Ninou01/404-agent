from llama_index.core.tools.function_tool import FunctionTool

from formats import OrderCurrentState, OrderTimeline, StatusTransition, TimelineEntry, InvestigationResponse
from tools.order_log_tool import get_order_logs

def generate_investigation_response(order_id: int, logs: list[dict]) -> InvestigationResponse:
    from operator import itemgetter

    # Sort logs
    order_logs = sorted(logs, key=lambda l: l["timestamp"])
    
    # Timeline
    timeline_entries = []
    for log in order_logs:
        transition = StatusTransition(
            from_status=f"{log['pre_state']['status']}::{log['pre_state'].get('intra_status')}" if log['pre_state'].get("intra_status") else log['pre_state']['status'],
            to_status=f"{log['post_state']['status']}::{log['post_state'].get('intra_status')}" if log['post_state'].get("intra_status") else log['post_state']['status'],
        )
        entry = TimelineEntry(
            timestamp=log["timestamp"],
            action=log["action"],
            user=f"{log['user']['name']} ({log['user']['role']})",
            location=log.get("warehouse", {}).get("warehouse_name"),
            status_transition=transition,
            related_entities=[e["type"] for e in log.get("related_entities", [])]
        )
        timeline_entries.append(entry)
    
    timeline = OrderTimeline(order_id=order_id, timeline=timeline_entries)

    # Current state
    last_log = order_logs[-1]
    current = OrderCurrentState(
        order_id=order_id,
        current_status=last_log["post_state"].get("status"),
        current_intra_status=last_log["post_state"].get("intra_status"),
        last_action=last_log["action"],
        last_user=last_log["user"]["name"],
        last_user_role=last_log["user"]["role"],
        location=last_log.get("warehouse", {}).get("warehouse_name"),
        timestamp=last_log["timestamp"]
    )

    # Call your LLM to generate summary and gaps
    summary = f"Order {order_id} was handled by {current.last_user} at {current.location} with final status {current.current_status}."
    gaps = []  # Optional: later enhanced via your status/lifecycle JSONQueryEngine

    return InvestigationResponse(
        summary=summary,
        gaps_or_broken_steps=gaps,
        order_timeline=timeline,
        current_state=current
    )


def build_order_timeline(order_id: int) -> dict:
    logs = get_order_logs(order_id)  # use your existing function
    response = generate_investigation_response(order_id, logs)
    return response.dict()

timeline_builder_tool = FunctionTool.from_defaults(
    fn=build_order_timeline,
    name="build_order_timeline",
    description="Build a structured investigation report for an order using logs, including timeline and current state"
)