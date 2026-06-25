from fastapi import FastAPI
from pydantic import BaseModel
from .graph import build_graph

app = FastAPI(title="Contract Risk Analyst Agent")
agent = build_graph()


class AnalyzeRequest(BaseModel):
    input_path: str


@app.post("/analyze")
def analyze_contract(request: AnalyzeRequest):
    result = agent.invoke({"input_path": request.input_path})
    return {
        "contract_type": result.get("contract_type"),
        "risk_level": result.get("risk_level"),
        "report": result.get("report"),
        "saved_report_path": result.get("saved_report_path"),
    }
