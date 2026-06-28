from google.adk.agents.callback_context import CallbackContext

def init_planner_state(callback_context: CallbackContext) -> None:
    if "ranked_plots" not in callback_context.state:
        callback_context.state["ranked_plots"] = []
    if "filters" not in callback_context.state:
        callback_context.state["filters"] = {}
    if "query" not in callback_context.state:
        callback_context.state["query"] = ""
    if "investment_analysis" not in callback_context.state:
        callback_context.state["investment_analysis"] = "N/A"
    if "risk_analysis" not in callback_context.state:
        callback_context.state["risk_analysis"] = "N/A"
    if "location_analysis" not in callback_context.state:
        callback_context.state["location_analysis"] = "N/A"
    if "document_analysis" not in callback_context.state:
        callback_context.state["document_analysis"] = "N/A"
    if "deterministic_analysis" not in callback_context.state:
        callback_context.state["deterministic_analysis"] = {}
    if "investment_metrics" not in callback_context.state:
        callback_context.state["investment_metrics"] = []
    if "risk_metrics" not in callback_context.state:
        callback_context.state["risk_metrics"] = []
    if "location_metrics" not in callback_context.state:
        callback_context.state["location_metrics"] = []