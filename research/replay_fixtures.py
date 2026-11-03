"""Replay-only catalog; frozen corpus v2.2 is neither modified nor reclassified.

The generic supervisor's D/C namespace is wire syntax, not corpus membership.
These four identifiers exist only on the separately reviewed replay medium.
"""
from common import canonical, digest
from corpus_probes import HEADER, PROBES

VERSION = 'GRRR-independent-replay-input-v1'
CLEAN = 'GRRR-VC-C901'
SEEDED = 'GRRR-VC-D901'
REBUILD = 'GRRR-VC-D902'
INTERRUPTION = 'GRRR-VC-C902'
FLOOR = 16106127360


def seeds() -> list:
    """Return a fresh exact catalog, never a caller-provided mutation recipe."""
    return [
        {'challenge': CLEAN, 'kind': 'clean-control', 'file': '', 'anchor': '', 'replacement': ''},
        {'challenge': SEEDED, 'kind': 'single-unique-replacement', 'file': 'wikilinks.go',
         'anchor': 'if len(m) > 4 {', 'replacement': 'if false {'},
        {'challenge': REBUILD, 'kind': 'single-unique-replacement', 'file': 'wikilinks.go',
         'anchor': 'if len(m) > 4 {', 'replacement': 'if GRRR_REPLAY_INVALID_SYNTAX { {'},
        {'challenge': INTERRUPTION, 'kind': 'clean-control', 'file': '', 'anchor': '', 'replacement': ''},
    ]


def probes() -> dict:
    """Clean and seeded cases use the identical D011 semantic assertion.

The interruption probe blocks for a bounded 300 seconds inside the guest. The
reviewed runner must interrupt it; merely timing out elsewhere is not proof that
this probe ran. No candidate source is executed during input preparation.
"""
    result = {}
    for name in (CLEAN, SEEDED, REBUILD, INTERRUPTION):
        body = PROBES['D011']
        if name == INTERRUPTION:
            body = 'time.Sleep(300 * time.Second)\n' + body
        result[name] = HEADER.replace('__CHALLENGE__', name[-4:]).replace('__BODY__', body).encode()
    return result


def catalog() -> dict:
    """Stable content identity for reviewed fixture semantics, not execution proof."""
    return {'version': VERSION, 'source_challenge': 'GRRR-VC-D011',
            'seed_sha256': digest(canonical(seeds())),
            'probe_sha256': {name: digest(raw) for name, raw in probes().items()},
            'interruption_probe_bound_seconds': 300,
            'admission': 'blocked', 'execution_performed': False}
