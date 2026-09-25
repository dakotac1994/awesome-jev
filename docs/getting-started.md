# Getting Started with Jev

Get from zero to your first typed decision in about ten minutes.

## 1. Get access

Jev is served through TypeSafe's hosted API. Access is early access:

- Direct API access historically required a **waitlist invite**. On **September 20, 2026**, TypeSafe opened signups to everyone with **$5 in free credit**, then **paused new signups on September 22** under demand.
- **No-signup alternatives:** Vercel AI Gateway (`typesafe-ai/jev`), OpenRouter (`typesafe/jev-1.13`), Cloudflare Workers AI, Netlify AI Gateway, and LiteLLM all offer pass-through access.

Check the [README](../README.md#gateway--platform-integrations) for gateway details. When signups reopen, grab an API key and export it:

```bash
export TYPESAFE_API_KEY="ts_..."
```

## 2. Install an SDK

**Python** (3.10+):

```bash
pip install typesafe-sdk
```

**JavaScript/TypeScript**:

```bash
npm install @typesafe-ai/sdk
```

## 3. Make your first decision

The mental model: you don't prompt Jev, you **declare a decision**. Every request has:

- **`state`** — the situation to judge: a text string, a JSON object, or an array.
- **`questions`** — a map of named, typed questions. Each is a `Choice`, `Score`, or `Noul`.
- **`model`** — the alias `jev-latest` (currently resolves to `jev-1.13.0`).

Python:

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()  # reads TYPESAFE_API_KEY from the environment

response = client.system_one(
    state={
        "ticket_message": "Hi, I've been trying to connect my Stripe account "
                          "for 3 days and it keeps failing. I'm losing sales. "
                          "Please help ASAP."
    },
    questions={
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "billing": "Payment or subscription issues",
                "technical": "Bugs or integration problems",
                "sales": "Pricing or account questions",
            },
        ),
        "frustration": Score(
            instructions="How frustrated the customer appears",
            criteria=["Calm, just stating facts",
                      "Frustrated but civil",
                      "Very angry, strong language"],
        ),
        "is_urgent": Noul(
            instructions="The message conveys urgency or time-sensitivity"
        ),
    },
)

print(response.answers["department"].choice)    # e.g. "technical"
print(response.answers["frustration"].score)   # e.g. 1.035
print(response.answers["is_urgent"].noul)       # e.g. 0.999
```

All three questions are answered **in one parallel pass** — adding a question barely changes latency.

## 4. Use confidence as a second axis

Every answer carries confidence, separate from the value itself. TypeSafe's docs recommend:

- The **answer** tells you *what*.
- The **confidence** tells you *whether to act on it*.

The canonical production pattern — **confidence-gated escalation**:

```python
AUTO_ACT_THRESHOLD = 0.90
REVIEW_THRESHOLD = 0.60

dept = response.answers["department"]
if dept.confidence >= AUTO_ACT_THRESHOLD:
    route_ticket(dept.choice)                    # act autonomously
elif dept.confidence >= REVIEW_THRESHOLD:
    route_ticket(dept.choice, flag="low-confidence")  # act, but flag
else:
    escalate_to_frontier_llm(ticket)             # hand to the slow model
```

This is the architecture Jev is designed for: Jev as the fast, cheap decision layer handling routine cases, escalating anything below a threshold to a slower model that can explain itself. See [recipes.md](./recipes.md) for full patterns.

## 5. Go async for volume

The Python SDK ships `AsyncTypeSafeClient` for concurrent fan-out, plus `RetryPolicy` and typed errors. A runnable example with retries, typed Pydantic response models, and a usage ledger is in [`../examples/ticket_triage.py`](../examples/ticket_triage.py).

## 6. Know the limits before you ship

- **Text only**, English-first. Transcribe/preprocess images, audio, video first.
- **Literal reader**: avoid sarcasm, double negatives, adversarial phrasing on critical paths.
- **No arithmetic**: don't ask it to sum lines or diff dates — use code.
- **64k token context** (32k for state + longest question); **255 options** max per Choice.
- **Not trained on your data**, not fine-tuned per account — steer it with instructions and criteria.
- Validate thresholds on *your* data with a labeled eval set before trusting auto-action.

Next: [API Reference](./api-reference.md) · [Use-Case Recipes](./recipes.md) · [Benchmarks](./benchmarks.md)
