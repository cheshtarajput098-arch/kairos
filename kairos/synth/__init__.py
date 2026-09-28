"""Stage 5 Synthesis & Answer-as-you-speak Drafting (SPEC §6.2, §6.4).

Extractive grounded synthesis and speculative answer drafting with Ready-at-End measurement.
"""

from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer

__all__ = [
    "DraftingManager",
    "ExtractiveSynthesizer",
]
