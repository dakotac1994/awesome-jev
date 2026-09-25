# Examples

Runnable Jev examples. Everything runs **offline** with `--demo` (a built-in mock that prints the request shape it *would* send) — no API key needed. Drop `--demo` and set `TYPESAFE_API_KEY` for live calls.

| File | What it shows |
| --- | --- |
| [`curl.sh`](./curl.sh) | Raw HTTP: `POST https://api.typesafe.ai/v1/systemone` |
| [`quickstart.py`](./quickstart.py) | One state, three typed questions (Choice, Score, Noul) in one parallel pass |
| [`confidence_gate.py`](./confidence_gate.py) | Confidence-gated escalation: auto-act / flag / escalate to a frontier LLM |
| [`ticket_triage.py`](./ticket_triage.py) | Async fan-out over 12 tickets, Pydantic response models, `RetryPolicy`, usage ledger |
| [`js/quickstart.mjs`](./js/quickstart.mjs) | Same quickstart in TypeScript (`@typesafe-ai/sdk`) |

```bash
python quickstart.py --demo
python confidence_gate.py --demo
python ticket_triage.py --demo
sh curl.sh            # needs TYPESAFE_API_KEY
```
