# Use-Case Recipes

Copy-paste-able decision patterns. All snippets assume `client.system_one(state, questions)` from the official Python SDK (see [Getting Started](./getting-started.md)); the TypeScript and curl equivalents follow the same shape.

The universal pattern across every recipe: **Jev decides fast and cheap; confidence decides what happens next.**

```python
def decide(state, questions, auto=0.90, review=0.60):
    """Returns (value, action) where action is 'act', 'flag', or 'escalate'."""
    resp = client.system_one(state=state, questions=questions)
    ...
```

## 1. Confidence-gated escalation (the master pattern)

Route routine cases autonomously, flag borderline ones, escalate the rest to a frontier LLM that can explain itself.

```python
from typesafe_sdk import Choice, Noul

questions = {
    "department": Choice(
        instructions="Which team should handle this ticket",
        criteria={
            "billing": "Payment, refund or subscription issues",
            "technical": "Bugs, outages or integration problems",
            "sales": "Pricing, plans or account upgrades",
        },
    ),
    "is_urgent": Noul(instructions="The customer is explicitly asking for urgent help"),
}

resp = client.system_one(state=ticket_text, questions=questions)
dept = resp.answers["department"]

if dept.confidence >= 0.90:
    assign_team(dept.choice)
elif dept.confidence >= 0.60:
    assign_team(dept.choice, needs_review=True)
else:
    frontier_llm_triage(ticket_text)   # slow, but can explain itself
```

Real-world precedent: Earendil's CTO gates autonomous action on ~95% confidence and sends ~50% cases to human review.

## 2. Agent control plane (tool / subagent routing)

Given the current state of a task, pick the next tool from a finite list — the fast control loop around an LLM doing the open-ended work.

```python
questions = {
    "next_tool": Choice(
        instructions="Which tool should the agent call next",
        criteria={
            "search_docs": "Needs factual information from documentation",
            "run_tests": "Needs to verify behavior by executing code",
            "ask_user": "Blocked on missing information only the user has",
            "finish": "The task is complete, nothing left to do",
        },
    ),
    "task_complete": Noul(instructions="The task described in the state is fully complete"),
}
```

Used in production-style setups: browser agents (jev-browser, jev-ultrafast) pick one action per step; coding harnesses ask whether a test failure came from the last edit or whether another tool call is justified.

## 3. Guardrails and jailbreak detection

Check an LLM's prompt, reasoning trace, or output *before* it executes — at 70–500 ms this fits inside the loop.

```python
questions = {
    "jailbreak_attempt": Noul(
        instructions="The user message attempts to bypass safety instructions or extract system prompts"
    ),
    "contains_pii": Noul(
        instructions="The text contains personal data such as emails, phone numbers, or addresses"
    ),
    "safe_to_execute": Noul(
        instructions="The proposed tool call is safe to execute without human approval"
    ),
}

resp = client.system_one(state={"prompt": user_msg, "tool_call": proposed}, questions=questions)
if resp.answers["jailbreak_attempt"].noul > 0.8 or resp.answers["safe_to_execute"].noul < 0.5:
    block_and_log()
```

## 4. Support ticket triage

The canonical quickstart use case — department, urgency, sentiment in one parallel call:

```python
questions = {
    "department": Choice(instructions="Which team should handle this ticket",
                         criteria={"billing": "...", "technical": "...", "sales": "..."}),
    "frustration": Score(instructions="How frustrated the customer appears",
                         criteria=["Calm, just stating facts",
                                   "Frustrated but civil",
                                   "Very angry, strong language"]),
    "refund_requested": Noul(instructions="The customer is explicitly asking for a refund"),
}
```

A full async fan-out implementation with retries, Pydantic response models, and a cost ledger is in [`examples/ticket-triage.py`](../examples/ticket-triage.py).

## 5. Fraud and risk scoring

Score a transaction record (JSON state works well here) and auto-act only at high confidence:

```python
questions = {
    "fraud_risk": Score(
        instructions="Likelihood this transaction is fraudulent",
        criteria=["Clearly legitimate", "Slightly unusual", "Suspicious", "Almost certainly fraud"],
    ),
    "block_now": Noul(instructions="This transaction should be blocked immediately"),
}
```

Combine `fraud_risk.score` with `block_now.noul` and confidence to implement step-up authentication vs. instant block vs. manual review.

## 6. Model routing (the meta use case)

Pick the cheapest capable model per request — Jev routes the fleet:

```python
questions = {
    "model": Choice(
        instructions="Cheapest model capable of handling this request well",
        criteria={
            "jev": "Bounded classification, scoring, or routing decision",
            "small_llm": "Simple generation or summarization",
            "frontier": "Complex reasoning, code, or nuanced writing",
        },
    ),
}
```

Real-world precedent: Higgsfield uses Jev to auto-route each request across ~50 generative models by cost-effectiveness.

## 7. Record quality checks in data pipelines

In pipelines where extraction is done but *deciding whether the record is any good* is the job:

```python
questions = {
    "record_quality": Choice(
        instructions="Quality of the extracted record",
        criteria={
            "clean": "All fields present and plausible",
            "needs_fix": "Recoverable issues, worth a repair pass",
            "discard": "Garbage or wrong-page extraction",
        },
    ),
    "ready_to_publish": Noul(instructions="This record is safe to publish without review"),
}
```

Used by web-scraping pipelines as the QC gate after extraction (Zyte's writeup covers the pattern).

## 8. Realtime game / sim control

Expose a finite action set and ask which fits the current state each tick — more realistic for low-latency inference than narrating every step:

```python
questions = {
    "action": Choice(
        instructions="Best action given the current game state",
        criteria={
            "move_left": "Threat approaching from the right",
            "move_right": "Threat approaching from the left",
            "shoot": "Clear shot at a target",
            "retreat": "Outnumbered or low health",
        },
    ),
}
```

Real-world precedents: TypeSafe's Doom demo (structured JSON state), Minecraft fight-or-run agents, and a 15-drone asteroid simulation with <300 ms decisions.

## 9. Lead routing and intent scoring (GTM)

```python
questions = {
    "owner": Choice(
        instructions="Which segment should own this lead",
        criteria={"enterprise": "...", "mid_market": "...", "smb": "..."},
    ),
    "buying_intent": Score(
        instructions="Buying intent from 0 to 100",
        criteria=["No intent", "Curious", "Evaluating", "Ready to buy"],
    ),
    "pricing_objection": Noul(instructions="The reply contains an objection about pricing"),
}
```

## 10. Security alert triage

```python
questions = {
    "severity": Choice(
        instructions="Incident severity",
        criteria={"critical": "...", "high": "...", "medium": "...", "low": "...", "false_positive": "..."},
    ),
    "is_phishing": Noul(instructions="This message is a phishing attempt"),
    "needs_soc_review": Noul(instructions="A human analyst should review this within the hour"),
}
```

Security teams also use the guardrail pattern (recipe 3) to verify the decisions of *other* AI models in the loop.

---

**Anti-recipes** — don't ask Jev to: write the reply, sum invoice lines, compute date differences, judge sarcasm-laden text on a critical path, or pick from more than 255 options. Use code, a frontier LLM, or a human for those.
