from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.nodes import (
    router_node,
    extract_card_node,
    confirmation_node,
    dedup_check_node,
    write_sheets_node,
    whatsapp_node,
    transcribe_audio_node,
    upload_audio_node,
    update_sheets_voice_node,
    respond_node,
)


def _route_from_router(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "IMAGE_UPLOAD":
        return "extract_card"
    if intent == "VOICE_UPLOAD":
        return "transcribe_audio"
    if intent in ("CONFIRMATION_YES", "CONFIRMATION_NO"):
        return "confirmation"
    return "respond"


def _route_from_confirmation(state: AgentState) -> str:
    return "dedup_check" if state.get("user_confirmed") else "respond"


def _route_from_dedup(state: AgentState) -> str:
    return "respond" if state.get("is_duplicate") else "write_sheets"


def _route_from_transcribe(state: AgentState) -> str:
    return "respond" if state.get("error") else "upload_audio"


def _route_from_upload(state: AgentState) -> str:
    return "respond" if state.get("error") else "update_sheets_voice"


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("extract_card", extract_card_node)
    graph.add_node("confirmation", confirmation_node)
    graph.add_node("dedup_check", dedup_check_node)
    graph.add_node("write_sheets", write_sheets_node)
    graph.add_node("send_whatsapp", whatsapp_node)
    graph.add_node("transcribe_audio", transcribe_audio_node)
    graph.add_node("upload_audio", upload_audio_node)
    graph.add_node("update_sheets_voice", update_sheets_voice_node)
    graph.add_node("respond", respond_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges("router", _route_from_router, {
        "extract_card": "extract_card",
        "transcribe_audio": "transcribe_audio",
        "confirmation": "confirmation",
        "respond": "respond",
    })

    graph.add_edge("extract_card", "respond")

    graph.add_conditional_edges("confirmation", _route_from_confirmation, {
        "dedup_check": "dedup_check",
        "respond": "respond",
    })

    graph.add_conditional_edges("dedup_check", _route_from_dedup, {
        "respond": "respond",
        "write_sheets": "write_sheets",
    })

    graph.add_edge("write_sheets", "send_whatsapp")
    graph.add_edge("send_whatsapp", "respond")

    graph.add_conditional_edges("transcribe_audio", _route_from_transcribe, {
        "respond": "respond",
        "upload_audio": "upload_audio",
    })

    graph.add_conditional_edges("upload_audio", _route_from_upload, {
        "respond": "respond",
        "update_sheets_voice": "update_sheets_voice",
    })

    graph.add_edge("update_sheets_voice", "respond")
    graph.add_edge("respond", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


agent = build_agent_graph()
