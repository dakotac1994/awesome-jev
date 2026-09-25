#!/usr/bin/env python3
"""Jev quickstart: one state, three typed questions, one parallel pass.

Usage:
    python quickstart.py --demo        # offline mock, no API key needed
    TYPESAFE_API_KEY=ts_... python quickstart.py   # live call

Requires: pip install typesafe-sdk  (only for live mode)
"""
from __future__ import annotations

import argparse
import json
import os
import sys


# ---------------------------------------------------------------- mock mode
class _Answer(dict):
    __getattr__ = dict.get


class _MockResponse:
    answers = {
        "department": _Answer(choice="technical",
                             probabilities={"billing": 0.159, "technical": 0.84, "sales": 0.001},
                             confidence=0.596),
        "frustration": _Answer(score=1.035, confidence=0.842),
        "is_urgent": _Answer(noul=0.999),
    }
    usage = _Answer(input_tokens=312, output_tokens=48)


class _MockClient:
    def system_one(self, **kwargs):
        print("(mock) would POST to https://api.typesafe.ai/v1/systemone", file=sys.stderr)
        print("(mock) questions:", ", ".join(kwargs["questions"]), file=sys.stderr)
        return _MockResponse()


# ---------------------------------------------------------------- main
STATE = (
    "Hi, I've been trying to connect my Stripe account for 3 days "
    "and it keeps failing. I'm losing sales. Please help ASAP."
)

QUESTIONS_SPEC = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this",
        "criteria": {
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    },
    "frustration": {
        "type": "score",
        "instructions": "How frustrated the customer appears",
        "criteria": ["Calm, just stating facts",
                     "Frustrated but civil",
                     "Very angry, strong language"],
    },
    "is_urgent": {
        "type": "noul",
        "instructions": "The message conveys urgency or time-sensitivity",
    },
}


def build_questions_sdk():
    from typesafe_sdk import Choice, Noul, Score  # noqa: F401

    return {
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
        "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="run offline with a mock client")
    args = ap.parse_args()

    if args.demo:
        client = _MockClient()
        questions = QUESTIONS_SPEC
    else:
        if not os.environ.get("TYPESAFE_API_KEY"):
            sys.exit("Set TYPESAFE_API_KEY, or run with --demo for the offline mock.")
        from typesafe_sdk import TypeSafeClient

        client = TypeSafeClient()
        questions = build_questions_sdk()

    response = client.system_one(state=STATE, questions=questions)

    print("department :", response.answers["department"].choice,
          dict(response.answers["department"].get("probabilities", {})))
    print("frustration:", response.answers["frustration"].score)
    print("is_urgent  :", response.answers["is_urgent"].noul)
    print("usage      :", json.dumps(dict(response.usage)))


if __name__ == "__main__":
    main()
