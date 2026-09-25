# Jev vs Generative LLMs — Where Each Layer Wins

The most common confusion about Jev: *"Why not just use an LLM in JSON mode?"* They're different layers.

| | Generative LLM | LLM with structured output | Jev (System One) |
| --- | --- | --- | --- |
| **Primary output** | Open-ended text or code | Generated values constrained to a schema | Bounded decisions and distributions |
| **Answer space** | Open | Schema-shaped but generative | Defined in the request |
| **Main role** | Explain, plan, synthesize, create | Put a generative result into application types | Classify, score, route, rank, gate |
| **Evaluation** | Sequential token generation | Constrained token generation | All questions answered in parallel |
| **Uncertainty** | Expressed in prose or self-reported | Provider- and application-dependent | Probability distribution; confidence on Choice/Score |
| **Failure mode** | Invents facts, breaks schema | Valid shape, possibly wrong content | Picks the wrong valid option |
| **Valid shape ⇒ correct meaning** | No | No | No |
| **Latency** | 3–329 s on reasoning tasks | Similar, slightly less | 70–500 ms |
| **Input price** | $0.20–$10 / MTok | Same | $0.042 / MTok |
| **Output price** | ~5× input | Same | Free |

## The deeper difference

An LLM in JSON mode still **generates the path to the structure** — tokens are sampled one at a time, then parsed, then validated. Jev's answer space is **constrained at the model interface itself**: there is no generation phase, so there is nothing to parse and nothing that can break schema.

```
LLM + structured output:   generate tokens → parse → validate → use
Jev:                       evaluate typed questions → receive typed answers → use
```

That changes how much compute is spent producing the answer — which is where the speed and cost advantage comes from.

## They compose, not compete

The realistic architecture, and the one TypeSafe itself recommends:

- **Jev as the fast decision layer** — routing, triage, gating, scoring at high volume, with confidence thresholds deciding what auto-acts.
- **Frontier LLM for the open-ended work** — writing, explaining, reasoning, handling everything below Jev's confidence threshold.

In practice: *Jev decides which cases need the expensive model*, and the expensive model only sees the cases that need it.

## When Jev is the wrong tool

- You need generated text, code, summaries, or explanations
- The decision requires multi-step reasoning, arithmetic, or date logic
- The input is sarcastic, adversarial, or relies on indirection — without human review on low confidence
- You need image/audio/video understanding (transcribe first, or use another model)
- You need a public benchmark pedigree or compliance certifications it doesn't have yet
