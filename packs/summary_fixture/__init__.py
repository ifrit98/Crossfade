"""W0 fixture pack: an output-only summary import with no channel estimator."""

from packs.summary_fixture.ops import ImportSummary

CORE_API_VERSION = 1
OPERATIONS = [ImportSummary()]
REGIME: dict = {}
TRANSFORMS: list = []
