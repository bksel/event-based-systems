"""The supervisor: picks the next controllable event from E_con ∩ EF(s) that is safe."""

from __future__ import annotations

from dataclasses import dataclass

from espresso.events import E_CON, Event
from espresso.model import enabled, safe
from espresso.policy import Policy
from espresso.state import State

# Fired before the policy is asked: they are rules, not prioritization choices.
MANDATORY = (Event.ABORT_DRINK, Event.REJECT_ORDER)


@dataclass(frozen=True)
class Controller:
    policy: Policy

    def candidates(self, s: State) -> frozenset[Event]:
        return frozenset(e for e in enabled(s) & E_CON if safe(s, e))

    def decide(self, s: State) -> Event | None:
        """The next controllable event to fire in s, or None to wait for the plant."""
        candidates = self.candidates(s)
        for e in MANDATORY:
            if e in candidates:
                return e
        choice = self.policy.choose(s, candidates)
        if choice is not None and choice not in candidates:
            raise ValueError(f"policy chose {choice}, which is not enabled and safe")
        return choice
