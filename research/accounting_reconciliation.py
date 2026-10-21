"""Legacy evidence inventory, never an allowance or migration authorization.

Accepted integration evidence proves those runs, not complete cumulative campaign
accounting. This phase intentionally cannot create an approved migration receipt.
"""
from decimal import Decimal, InvalidOperation
from common import canonical, digest, require

REQUIRED = (
    'complete_invocation_inventory_including_failed_attempts',
    'cumulative_review_and_replay_duration',
    'selector_and_preparation_separation',
    'prior_hold_settlement_receipts',
    'campaign_and_run_stop_scope_reconciliation',
    'cross_profile_poc_carry_forward',
)


def micros(value):
    """Exact decimal conversion only for observations, never settlement."""
    require(type(value) in (str, int, float), 'RecoveryRequired', 'Malformed legacy duration')
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        require(False, 'RecoveryRequired', 'Malformed legacy duration')
    require(number.is_finite() and 0 <= number <= Decimal(2**63 - 1) / 1_000_000,
            'RecoveryRequired', 'Unknown or unbounded legacy duration')
    return str(number * 1_000_000)


def summarize(events):
    """Deduplicate identical accepted snapshots; conflicting identities block."""
    reservations, seen, observations, stops, issues = {}, set(), [], [], []
    for item in events:
        require(set(item) == {'source', 'event'}, 'RecoveryRequired', 'Event envelope differs')
        source, event = item['source'], item['event']
        require(isinstance(source, str) and isinstance(event, dict), 'RecoveryRequired', 'Malformed evidence')
        identity = digest(canonical(event))
        if identity in seen:
            continue
        seen.add(identity)
        kind = event.get('kind')
        if kind == 'reserved':
            maximum = event.get('maximum_seconds')
            require(type(maximum) is int and 0 < maximum <= (2**63 - 1) // 1_000_000,
                    'RecoveryRequired', 'Unknown reservation maximum')
            if 'reservation' not in event:
                total = event.get('reserved_total_seconds')
                require(total is None or type(total) is int and maximum <= total <= (2**63 - 1) // 1_000_000,
                        'RecoveryRequired', 'Malformed legacy reservation total')
                issues.append({'kind': 'unmapped_legacy_reservation', 'source': source,
                               'event_sha256': identity, 'fields': sorted(event),
                               'reported_maximum_seconds': maximum,
                               'reported_reserved_total_seconds': total,
                               'reported_run': event.get('run'), 'settled': False})
                continue  # Never invent a new reservation ID from partial legacy metadata.
            reservation = event.get('reservation')
            require(isinstance(reservation, str) and reservation, 'RecoveryRequired', 'Missing reservation identity')
            money = event.get('money_cents')
            require(money is None or type(money) is int and 0 <= money <= 2**63 - 1,
                    'RecoveryRequired', 'Malformed reported cost')
            if event.get('review_seconds') is not None:
                micros(event['review_seconds'])
            row = {'source': source, 'event_sha256': identity, 'reservation': reservation,
                   'run': event.get('run'), 'maximum_execution_us': maximum * 1_000_000,
                   'reported_money_cents': event.get('money_cents'),
                   'reported_review_seconds': event.get('review_seconds'),
                   'settled': False, 'authority': 'legacy evidence only'}
            if reservation in reservations:
                issues.append({'kind': 'conflicting_reservation', 'reservation': reservation,
                               'first': reservations[reservation]['event_sha256'], 'other': identity})
            else:
                reservations[reservation] = row
        elif kind == 'observation':
            value = event.get('execution_seconds')
            observations.append({'source': source, 'event_sha256': identity,
                                 'run': event.get('run'), 'reservation': event.get('reservation'),
                                 'reported_execution_us': None if value is None else micros(value),
                                 'reported_review_seconds': event.get('review_seconds'),
                                 'settlement_authorized': False})
        elif kind in ('stop-fenced', 'stop-outcome'):
            stops.append({'source': source, 'event_sha256': identity, 'kind': kind,
                          'run': event.get('run'), 'epoch': event.get('epoch'),
                          'campaign_stop_state': None})
    return {'version': 1, 'decision': 'reconciliation-required', 'execution_gate': 'blocked',
            'migration_authorized': False, 'reset_allowance': False, 'unresolved_history': True,
            'known_legacy_reservations': list(reservations.values()),
            'known_legacy_observations': observations, 'known_stop_events': stops, 'conflicts': issues,
            'required_evidence': list(REQUIRED), 'campaign_totals': None,
            'remaining_allowance': None, 'campaign_stop_state': None,
            'note': 'Even complete accepted-run observations do not prove cumulative campaign history.'}
