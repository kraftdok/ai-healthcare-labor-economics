"""
Shared hard-cap budget tracker across all pilot scripts.

Writes cumulative spend to data/results/_budget_ledger.json.
Every Claude call in any pilot script MUST call record() before sending,
which aborts if the cap would be exceeded.

Pricing: claude-opus-4-7 = $15/MTok input, $75/MTok output
"""

import json
from pathlib import Path

OPUS47_INPUT_PER_MTOK = 15.0
OPUS47_OUTPUT_PER_MTOK = 75.0

HARD_CAP_USD = 5.00

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "results" / "_budget_ledger.json"
_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load():
    if _LEDGER_PATH.exists():
        return json.loads(_LEDGER_PATH.read_text())
    return {"total_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "call_count": 0, "runs": []}


def _save(ledger):
    _LEDGER_PATH.write_text(json.dumps(ledger, indent=2))


def current_total_usd() -> float:
    return _load()["total_usd"]


def remaining_usd() -> float:
    return max(0.0, HARD_CAP_USD - current_total_usd())


def record_usage(input_tokens: int, output_tokens: int, label: str = ""):
    """Record a completed call. Returns running total."""
    ledger = _load()
    cost = (input_tokens / 1e6) * OPUS47_INPUT_PER_MTOK + (output_tokens / 1e6) * OPUS47_OUTPUT_PER_MTOK
    ledger["total_usd"] += cost
    ledger["input_tokens"] += input_tokens
    ledger["output_tokens"] += output_tokens
    ledger["call_count"] += 1
    ledger["runs"].append({"label": label, "in": input_tokens, "out": output_tokens, "cost_usd": round(cost, 5)})
    _save(ledger)
    return ledger["total_usd"]


def check_before_call(estimated_max_cost_usd: float = 0.05):
    """Raise RuntimeError if the next call could push total over HARD_CAP_USD."""
    total = current_total_usd()
    if total + estimated_max_cost_usd > HARD_CAP_USD:
        raise RuntimeError(
            f"BUDGET HARD CAP HIT: spent ${total:.4f}, "
            f"cap ${HARD_CAP_USD:.2f}. Aborting before next call."
        )


def reset_ledger():
    """Only use manually if you want to restart budget tracking."""
    _save({"total_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "call_count": 0, "runs": []})


if __name__ == "__main__":
    L = _load()
    print(f"Total spend: ${L['total_usd']:.4f}")
    print(f"Remaining in cap: ${remaining_usd():.4f}")
    print(f"Calls made: {L['call_count']}")
