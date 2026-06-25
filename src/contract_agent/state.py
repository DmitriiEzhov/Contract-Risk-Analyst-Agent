from typing import Any, Dict, List, Literal, TypedDict

RiskLevel = Literal["low", "medium", "high"]

class ContractAgentState(TypedDict, total=False):
    input_path: str
    contract_text: str
    contract_type: str
    need_rag: bool
    retrieved_context: str
    extracted_facts: Dict[str, Any]
    risks: List[Dict[str, Any]]
    risk_level: RiskLevel
    report: str
    saved_report_path: str
    errors: List[str]
