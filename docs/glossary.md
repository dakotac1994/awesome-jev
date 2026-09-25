# Glossary

Terms you'll meet around Jev and System One models.

- **System One model** — TypeSafe's category name for models that make fast, structured decisions software can consume directly, instead of generating text. Borrowed from Daniel Kahneman's *Thinking, Fast and Slow*: System 1 is fast, associative judgment; System 2 is slow, deliberate reasoning. Jev is the first public example.

- **Jev** — TypeSafe AI's first System One model (early access, Sept 15, 2026). Named as a nod to Jevons Paradox, after economist William Stanley Jevons. Production alias `jev-latest` → `jev-1.13.0`.

- **Choice** — A Jev question primitive: pick exactly one option from up to 255 predefined options. Returns the selected option, a probability per option, and confidence.

- **Score** — A Jev question primitive: rate a situation against ordered levels you define. Returns a score, a probability per level, and confidence.

- **Noul** — A Jev question primitive: a yes/no question returning a single probability (0–1) that the statement is true. (Pronounced like "knoll"; think "null/yes-no" — TypeSafe's term for the binary primitive.)

- **State** — The input situation Jev evaluates: a text string, JSON object, or array. All questions in a request are evaluated against the same state, in parallel.

- **Typed question** — A question with a fixed answer space declared in advance. No strings are ever generated; outputs are bounded choices, scores, and yes/no probabilities.

- **RLCD** — Reinforcement Learning for Calibrated Decisions. TypeSafe's training regime for Jev: it rewards the model when its stated probabilities match how often it's actually right. Contrast with RLHF (optimizes for human preference) and RLVR (optimizes for verifiable correctness). No paper published as of Sept 2026.

- **Calibration** — The property that stated confidence matches empirical accuracy: a model saying 0.73 should be right ~73% of the time. The core of Jev's value proposition — it turns the score into a routing signal for auto-act vs. escalate.

- **Expected calibration error (ECE)** — A metric for how far stated probabilities deviate from observed accuracy. The Rafe & Das study reported Jev's raw ECE at 0.0231, reduced to 0.0069 after out-of-fold recalibration.

- **Confidence** — A per-answer value, separate from the answer itself, that TypeSafe's docs recommend using as the *whether to act* axis (the answer is the *what*).

- **Parallel sampling** — Jev's inference design: all questions over a state are evaluated simultaneously in a single forward pass, with no autoregressive token-by-token loop. The source of its latency advantage.

- **Confidence-gated escalation** — The canonical Jev architecture: act autonomously above a confidence threshold, flag borderline cases, escalate low-confidence cases to a frontier LLM or a human.

- **Type-safe (in the Jev sense)** — The guarantee that outputs always match the declared answer space. Not a correctness guarantee: the model can still pick the wrong valid option.

- **Pareto frontier** — In TypeSafe's launch materials, the claim that Jev dominates the speed-vs-cost tradeoff curve on workflow-centric automation tasks. Independent verification is pending.
