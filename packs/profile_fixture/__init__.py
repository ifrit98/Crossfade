"""W0 fixture pack: the T0 weighted-RMS-width transform on a supplied delay-power profile."""

from packs.profile_fixture.ops import WeightedRmsWidth

CORE_API_VERSION = 1
OPERATIONS = [WeightedRmsWidth()]
REGIME: dict = {}
TRANSFORMS: list = []
