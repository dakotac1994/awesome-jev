# Awesome Jev

> A curated list of resources for **Jev** — TypeSafe AI's decision-only "System One" model that returns typed decisions with calibrated probabilities instead of generating text.

Jev doesn't write. You send it a state (text or JSON) plus a map of typed questions — `Choice`, `Score`, or `Noul` — and it evaluates every question in one parallel pass, returning typed values with probabilities and confidence your code can branch on directly. Launched in early access on **September 15, 2026**, it's the first model in a new category TypeSafe calls **System One models** (a nod to Kahneman's fast, intuitive System 1 thinking).

![Awesome](https://awesome.re/badge.svg)
[![CI](https://github.com/dakotac1994/awesome-jev/actions/workflows/ci.yml/badge.svg)](https://github.com/dakotac1994/awesome-jev/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Contents

- [What is Jev?](#what-is-jev)
- [The Three Primitives](#the-three-primitives)
- [Quickstart](#quickstart)
- [Specifications](#specifications)
- [Official Resources](#official-resources)
- [SDKs & Client Libraries](#sdks--client-libraries)
- [Gateway & Platform Integrations](#gateway--platform-integrations)
- [How It Works](#how-it-works)
- [Benchmarks & Evaluations](#benchmarks--evaluations)
- [Limitations & Failure Modes](#limitations--failure-modes)
- [Use Cases](#use-cases)
- [Community Projects](#community-projects)
- [Open-Source Ecosystem & Clones](#open-source-ecosystem--clones)
- [Articles & Explainers](#articles--explainers)
- [Comparisons](#comparisons)
- [FAQ](#faq)
- [Contributing](#contributing)

## What is Jev?

**TypeSafe AI** (San Francisco) emerged from two years of stealth on September 15, 2026, with **$40M in seed funding led by DCVC**, announcing Jev — the first of what it calls *System One models*. Founded in 2024 by **Diogo Almeida** (CEO; former OpenAI researcher, co-inventor of RLHF and InstructGPT) with **Erik Gafni** and **Sasha Sheng**.

The thesis: large frontier models are optimized for *talking to people*, but production software needs *intelligence software can consume directly*. A decision layer shouldn't generate a paragraph you then parse, validate, and constrain — it should return the decision itself. Jev reads natural-language or JSON state, and instead of generating tokens, fills in a developer-defined answer space: a choice from your options, a score on your scale, or a yes/no probability — each with calibrated confidence.

The name is a nod to **Jevons Paradox**, after 19th-century economist William Stanley Jevons.

Key properties:

- **No text generation.** There is no string output at all — no replies, no code, no explanations.
- **Parallel questions.** Ask 20 questions about the same state in one call; they're evaluated simultaneously in a single forward pass.
- **Calibrated probabilities.** Trained with RLCD (Reinforcement Learning for Calibrated Decisions) so stated confidence matches actual accuracy — the signal you use to auto-act or escalate.
- **Type-safe by construction.** The answer space is declared in the request, so the response can never be a malformed schema or an invented option. (Wrong-but-valid decisions are still possible — see [Limitations](#limitations--failure-modes).)
- **Fast and cheap.** 70–500 ms latency; $0.042 per million input tokens; output tokens free.

> This list is a community resource, not affiliated with TypeSafe AI. Company figures are TypeSafe's own claims unless marked independent — the [Benchmarks](#benchmarks--evaluations) section keeps score honestly.

## The Three Primitives

Every question you ask is one of exactly three typed question kinds:

| Primitive | Question shape | Returns | Example |
| --- | --- | --- | --- |
| **Choice** | Pick one of up to 255 predefined options | Selected option, probability per option, confidence | `"Which team owns this ticket?" → billing / technical / sales` |
| **Score** | Rate against ordered levels you define | Score, probability per level, confidence | `"How frustrated is this customer?" → 1.035` |
| **Noul** | Is this statement true? (yes/no) | Single probability 0–1 | `"Does this request a refund?" → 0.999` |

All questions in one request are evaluated **in parallel and in isolation against the same state**, so adding a question barely changes response time.

## Quickstart

One endpoint, one request shape:

```bash
curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jev-latest",
    "state": "Help! My payments have been failing for 3 days and nobody answers support.",
    "questions": {
      "is_urgent": {
        "type": "noul",
        "instructions": "Does this message express urgency?"
      },
      "department": {
        "type": "choice",
        "instructions": "Which team should handle this?",
        "criteria": {
          "billing": "Payments, invoicing, refunds",
          "technical": "Bugs, outages, integrations",
          "sales": "Pricing, upgrades, new accounts"
        }
      }
    }
  }'
```

Python (official SDK):

```bash
pip install typesafe-sdk
```

```python
from typesafe_sdk import Choice, Noul, TypeSafeClient

client = TypeSafeClient()  # reads TYPESAFE_API_KEY
response = client.system_one(
    state="My payout has been delayed for three days. Please help ASAP.",
    questions={
        "is_urgent": Noul(instructions="Does this convey urgency?"),
        "department": Choice(
            instructions="Which team should handle this?",
            criteria={
                "billing": "Payments, invoicing, refunds",
                "technical": "Bugs, outages, integrations",
            },
        ),
    },
)
print(response.answers["is_urgent"].noul)       # 0.999
print(response.answers["department"].choice)    # "billing"
```

TypeScript (official SDK):

```bash
npm install @typesafe-ai/sdk
```

```ts
import { TypeSafeClient, Choice, Noul } from '@typesafe-ai/sdk';

const client = new TypeSafeClient({ apiKey: process.env.TYPESAFE_API_KEY });
const result = await client.systemOne({
  state: 'My payout has been delayed for three days. Please help ASAP.',
  questions: {
    isUrgent: Noul({ instructions: 'Does this convey urgency?' }),
    department: Choice({
      instructions: 'Which team should handle this?',
      criteria: {
        billing: 'Payments, invoicing, refunds',
        technical: 'Bugs, outages, integrations',
      },
    }),
  },
});
console.log(result.answers.isUrgent.noul);
console.log(result.answers.department.choice);
```

A typical response:

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

There is no text to parse. `department.choice` is one of the keys you supplied; `is_urgent.noul` is a float you threshold. Confidence is a separate axis from the answer — the docs recommend using the answer to know *what*, and confidence to decide *whether to act on it*.

Runnable examples (with an offline `--demo` mock mode, no key needed): [`examples/`](./examples/).

Deeper guides: [Getting Started](./docs/getting-started.md) · [API Reference](./docs/api-reference.md) · [Use-Case Recipes](./docs/recipes.md)

## Specifications

| Property | Value |
| --- | --- |
| Model alias | `jev-latest` → `jev-1.13.0` |
| Endpoint | `POST https://api.typesafe.ai/v1/systemone` |
| Input | State: text string, JSON object, or array. Questions: map of named Choice/Score/Noul |
| Context | 64k tokens per request (32k reserved for state + longest single question) |
| Choice options | Up to 255 per question |
| Latency | 70–500 ms end-to-end (TypeSafe, Sept 2026) |
| Pricing | **$0.042 / million input tokens; output tokens free** |
| Modalities | Text only — no images, audio, or video |
| Primary language | English (other languages accepted with lower accuracy, per docs) |
| Training on customer data | No — Jev is not trained on customer requests; no per-account fine-tuning |
| Access | Early access via hosted API; signups opened to all Sept 20, 2026 with $5 free credit, then **paused Sept 22** under demand. Gateway pass-throughs (below) need no TypeSafe signup |

## Official Resources

- [typesafe.ai](https://typesafe.ai) — company homepage; host of the official launch post (*Introducing System One Models & Jev*, Sept 15, 2026), the API documentation (quickstart, primitives, confidence guidance), and TypeSafe's own *Where Jev Actually Fails* page
- [Launch post on X — @CompleteSkeptic](https://x.com) — the launch thread (39M+ views per case study)
- [Latent Space: Jev — System One Models for Prod, Not God](https://www.latent.space/p/jev) — podcast interview with Diogo Almeida (Sept 21, 2026)

## SDKs & Client Libraries

- [PyPI](https://pypi.org) — `typesafe-sdk`: official Python SDK (`pip install typesafe-sdk`; Python 3.10+; `TypeSafeClient`, `AsyncTypeSafeClient`, Pydantic `ChoiceAnswer`/`ScoreAnswer`/`NoulAnswer` response models, `RetryPolicy`, typed errors)
- [npm](https://www.npmjs.com) — `@typesafe-ai/sdk`: official JavaScript/TypeScript SDK (`npm install @typesafe-ai/sdk`)
- **langchain-typesafe** — **official LangChain integration** package, wiring Jev decisions into existing chains

## Gateway & Platform Integrations

Access Jev without a TypeSafe signup through these pass-through providers:

- [Vercel AI Gateway](https://vercel.com) — model ID `typesafe-ai/jev`, via AI SDK 7's `evaluate`
- [OpenRouter](https://openrouter.ai) — beta listing `typesafe/jev-1.13`
- [Cloudflare Workers AI](https://developers.cloudflare.com) — via `env.AI.run`
- [Netlify AI Gateway](https://www.netlify.com) — zero-config from Netlify Functions
- [LiteLLM](https://www.litellm.ai) — proxy pass-through

## How It Works

Jev is a transformer-based model with a new architecture and a parallel sampler — but TypeSafe keeps the internals close. What is public:

- **Parallel, single-pass evaluation.** An LLM answers token *n+1* from token *n*; Jev has no ordering constraint, so every question over a state is scored simultaneously. That is where most of the speed comes from.
- **RLCD — Reinforcement Learning for Calibrated Decisions.** TypeSafe's training regime. The deliberate contrast from founder Diogo Almeida (who helped invent RLHF):
  - **RLHF** optimizes for human preference
  - **RLVR** optimizes for verifiable correctness
  - **RLCD** optimizes for **calibration** — the model's stated probabilities match how often it's actually right
- **No paper (yet).** As of September 2026 the architecture and RLCD loss are unpublished; Almeida has said a paper is possible. Treat internals as a black box.
- **Synthetic training data.** Almeida confirmed on Latent Space that all of Jev's training data is synthetic.
- **Behavior is shaped in the request.** Instructions and criteria per question steer decisions — there is no fine-tuning or per-account weights.

See [docs/api-reference.md](./docs/api-reference.md) for request/response details and [docs/comparisons.md](./docs/comparisons.md) for how this differs from an LLM in JSON mode.

## Benchmarks & Evaluations

Company numbers first, independent checks second. Full breakdown in [docs/benchmarks.md](./docs/benchmarks.md).

**TypeSafe's own claims** (four in-house "workflow evals", published Sept 15, 2026):

- **193.6× faster / 444.6× cheaper** than frontier LLMs — at the *high end* of the four workflows; averaged across all eight setups: **97.8× faster / 149.2× cheaper**
- Reference labels are *"an average of the responses of GPT-6 Astra and Claude Fable 5.1, both at high thinking"* — i.e., agreement with two LLMs, not verified ground truth
- Eval accuracy: Jev **67.8%** (equal to Sonnet 5; GPT-5.6 Sol leads at 74.1%); invoice processing 61.8% vs Sol's 79.1%
- "0% hallucination": TypeSafe's own wording — *"Our number is not empirical. Schema matching is guaranteed."* Wrong-but-valid decisions remain the real error rate
- No public-benchmark results published by TypeSafe

**Independent checks** (early, task-specific):

- **TrueStandard** — confirmed calibration holds (accuracy rises in higher-confidence buckets); ~1.7× faster than a comparable LLM call for a single decision, up to ~100× on a multi-step workflow in one test configuration
- **Rafe & Das preprint, *Calibrated Decisions at Scale* (Sept 2026)** — coded 499,500 police-crash narratives with Jev 1.13; pooled F1 **0.908**, but raw probabilities failed calibration checks until out-of-fold recalibration (ECE 0.0231 → 0.0069); four variables had F1 < 0.70
- **12,000 real RFQs vs Qwen3.5-35B vs Laya 421M** (Sept 2026) — Jev: 91.9% primary accuracy, calibration error 0.049, auto-accepted 86.5% at a bounded 95% precision target; Qwen: 89.6% accuracy, 69 permanently malformed responses, precision target not reached
- **Eight-day independent review** (Sept 2026) — levels with mid-price LLMs, behind the frontier; flags jaggedness: one request returned "suspend" for an account the same response classified as a test sender; "refund" 0.72 vs "not a refund" 0.47 on the same ticket

## Limitations & Failure Modes

Honest constraints, drawn from TypeSafe's own docs and independent testing:

- **Not a replacement for frontier LLMs.** No chat, no code, no explanations, no images. It classifies, scores, routes, and gates; it never generates.
- **"Can't hallucinate" is a schema guarantee, not a correctness guarantee.** It will never emit a value outside your answer space — but it can confidently pick the wrong valid option.
- **Literal reader.** TypeSafe's failure-modes page lists: literal interpretation, sarcasm, double negatives, arithmetic and counting, dates, long irrelevant input, and adversarial phrasing.
- **Hard limits:** 255 options per Choice; ~64k context; text only; English-first accuracy.
- **No arithmetic.** Don't ask it to sum invoice lines or diff dates — use code.
- **Benchmarks are company-reported.** No public leaderboards; evals compare against LLM consensus, not ground truth.
- **Vendor risk.** Early-stage company, hosted-only API, no on-prem/VPC option found; no SOC 2 / ISO 27001 certifications listed as of Sept 2026. Enterprise zero-data-retention exists, but wrap calls in a swappable interface.
- **Launch pricing may not last.** Output tokens are "too cheap to meter" at launch; the founder openly says that can't be proven to be unsubsidized.

## Use Cases

The use cases that hold up sit *next to* an LLM rather than replacing it — Jev as the fast decision layer, the frontier model for the open-ended work. Full code recipes in [docs/recipes.md](./docs/recipes.md).

| Domain | What Jev decides |
| --- | --- |
| **Agentic control plane** | Next tool / subagent selection, stop–retry–escalate logic, whether a tool failure is transient, whether the task is complete |
| **Guardrails & judges** | Jailbreak detection on prompts/traces/outputs, PII checks, policy compliance gates, LLM-output verification |
| **Support & ops** | Ticket routing and triage, urgency scoring, frustration scoring, refund-request detection |
| **Trust & safety** | Spam/phishing detection, content moderation, alert triage, IOC classification, false-positive filtering |
| **Risk & fraud** | Transaction fraud scoring, churn risk, credit/vetting scores with confidence-gated auto-action |
| **Model routing** | Pick the cheapest capable model per request (e.g., Higgsfield auto-routes across 50 generative models) |
| **Go-to-market** | Lead routing (enterprise/mid-market/SMB), buying-intent scoring, objection detection in replies |
| **Security** | Vulnerability prioritization, credential-leak prioritization, incident routing, threat-attribution confidence |
| **Data pipelines** | Record-quality checks after extraction (e.g., web-scraping QC: "is this record any good?"), document classification |
| **Realtime control** | Game/browser agents picking from a finite action set per frame; drone/sim control loops |
| **Dev workflows** | Test-failure attribution ("caused by last edit?"), PR risk scoring, CI signal triage |

**Where it doesn't fit:** anything needing generated text, explanations, code, images, or deep multi-step reasoning; arithmetic and dates; sarcasm-heavy or adversarial input without human review on low confidence.

## Community Projects

Real things people built in the first week (Sept 15–24, 2026):

### Apps & showcases
- [Made with Jev](https://www.producthunt.com/products/made-with-jev) — Product Hunt collection: **186 builds in 8 categories** (browser agents, games, inbox triage…), with each builder's reported cost/speed
- [Jevable](https://www.theregister.com/devops/2026/09/23/shut-up-and-calculate-jevs-new-ai-primitives-for-coders/5298431) — FPV Ventures' Nikunj Kothari's gallery of prototype Jev apps posted on X (described in The Register's Jev writeup): "Urgency" spreadsheet columns, plain-English → fancy-prose translator, virtual outfit previews ($0.0011/decision, ~620 ms)
- [safer-with-jev.com](https://echai.ventures/feed/we-found-the-perfect-use-case-for-jev-auto-routing-genai-models-the-623) — Andre Landgraf's yes/no-gate showcase examples (via eChai's Jev roundup)

### Browser & agent control
- **jev-ultrafast** — the official **Browser Use** integration: dynamic indexed action space, two decisions per round trip, documented 7.1-second Google Flights run ([via Julian Goldie's open-source roundup](https://juliangoldieaiautomation.com/blog/is-jev-open-source/))
- **jev-browser** — by jkudish (MIT): browser automation as an **MCP server**, Jev picks one action per step ([roundup](https://juliangoldieaiautomation.com/blog/is-jev-open-source/))
- **jev-voice-browser** — by Moritz Kremb (MIT): voice-controls a real Chromium browser, Jev decisions + Playwright ([roundup](https://juliangoldieaiautomation.com/blog/is-jev-open-source/))
- [Vercel command-safety checks](https://www.omegatechnologysolutionsgroupinc.com/blog/typesafe-ais-jev-model-chooses-actions-not-words-ca35b3) — Vercel engineer Pranit Sharma: 5–18× faster than ChatGPT Luna 5.6, improved classification accuracy

### Games & realtime
- **Doom bot** — TypeSafe's launch demo: real-time Doom driven by Jev decisions over structured JSON game state (not vision)
- **Minecraft agents** — Vipul Sharma: agents ask Jev whether to fight or run from visible mobs, weapon, health; one broke off mid-fight as the odds turned
- **15-drone asteroid simulation** — Mahmoud: Jev steers each drone, <300 ms decisions, 100% survival
- **Chess / Tetris / League of Legends / Settlers of Catan** — community game hacks (chess entry lost to GLM 5.3 but far cheaper); Smash Bros. self-play for cents
- **jevchat** — "I turned Jev into a (lousy) chatbot": asks Jev which symbol comes next at every step, from an alphabet + stop option

### Production-flavored
- **Higgsfield** — auto-routes each request to the most cost-effective of 50 generative models using Jev
- **Bryo AI** (CTO Nikhil Mudholkar) — business-correspondence classification vs Gemini: slightly less accurate, 10–20× cheaper; calibrated confidence triggers automated workflows
- **Earendil** (CTO Armin Ronacher) — confidence-gated autonomy: ~50% confidence → human review, ~95% → autonomous action
- **Second-hand shopping agent** — per-listing buy/skip decisions in 406 ms
- **Postgres function** — `WHERE jev(people, 'could work from home')` — decision models as SQL predicates

## Open-Source Ecosystem & Clones

Jev itself is closed and hosted-only, but the tooling around it went open within days. The honest pattern: **open ecosystem, closed core** — every project still phones TypeSafe's endpoint for the actual decision.

- **OpenJev** — reads next-token logits directly from a frozen Qwen3.5-4B instead of autoregressive decode; drew 714 HN points three days after launch ([via Zyte's Jev writeup](https://www.zyte.com/blog/jev-the-model-that-cannot-write-a-word-and-where-it-fits-in-web-scraping-does-it/))
- **mini-jev** — similar approach; 0.909 accuracy on a multiple-choice benchmark vs Jev's 0.907 across 6,750 observations ([via AI Beat](https://ai-beat.github.io/news/2026/09/jev-agent-decision-layer/))
- **MLX parallel constrained decoding** — targets Apple Silicon with Qwen2.5-1.5B
- The gap the clones can't close: **calibration**. Logit rankings are preference signals, not calibrated probabilities — fine for fast classifiers, not for decision gates that hand off to humans at exactly the right threshold.

## Articles & Explainers

### Overviews
- [What Is Jev? TypeSafe's System One Model Explained — KuCoin](https://www.kucoin.com/blog/what-is-jev-ai-typesafe-system-one-model-explained)
- [What is Jev: TypeSafe AI's model that decides instead of writing — DEV](https://dev.to/devrchancay/what-is-jev-typesafe-ais-model-that-decides-instead-of-writing-1ndd)
- [TypeSafe AI Jev: An AI model that doesn't generate text – and is 200x faster — DEV](https://dev.to/saaro_net/typesafe-ai-jev-an-ai-model-that-doesnt-generate-text-and-is-200x-faster-1ggo)
- [What Is Jev? The AI Model That Refuses to Write Text — Offgrid Studio](https://offgridstudio.app/blog/what-is-jev-typesafe-system-one-model)
- [What Is Jev? TypeSafe AI's System One Model Explained — TestMu AI](https://www.testmuai.com/blog/what-is-jev/)
- [TypeSafe AI's Jev Is Not a Chatbot. It Is a Decision Engine — LLM Rumors](https://www.llmrumors.com/news/typesafe-ai-jev-system-one-model-use-cases)
- [Jev Puts AI Judgment Directly Inside Software — The Brief](https://www.thebrief.news/en/standard/article/21281/jev-puts-ai-judgment-directly-inside-software)
- [TypeSafe AI's Jev Model Chooses Actions, Not Words — Omega Tech](https://www.omegatechnologysolutionsgroupinc.com/blog/typesafe-ais-jev-model-chooses-actions-not-words-ca35b3)
- [TypeSafe JEV AI Decision Model: 193x Faster and Explains Every Output — Karmactive](https://www.karmactive.com/typesafe-jev-ai-decision-model-explainer-193x-speed/)
- [Jev Rapid Decision Engine: Automating Software in Real-Time — BinaryPH](https://binary.ph/2026/09/23/unveiling-jev-typesafe-ais-rapid-decision-engine-revolutionizing-software-automation/)
- [Shut up and calculate: Jev's new AI primitives for coders — The Register](https://www.theregister.com/devops/2026/09/23/shut-up-and-calculate-jevs-new-ai-primitives-for-coders/5298431)
- [What Is Jev? Why System One Models Matter for Enterprise AI — HatchWorks](https://hatchworks.com/blog/gen-ai/system-one-models-jev/)

### Technical deep dives & coding guides
- [A Coding Guide to TypeSafe AI Jev — MarkTechPost](https://www.marktechpost.com/2026/09/23/a-coding-guide-to-typesafe-ai-jev/)
- [A Coding Guide to TypeSafe AI Jev — Bytecore News](https://bytecorenews.com/a-coding-guide-to-typesafe-ai-jev-typed-decisions-calibrated-confidence-and-speculative-fan-out-with-a-system-one-model/)
- [Jev and System One models: typed decisions — Noze](https://www.noze.it/en/insights/jev-system-one-typed-decisions/)
- [What Is Jev? Inside TypeSafe's Decision-Only AI Model and Its Developer Use Cases — Firecrawl](https://www.firecrawl.dev/blog/what-is-jev)
- [What Is Jev? TypeSafe AI's New "Decision Model" Explained — Codecaf](https://codecaf.com/what-is-jev-typesafe-ais-new-decision-model-explained/)
- [Jev Does Not Replace the LLM. It Changes Who Owns the Decision — DEV](https://dev.to/miruky/jev-does-not-replace-the-llm-it-changes-who-owns-the-decision-3n6)
- [THIS AI MODEL DOESN'T WANT TO TALK TO YOU — DEV](https://dev.to/mahankenway/this-ai-model-doesnt-want-to-talk-to-you-od0)
- [Jev: The AI That Returns a Decision, Not a Paragraph — Sreenath Menon](https://sreenathmenon.com/blog/2026-09-20-jev-the-ai-that-returns-a-decision-not-a-paragraph/)

### Company & launch coverage
- [TypeSafe AI emerges from stealth with $40M — Tech Startups](https://techstartups.com/2026/09/16/typesafe-ai-an-ai-startup-founded-by-chatgpt-co-inventor-emerges-from-stealth-with-40m-to-build-ai-thats-100x-faster-and-cheaper/)
- [TypeSafe AI Emerges From Stealth With $40M — HPCwire/AIwire](https://www.hpcwire.com/aiwire/2026/09/16/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai/)
- [How Doomers Launched TypeSafe AI and Jev on X — Case Study](https://doomers.ai/work/typesafe-ai-case-study)
- [What Is TypeSafe Jev? The ChatGPT Co-Creator's Silent AI — Apex36](https://www.apex36tech.com/blog/what-is-typesafe-jev-the-chatgpt-co-inventors-silent-ai)
- [TypeSafe AI unveils Jev, up to 400× cheaper and 200× faster — DigestAI](https://digestai.news/story/typesafe-ai-unveils-jev-a-frontier-model-up-to-400-cheaper-and-200-faster)

### Critical & security perspectives
- [Jev After Eight Days of Independent Tests — DEV](https://dev.to/gde/jev-after-eight-days-of-independent-tests-level-with-mid-price-llms-behind-the-frontier-1kln)
- [Jev AI Limitations: What the 193x Benchmark Doesn't Measure — Silverthread Labs](https://www.silverthreadlabs.com/blog/jev-ai-benchmark-limitations)
- [Jev and System One Models: A Production Engineering Review — ContextOS](https://contextosai.com/blog/jev-system-one-models-when-ai-returns-decisions)
- [The Decision Layer Eating the Agent Harness — AI Beat](https://ai-beat.github.io/news/2026/09/jev-agent-decision-layer/)
- [Why Is Everyone Suddenly Talking About Jev? A Look From the Security Side — LinkedIn](https://www.linkedin.com/pulse/why-everyone-suddenly-talking-jev-look-from-security-side-onal-vbmge)
- [Jev, the model that cannot write a word, and where it fits in web scraping — Zyte](https://www.zyte.com/blog/jev-the-model-that-cannot-write-a-word-and-where-it-fits-in-web-scraping-does-it/)
- [We Tested a 35B LLM Against Typed-Decision Models on 12,000 Real RFQs — DEV](https://dev.to/cookies_c9dc8b91f33d29250/we-tested-a-35b-llm-against-typed-decision-models-on-12000-real-rfqs-confidence-changed-the-winner-56hh)

### Domain playbooks
- [Jev for GTM: What a $0.04 Decision Model Does to Your Sales Stack — MarketBetter](https://marketbetter.ai/blog/jev-for-gtm-decision-model-playbook/)
- [Jev by TypeSafe AI: System One Model Guide for Startups — SaaSCity](https://saascity.io/blog/system-one-models-jev-typesafe-ai-2026)
- [Jev System Model vs LLM for Developers — Injoys](https://injoys.com/en/articles/jev-system-one-model-llm-comparison)
- [Is Jev Open Source? What Builders Need (2026) — Julian Goldie](https://juliangoldieaiautomation.com/blog/is-jev-open-source/)

## Comparisons

- [Jev vs generative LLM vs LLM-with-structured-output table](./docs/comparisons.md) — where each layer wins
- [Jev System Model vs LLM for Developers — Injoys](https://injoys.com/en/articles/jev-system-one-model-llm-comparison)
- [Jev Does Not Replace the LLM. It Changes Who Owns the Decision — DEV](https://dev.to/miruky/jev-does-not-replace-the-llm-it-changes-who-owns-the-decision-3n6)

## FAQ

**Is Jev an LLM?**
It reads language like one, but generates no text at all — no replies, no code, no explanations. TypeSafe calls it a System One model, not a large language model.

**Can it hallucinate?**
Not schema hallucinations: it cannot emit a value outside the answer space you declared. It *can* pick the wrong valid option. "Type-safe" ≠ "correct."

**Why not just use an LLM in JSON mode?**
JSON mode constrains *generation* to a schema; the model still generates the path to that structure token by token. Jev constrains the *answer space itself* at the model interface — no generation, no parsing, no validation step, and all questions answered in one parallel pass. They optimize different layers; in practice they compose.

**What does "calibrated" mean?**
When Jev says 0.73 confidence, it's right about 73% of the time (approximately — see independent checks). That turns the score into a routing signal: auto-act above a threshold, escalate below it.

**Is it open source?**
No. The model and RLCD training method are closed and unpublished; the surrounding SDKs and community integrations are open.

**Where do I start?**
[docs/getting-started.md](./docs/getting-started.md) — API key, first call, and the confidence-gating pattern in ~10 minutes.

## Contributing

This list tracks a fast-moving launch. Contributions are welcome — new projects, articles, benchmarks, recipes, or corrections.

1. Check the [contribution guidelines](./CONTRIBUTING.md)
2. Add your entry in the right section (alphabetical within subsections where it makes sense)
3. Open a PR — CI runs a link check on every README/docs change

---

*Maintained by [@dakotac1994](https://github.com/dakotac1994). Not affiliated with TypeSafe AI. Pricing, specs, and launch figures reflect public reporting as of September 2026.*
