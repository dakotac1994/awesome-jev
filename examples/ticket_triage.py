#!/usr/bin/env python3
"""Async ticket triage at volume: typed Pydantic response models, retries,
concurrent fan-out, and a usage ledger.

Adapted from the community coding-guide pattern (MarkTechPost/Bytecore,
Sept 2026): declare the answers you expect, read them as attributes.

Usage:
    python ticket_triage.py --demo        # offline mock
    TYPESAFE_API_KEY=ts_... python ticket_triage.py   # live

Requires: pip install typesafe-sdk  (only for live mode)
"""
from __future__ import annotations

import argparse
import asyncio
import concurrent.futures
import os
import sys
import time

QUEUE = [
    "My invoice shows two seats but I only have one user.",
    "The export button does nothing in Safari.",
    "Can I get a discount if I pay annually?",
    "Your API returns 500 on every request since this morning!!",
    "I want my money back for last month, the product never worked.",
    "How do I add a teammate?",
    "Webhooks stopped firing after your update.",
    "Do you offer a plan for nonprofits?",
    "Charged after I cancelled. Refund this immediately.",
    "The dashboard is slow but usable.",
    "Is there an on-prem version?",
    "Login emails never arrive.",
]

LEDGER = {"calls": 0, "input_tokens": 0, "output_tokens": 0}

PRICE_PER_MTOK = 0.042  # USD, input only; output is free


class _Answer(dict):
    __getattr__ = dict.get


class _MockTicket:
    def __init__(self, text):
        urgent = any(w in text.lower() for w in ("!!", "immediately", "money back", "500"))
        billing = any(w in text.lower() for w in ("invoice", "discount", "money back", "charged", "plan"))
        self.department = _Answer(choice="billing" if billing else "technical", confidence=0.81)
        self.frustration = _Answer(score=1.5 if urgent else 0.4, confidence=0.77)
        self.refund_requested = _Answer(noul=0.95 if "refund" in text.lower() or "money back" in text.lower() else 0.05)
        self.usage = _Answer(input_tokens=120, output_tokens=12)


class _MockAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def system_one(self, state, questions, response_model=None):
        await asyncio.sleep(0.01)  # pretend network
        return _MockTicket(state)


def run_async(coro):
    """Works in a plain script and inside Jupyter/Colab."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def triage_all(tickets, client, triage_questions, ticket_model):
    results = await asyncio.gather(
        *(client.system_one(t, triage_questions, response_model=ticket_model) for t in tickets)
    )
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    if args.demo:
        aclient, questions, model = _MockAsyncClient(), {}, None
    else:
        if not os.environ.get("TYPESAFE_API_KEY"):
            sys.exit("Set TYPESAFE_API_KEY, or run with --demo.")
        from typesafe_sdk import (AsyncTypeSafeClient, Choice, ChoiceAnswer, Noul,
                                  NoulAnswer, RetryPolicy, Score, ScoreAnswer,
                                  SystemOneResponse)

        class TicketDecision(SystemOneResponse):
            """Declare the answers you expect; read them as attributes."""

            department: ChoiceAnswer
            frustration: ScoreAnswer
            refund_requested: NoulAnswer

        questions = {
            "department": Choice(
                instructions="Which team should handle this ticket",
                criteria={
                    "billing": "Payment, refund or subscription issues",
                    "technical": "Bugs, outages or integration problems",
                    "sales": "Pricing, plans or account upgrades",
                },
            ),
            "frustration": Score(
                instructions="How frustrated the customer appears",
                criteria=["Calm, just stating facts",
                          "Frustrated but civil",
                          "Very angry, strong language"],
            ),
            "refund_requested": Noul(
                instructions="The customer is explicitly asking for a refund"),
        }
        retry = RetryPolicy(max_retries=3, backoff_initial=0.5, backoff_max=4.0, timeout=20.0)
        aclient, model = AsyncTypeSafeClient(retry=retry, timeout=10.0), TicketDecision

    async def run():
        async with aclient as client:
            t0 = time.perf_counter()
            results = await triage_all(QUEUE, client, questions, model)
            return results, (time.perf_counter() - t0) * 1e3

    results, wall_ms = run_async(run())

    for r in results:
        LEDGER["calls"] += 1
        LEDGER["input_tokens"] += r.usage.input_tokens or 0
        LEDGER["output_tokens"] += r.usage.output_tokens or 0

    cost = LEDGER["input_tokens"] / 1e6 * PRICE_PER_MTOK
    print(f"{len(QUEUE)} tickets triaged in {wall_ms:.0f} ms wall time "
          f"({wall_ms / len(QUEUE):.0f} ms amortised per ticket)\n")
    print(f"  {'ticket':<54} {'department':<10} {'frustr.':>7} {'refund':>7}")
    for text, r in zip(QUEUE, results):
        print(f"  {text[:54]:<54} {r.department.choice:<10} "
              f"{r.frustration.score:7.2f} {r.refund_requested.noul:7.2f}")
    print(f"\n  usage: {LEDGER['input_tokens']} in / {LEDGER['output_tokens']} out tokens "
          f"-> ~${cost:.4f} (output free)")


if __name__ == "__main__":
    main()
