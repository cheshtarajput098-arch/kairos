"""Stage 5 Synthesis & Answer-as-you-speak Drafting (SPEC §6.2, §6.4).

Extractive grounded synthesis and speculative answer drafting with Ready-at-End measurement.
"""

from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer
from kairos.synth.rewrite import Speed2Synthesizer

__all__ = [
    "DraftingManager",
    "ExtractiveSynthesizer",
    "Speed2Synthesizer",
]
