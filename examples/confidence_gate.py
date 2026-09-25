#!/usr/bin/env python3
"""Confidence-gated escalation: the canonical Jev architecture.

Jev triages each ticket fast and cheap. High confidence -> act autonomously.
Medium -> act but flag. Low -> escalate to a frontier LLM (the slow model
that can explain itself).

Usage:
    python confidence_gate.py --demo        # offline mock
    TYPESAFE_API_KEY=ts_... python confidence_gate.py   # live

Requires: pip install typesafe-sdk  (only for live mode)
"""
from __future__ import annotations

import argparse
import os
import sys

AUTO_ACT = 0.90   # act autonomously
REVIEW = 0.60     # act, but flag for review
                  # below REVIEW -> escalate to frontier LLM


class _Answer(dict):
    __getattr__ = dict.get


class _MockResponse:
    def __init__(self, choice, confidence, urgent):
        self.answers = {
            "department": _Answer(choice=choice, confidence=confidence),
            "is_urgent": _Answer(noul=urgent),
        }


class _MockClient:
    # canned (choice, confidence, urgency) triples to demo all three branches
    PRESETS = [("technical", 0.94, 0.99), ("billing", 0.72, 0.40), ("sales", 0.31, 0.10)]

    def __init__(self):
        self._i = 0

    def system_one(self, **kwargs):
        preset = self.PRESETS[self._i % len(self.PRESETS)]
        self._i += 1
        print("(mock) triaged; confidence=%.2f" % preset[1], file=sys.stderr)
        return _MockResponse(*preset)


def build_questions():
    from typesafe_sdk import Choice, Noul

    return {
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


def decide(client, ticket, questions):
    resp = client.system_one(state=ticket, questions=questions)
    dept = resp.answers["department"]
    conf = dept.confidence

    if conf >= AUTO_ACT:
        action = f"AUTO-ROUTE to {dept.choice}"
    elif conf >= REVIEW:
        action = f"ROUTE to {dept.choice} (flagged: confidence {conf:.2f})"
    else:
        action = f"ESCALATE to frontier LLM (confidence {conf:.2f})"
    return dept.choice, conf, action


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    tickets = [
        "The export button does nothing in Safari.",
        "Charged after I cancelled. Refund this immediately.",
        "Do you offer a plan for nonprofits?",
    ]

    if args.demo:
        client, questions = _MockClient(), {"department": {}, "is_urgent": {}}
    else:
        if not os.environ.get("TYPESAFE_API_KEY"):
            sys.exit("Set TYPESAFE_API_KEY, or run with --demo.")
        from typesafe_sdk import TypeSafeClient

        client, questions = TypeSafeClient(), build_questions()

    for t in tickets:
        choice, conf, action = decide(client, t, questions)
        print(f"[{conf:.2f}] {t[:52]:<54} -> {action}")


if __name__ == "__main__":
    main()
