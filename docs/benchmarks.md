# Benchmarks & Evaluations — An Honest Scorecard

TypeSafe's launch numbers are loud; the independent evidence is early. This page keeps both, clearly labeled.

## TypeSafe's own claims (company-reported)

From the September 15, 2026 launch post, based on **four in-house "workflow evals"**:

| Claim | Value | Caveat |
| --- | --- | --- |
| Speedup vs frontier LLMs | **193.6× faster** | High end of the four workflows; **average across all eight setups: 97.8×** |
| Cost reduction | **444.6× cheaper** | High end; **average: 149.2×**. Fits Jev vs Opus 5 in the workflow setup specifically |
| Eval accuracy | **67.8%** | Equal to Sonnet 5; GPT-5.6 Sol leads at 74.1%. Invoice processing: Jev 61.8% vs Sol 79.1% |
| Hallucination rate | **0%** | TypeSafe's own words: *"Our number is not empirical. Schema matching is guaranteed."* — it's a schema guarantee, not an accuracy measurement |
| Latency | 70–500 ms | End-to-end, vs 3–329 s for frontier LLMs on the cited reasoning tasks |

Methodological notes TypeSafe itself discloses:

- Workflows *"were made by individuals on our model capabilities team, so some bias could exist"*
- Reference labels are *"an average of the responses of GPT-6 Astra and Claude Fable 5.1, both at high thinking"* — **agreement with two LLMs, not verified ground truth**. If both reference models are wrong, Jev can "win" while being wrong
- The LLM comparators ran through TypeSafe's own probability adapter, which the company says is *"slower and more expensive"*; the comparator models are never named
- Timings came from laptops on the US West Coast; no case counts, run counts, or variance published
- TypeSafe chose to publish **no public-benchmark results**

## Independent checks

Early, task-specific, and worth more than the marketing numbers:

- **TrueStandard** — confirmed the calibration property holds (accuracy rises meaningfully in higher-confidence buckets). Measured roughly **1.7× faster** than a comparable LLM call for a single decision, reaching **~100×** on a multi-step workflow in one test configuration. The 193× figure reflects specific workflow types, not everything.
- **Rafe & Das preprint, *Calibrated Decisions at Scale* (Sept 2026)** — coded 499,500 police-crash narratives with Jev 1.13, full schema on 195,857, evaluated against 2,416 human judgments. Pooled **F1 0.908**, but raw probabilities **failed** the study's calibration checks; out-of-fold recalibration cut expected calibration error from **0.0231 → 0.0069**. Four variables had F1 below 0.70. One generative comparator scored higher overall; another was statistically indistinguishable.
- **12,000 real RFQs: Jev vs Qwen3.5-35B vs Laya 421M (Sept 2026)** — ground truth from actual quoting behavior:
  | | Primary accuracy | Calibration error | Auto-accepted at 95% precision target |
  | --- | --- | --- | --- |
  | Jev (jev-1.13.0) | **91.9%** | **0.049** | **86.5%** |
  | Qwen3.5-35B (JSON mode) | 89.6% | n/a | not reached |
  | Laya 421M | 78.0% | 0.322 | not reached |
  Qwen produced **69 permanently malformed responses**; the decisive gap was calibration, not the 2.3-point accuracy lead.
- **Eight-day independent review (Sept 2026)** — verdict: *levels with mid-price LLMs, behind the frontier*. Jaggedness examples: one request returned "suspend" for an account the same response classified as a developer sending tests; "refund" scored 0.72 vs "not a refund" 0.47 on the same ticket.

## Field reports

- **Vercel** (engineer Pranit Sharma) — command-safety checks: 5–18× faster than ChatGPT Luna 5.6 with improved classification accuracy
- **Bryo AI** (CTO Nikhil Mudholkar) — business-correspondence classification vs Gemini: slightly less accurate, **10–20× cheaper**; calibrated confidence triggers automated workflows
- **Earendil** (CTO Armin Ronacher) — confidence scores allocate responsibility: ~50% → human review, ~95% → autonomous action
- **Hacker News launch thread** (Sept 15, 2026) — 1,900+ points, 509 comments; broadly positive on the core idea, skeptical on "frontier model" framing and benchmark independence
- **Demand** — TypeSafe briefly lost the ability to serve API users at launch; signups opened Sept 20 ($5 free credit) and paused Sept 22

## How to read all of this

1. The speed/cost advantage is real but workload-dependent; the headline 193×/444× are high-end, not typical.
2. "Can't hallucinate" means "can't emit an invalid type." The wrong-but-valid rate is the accuracy column above.
3. Calibration is the actual moat — the one property the open-source clones haven't reproduced — and even it needed recalibration in the one rigorous study so far.
4. Qualify a **model–schema–population combination for a particular decision**, not the model category in general.
