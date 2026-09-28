"""Stage 2 Multi-Intent Decomposer (SPEC §5).

Disfluency normalisation, incremental legs, deduplication, hard cap, stable leg IDs,
and concurrent parallel retrieval dispatch.
"""

from kairos.decompose.disfluency import DisfluencyNormalizer
from kairos.decompose.dispatcher import ParallelDispatcher
from kairos.decompose.llm_splitter import LLMDecomposer
from kairos.decompose.manager import DecompositionManager
from kairos.decompose.rule_splitter import RuleBasedSplitter

__all__ = [
    "DecompositionManager",
    "DisfluencyNormalizer",
    "LLMDecomposer",
    "ParallelDispatcher",
    "RuleBasedSplitter",
]
