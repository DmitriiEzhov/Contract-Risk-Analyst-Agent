# Contract Risk Analyst Agent

AI-агент для предварительного анализа договоров перед подписанием.

Агент принимает текст договора, определяет тип документа, извлекает ключевые условия, проверяет договор по чеклисту рисков через RAG, классифицирует уровень риска и сохраняет отчет.

Важно: агент не заменяет юриста и не предоставляет юридическое заключение. Это предварительный risk screening.

## Architecture

```text
User
 ↓
CLI / FastAPI
 ↓
LangGraph Agent
 ↓
read_document
 ↓
classify_contract
 ↓
need_rag?
 ├── yes → retrieve_checklist
 └── no  → skip_rag
 ↓
extract_facts
 ↓
risk_analysis
 ↓
risk_level_branch
 ├── low    → generate_short_report
 ├── medium → generate_detailed_report
 └── high   → generate_warning_report
 ↓
save_report
 ↓
END
```

The graph has two branching points: RAG routing and risk-level report routing.

## Tools

- `read_document_tool` — reads contract text from filesystem.
- `save_report_tool` — saves final report to `reports/`.
- `estimate_cost_tool` — estimates approximate token usage.
- `save_run_metadata_tool` — saves run metadata to JSONL.

## RAG

RAG knowledge is stored in `data/knowledge/`:

- `general_contract_risks.md`
- `rental_contract_checklist.md`
- `service_contract_checklist.md`
- `nda_checklist.md`
- `sales_contract_checklist.md`

Current version uses deterministic retrieval by contract type. It can be replaced by FAISS/Chroma later.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env`:

```env
YANDEX_API_KEY=your_secret_key
YANDEX_BASE_URL=https://ai.api.cloud.yandex.net/v1
YANDEX_MODEL=gpt://your_folder_id/yandexgpt/latest
```

## Run CLI

```bash
PYTHONPATH=. python -m src.contract_agent.cli data/examples/contract_01.txt
```

## Run API

```bash
PYTHONPATH=. uvicorn src.contract_agent.api:app --reload
```

Request:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input_path":"data/examples/contract_01.txt"}'
```

## Benchmark

Benchmark file: `evals/cases.jsonl`.

Run:

```bash
PYTHONPATH=. python evals/run_evals.py
```

Metric:

```text
success rate = passed cases / total cases
```

## Evaluation

The project uses three types of checks:

1. Programmatic accept: expected keywords in final report.
2. LLM-as-judge: can be added for semantic assessment.
3. Tool-call correctness: run metadata shows that file reading, report saving, and cost estimation were executed.

## LangFuse

Optional observability can be added with LangFuse. Suggested trace fields:

- input path;
- contract type;
- selected graph route;
- retrieved checklist;
- extracted facts;
- risk level;
- final report;
- latency;
- approximate token usage;
- errors.

## Security checklist

- [x] API keys are stored in `.env`, not in code.
- [x] `.env` is ignored by git.
- [x] Agent output includes a disclaimer.
- [x] The agent performs preliminary analysis, not legal advice.
- [x] Input length sent to LLM is limited.
- [x] Reports and metadata are saved locally.
- [ ] Add PII masking before sending contract text to LLM.
- [ ] Add file size limits.
- [ ] Add PDF/DOCX support with validation.
- [ ] Add API authentication if deployed.

## Limitations

- Baseline supports `.txt` files only.
- RAG is deterministic and checklist-based.
- The model may miss legal risks.
- The agent should not be used as the only source for signing decisions.

## Future improvements

- PDF/DOCX support.
- OCR for scanned contracts.
- Vector RAG with FAISS/Chroma.
- Pydantic structured output validation.
- LLM-as-judge evals.
- Streamlit UI or Telegram bot.
- Export report to PDF.
