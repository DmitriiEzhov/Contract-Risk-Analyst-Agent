import argparse
from .graph import build_graph


def main():
    parser = argparse.ArgumentParser(description="Contract Risk Analyst Agent")
    parser.add_argument("input_path", help="Path to a .txt contract file")
    args = parser.parse_args()

    app = build_graph()
    result = app.invoke({"input_path": args.input_path})

    print("\n=== CONTRACT ANALYSIS REPORT ===\n")
    print(result.get("report", ""))
    print("\nSaved to:", result.get("saved_report_path"))


if __name__ == "__main__":
    main()
