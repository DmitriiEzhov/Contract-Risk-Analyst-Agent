from pathlib import Path

KNOWLEDGE_DIR = Path("data/knowledge")

CHECKLIST_FILES = {
    "rental": "rental_contract_checklist.md",
    "service": "service_contract_checklist.md",
    "nda": "nda_checklist.md",
    "sales": "sales_contract_checklist.md",
    "employment": "general_contract_risks.md",
    "general": "general_contract_risks.md",
}


def retrieve_checklist(contract_type: str) -> str:
    filename = CHECKLIST_FILES.get(contract_type, "general_contract_risks.md")
    path = KNOWLEDGE_DIR / filename
    if not path.exists():
        path = KNOWLEDGE_DIR / "general_contract_risks.md"
    return path.read_text(encoding="utf-8")
