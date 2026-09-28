"""Stage 5 Grounding Gate (SPEC §6.3, Gate G4).

Deterministic citation and evidence span verification against the session's retrieved chunks.
"""

from kairos.grounding.gate import GroundingGate

__all__ = ["GroundingGate"]
