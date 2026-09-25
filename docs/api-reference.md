# Jev API Reference (Community Summary)

Unofficial summary of the public Jev API as documented by TypeSafe AI and reported by early users (September 2026). For the authoritative contract, see TypeSafe's official documentation at [typesafe.ai](https://typesafe.ai).

## Endpoint

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json
```

One endpoint. Every call sends a state plus a map of questions.

## Request

| Field | Type | Description |
| --- | --- | --- |
| `model` | string | Model alias. `jev-latest` currently resolves to `jev-1.13.0` |
| `state` | string \| object \| array | The situation to evaluate. Text only — no images, audio, or video |
| `questions` | object | Map of question name → question definition. All evaluated in parallel |

### Question types

**Choice** — pick exactly one option from a set you define (up to 255 options):

```json
{
  "type": "choice",
  "instructions": "Which team should handle this",
  "criteria": {
    "billing": "Payment or subscription issues",
    "technical": "Bugs or integration problems",
    "sales": "Pricing or account questions"
  }
}
```

**Score** — rate against ordered levels you define:

```json
{
  "type": "score",
  "instructions": "How frustrated the customer appears",
  "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]
}
```

**Noul** — yes/no probability for a statement:

```json
{
  "type": "noul",
  "instructions": "The message conveys urgency or time-sensitivity"
}
```

Questions are evaluated **in parallel and in isolation** against the same state, so adding a question barely changes response time. Behavior is shaped through `instructions` and `criteria` — there is no fine-tuning.

## Response

```json
{
  "answers": {
    "department": {
      "choice": "technical",
      "probabilities": { "billing": 0.159, "technical": 0.84, "sales": 0.001 },
      "confidence": 0.596
    },
    "frustration": { "score": 1.035, "confidence": 0.842 },
    "is_urgent": { "noul": 0.999 }
  },
  "usage": { "input_tokens": 312, "output_tokens": 48 }
}
```

| Field | Description |
| --- | --- |
| `answers.<name>.choice` | The selected option key (exactly one of your declared options) |
| `answers.<name>.probabilities` | Full distribution over your options (Choice) or levels (Score) |
| `answers.<name>.score` | Numeric rating (Score) |
| `answers.<name>.noul` | Probability 0–1 that the statement is true (Noul) |
| `answers.<name>.confidence` | Separate confidence value (Choice/Score) — use as the act-vs-escalate axis |
| `usage` | Token counts. Output tokens are not billed |

There is no text to parse and nothing to validate — the answer space was declared by you in the request, so schema matching is guaranteed. (Guaranteed *shape*, not guaranteed *correctness*.)

## Limits

- 64k tokens per request; 32k reserved for state + longest single question
- Up to 255 options per Choice
- Text input only; English is the primary training language
- Early-access rate limits apply; TypeSafe briefly hit capacity limits at launch under demand

## SDK surface (Python)

From the official `typesafe-sdk` package:

- `TypeSafeClient` / `AsyncTypeSafeClient` — `system_one(state, questions, ...)`; key from `TYPESAFE_API_KEY`
- Question builders: `Choice(instructions=..., criteria={...})`, `Score(instructions=..., criteria=[...])`, `Noul(instructions=...)`
- Typed responses: subclass `SystemOneResponse` and declare `department: ChoiceAnswer`, etc. — Pydantic-validated attribute access, no dict lookups
- `RetryPolicy(max_retries, backoff_initial, backoff_max, timeout)` for production fan-out
- Errors are typed: `TypeSafeError` (client-side, e.g. empty questions — caught before any request) and `TypeSafeAPIError` (server-side, with HTTP status)

## Gateway equivalents

Through gateways the model appears under provider-specific IDs — `typesafe-ai/jev` (Vercel AI Gateway), `typesafe/jev-1.13` (OpenRouter) — but the typed-question contract is the same.
