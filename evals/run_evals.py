import json
from src.contract_agent.graph import build_graph


def load_cases(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def main():
    app = build_graph()
    total = 0
    passed = 0

    for case in load_cases("evals/cases.jsonl"):
        total += 1
        result = app.invoke({"input_path": case["input_path"]})
        report = result.get("report", "").lower()
        ok = all(word.lower() in report for word in case["expected_contains"])
        passed += int(ok)
        print(f'{case["id"]}: {"PASS" if ok else "FAIL"}')

    print(f"\nSuccess rate: {passed / total:.2%}" if total else "No cases")


if __name__ == "__main__":
    main()
