import json
from langgraph.graph import StateGraph, END

from .state import ContractAgentState
from .tools import read_document_tool, save_report_tool, estimate_cost_tool, save_run_metadata_tool
from .rag import retrieve_checklist
from .llm import call_llm
from .json_utils import parse_json_safely
from .prompts import CLASSIFY_CONTRACT_PROMPT, EXTRACT_FACTS_PROMPT, RISK_ANALYSIS_PROMPT, REPORT_PROMPT

ALLOWED_TYPES = {"rental", "service", "nda", "sales", "employment", "general"}
ALLOWED_RISKS = {"low", "medium", "high"}


def read_document_node(state: ContractAgentState):
    return {"contract_text": read_document_tool(state["input_path"])}


def classify_contract_node(state: ContractAgentState):
    label = call_llm(CLASSIFY_CONTRACT_PROMPT, state["contract_text"][:6000]).strip().lower()
    label = label.replace("`", "").split()[0] if label else "general"
    if label not in ALLOWED_TYPES:
        label = "general"
    # Contract analysis almost always benefits from a checklist, so baseline uses RAG.
    return {"contract_type": label, "need_rag": True}


def route_rag(state: ContractAgentState):
    return "use_rag" if state.get("need_rag") else "skip_rag"


def retrieve_rag_node(state: ContractAgentState):
    return {"retrieved_context": retrieve_checklist(state.get("contract_type", "general"))}


def skip_rag_node(state: ContractAgentState):
    return {"retrieved_context": ""}


def extract_facts_node(state: ContractAgentState):
    response = call_llm(EXTRACT_FACTS_PROMPT, state["contract_text"][:10000])
    facts = parse_json_safely(response, {"raw_response": response})
    return {"extracted_facts": facts}


def risk_analysis_node(state: ContractAgentState):
    prompt = f"""
Contract type: {state.get('contract_type', 'general')}

Checklist:
{state.get('retrieved_context', '')}

Contract text:
{state['contract_text'][:12000]}
"""
    response = call_llm(RISK_ANALYSIS_PROMPT, prompt)
    data = parse_json_safely(response, {"risks": [{"risk": "Could not parse risk output", "severity": "medium", "explanation": response, "recommendation": "Review manually"}], "overall_risk_level": "medium"})
    risks = data.get("risks", []) if isinstance(data, dict) else []
    level = data.get("overall_risk_level", "medium") if isinstance(data, dict) else "medium"
    if level not in ALLOWED_RISKS:
        level = "medium"
    return {"risks": risks, "risk_level": level}


def route_risk_level(state: ContractAgentState):
    return state.get("risk_level", "medium")


def generate_low_risk_report_node(state: ContractAgentState):
    return generate_report(state, "short and calm")


def generate_medium_risk_report_node(state: ContractAgentState):
    return generate_report(state, "detailed and practical")


def generate_high_risk_report_node(state: ContractAgentState):
    return generate_report(state, "warning-focused and very explicit")


def generate_report(state: ContractAgentState, report_style: str):
    prompt = f"""
Report style: {report_style}

Contract type:
{state.get('contract_type')}

Extracted facts:
{json.dumps(state.get('extracted_facts', {}), ensure_ascii=False, indent=2)}

Risks:
{json.dumps(state.get('risks', []), ensure_ascii=False, indent=2)}

Risk level:
{state.get('risk_level')}
"""
    return {"report": call_llm(REPORT_PROMPT, prompt, max_tokens=1800)}


def save_report_node(state: ContractAgentState):
    report_path = save_report_tool(state["report"])
    cost = estimate_cost_tool(state["contract_text"])
    save_run_metadata_tool({
        "input_path": state.get("input_path"),
        "contract_type": state.get("contract_type"),
        "risk_level": state.get("risk_level"),
        "saved_report_path": report_path,
        "cost_estimate": cost,
    })
    return {"saved_report_path": report_path}


def build_graph():
    graph = StateGraph(ContractAgentState)
    graph.add_node("read_document", read_document_node)
    graph.add_node("classify_contract", classify_contract_node)
    graph.add_node("retrieve_rag", retrieve_rag_node)
    graph.add_node("skip_rag", skip_rag_node)
    graph.add_node("extract_facts", extract_facts_node)
    graph.add_node("risk_analysis", risk_analysis_node)
    graph.add_node("low_risk_report", generate_low_risk_report_node)
    graph.add_node("medium_risk_report", generate_medium_risk_report_node)
    graph.add_node("high_risk_report", generate_high_risk_report_node)
    graph.add_node("save_report", save_report_node)

    graph.set_entry_point("read_document")
    graph.add_edge("read_document", "classify_contract")
    graph.add_conditional_edges("classify_contract", route_rag, {"use_rag": "retrieve_rag", "skip_rag": "skip_rag"})
    graph.add_edge("retrieve_rag", "extract_facts")
    graph.add_edge("skip_rag", "extract_facts")
    graph.add_edge("extract_facts", "risk_analysis")
    graph.add_conditional_edges("risk_analysis", route_risk_level, {"low": "low_risk_report", "medium": "medium_risk_report", "high": "high_risk_report"})
    graph.add_edge("low_risk_report", "save_report")
    graph.add_edge("medium_risk_report", "save_report")
    graph.add_edge("high_risk_report", "save_report")
    graph.add_edge("save_report", END)
    return graph.compile()
