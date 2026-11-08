"""Plan builder for the reviewed v4 stop release. Read-only."""
from pathlib import Path

from accounting_recovery_v4 import (BASE, authorization_for, plan_for, review_for,
                                    snapshot, sources)


def build(base: Path = BASE, directory: Path = None, *, owner: int = 320,
          active_uid: int = 0) -> dict:
    directory = Path(directory) if directory is not None else Path(__file__).parent
    baseline = snapshot(base, owner=owner, active_uid=active_uid)
    source_hashes = sources(directory)
    review = review_for(baseline, source_hashes)
    plan = plan_for(baseline, source_hashes)
    return {'plan': plan, 'review': review,
            'authorization': authorization_for(plan, review)}
