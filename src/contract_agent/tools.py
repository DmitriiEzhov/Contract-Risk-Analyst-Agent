from pathlib import Path
from datetime import datetime
import json


def read_document_tool(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if file_path.suffix.lower() != ".txt":
        raise ValueError("Only .txt files are supported in this baseline version")
    return file_path.read_text(encoding="utf-8")


def save_report_tool(report: str, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"contract_report_{timestamp}.md"
    output_path.write_text(report, encoding="utf-8")
    return str(output_path)


def estimate_cost_tool(text: str, output_tokens: int = 1200) -> dict:
    approx_input_tokens = max(1, len(text) // 4)
    return {
        "approx_input_tokens": approx_input_tokens,
        "approx_output_tokens": output_tokens,
        "approx_total_tokens": approx_input_tokens + output_tokens,
    }


def save_run_metadata_tool(metadata: dict, path: str = "reports/runs.jsonl") -> str:
    Path(path).parent.mkdir(exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
    return path
