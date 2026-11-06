# Review packet — GRRR-k3j7 revision 3



## F1: durable evidence helpers

def _objects_dir(db):
    main = [row[2] for row in db.execute('PRAGMA database_list') if row[1] == 'main']
    _check(len(main) == 1 and main[0], 'Durable evidence database path is absent')
    return Path(main[0]).parent / 'objects'

def _durable_object(db, hashed):
    """Resolve a hash-addressed durable evidence object; never trust the event."""
    identifier(hashed, True)
    path = _objects_dir(db) / hashed
    _check(path.is_file() and not path.is_symlink(), 'Durable evidence object is absent')
    raw = path.read_bytes()
    _check(digest(raw) == hashed, 'Durable evidence object digest differs')
    return raw

def _store_object(db, raw):
    """Persist evidence bytes before the referencing event is appended."""
    _check(type(raw) is bytes and 0 < len(raw) <= MAX_RAW, 'Evidence object bytes differ')
    hashed = digest(raw)
    directory = _objects_dir(db)
    try:
        directory.mkdir(mode=0o700, exist_ok=True)
        path = directory / hashed
        if path.exists():
            _check(path.is_file() and not path.is_symlink()
                   and digest(path.read_bytes()) == hashed,
                   'Existing evidence object content differs')
        else:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600)
            try:
                written = 0
                while written < len(raw):
                    count = os.write(descriptor, raw[written:])
                    _check(type(count) is int and count > 0,
                           'Short evidence object write')
                    written += count
                _check(written == len(raw), 'Short evidence object write')
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except OSError as exc:
        raise Failure('RecoveryRequired', 'Evidence object could not be persisted') from exc
    return hashed


## F1: manifest binding

def _bind_manifest(state, campaign_id, manifest, terminal, leaves, completed):
    """Manifest leaf entries must match the durable per-leaf Plans and prefix."""
    run = state['campaign_run'][(campaign_id,)]
    _check(type(manifest) is dict
           and manifest.get('schema') == 'capstone-campaign-manifest-v2'
           and manifest.get('campaign_plan_sha256') == run['plan_hash']
           and digest(canonical(manifest)) == terminal
           and type(manifest.get('leaves')) is list
           and len(manifest['leaves']) == len(leaves),
           'Campaign manifest differs')
    for position, index in enumerate(sorted(leaves)):
        entry = manifest['leaves'][position]
        leaf = state['leaf'][(campaign_id, index)]
        plan_row = state['leaf_plan'].get((campaign_id, index))
        _check(type(entry) is dict and entry.get('leaf_id') == leaf['leaf_id'],
               'Campaign manifest leaf identity differs')
        if plan_row is not None:
            _check(entry.get('operation_id') == plan_row['operation_id']
                   and entry.get('actual_plan_sha256') == plan_row['plan_hash']
                   and entry.get('actual_plan_bytes_sha256') == plan_row['plan_bytes_sha256']
                   and entry.get('review_sha256') == plan_row['review_hash'],
                   'Campaign manifest leaf binding differs')
        else:
            _check(entry.get('preclaim') == 'not-planned'
                   and entry.get('operation_id') is None,
                   'Campaign manifest invented a plan for an unplanned leaf')
    claimed = sum(1 for entry in manifest['leaves']
                  if type(entry) is dict and entry.get('preclaim') == 'claimed')
    if claimed == 0:
        expected_execution = 'not-run'
    elif claimed == len(leaves) and set(completed).issuperset(leaves):
        expected_execution = 'completed'
    else:
        expected_execution = 'partial'
    _check(manifest.get('execution') == expected_execution,
           'Campaign manifest execution differs from the completion prefix')


## F1: finish

def _finish(state, event, receipt, record, progress, manifest_provider, replay=False,
            db=None):
    """Complete only when every leaf advanced and a manifest provider exists."""
    if not replay:
        require(manifest_provider is not None, 'Unavailable',
                'Terminal manifest derivation is unavailable; finish refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign finish rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'running'
           and current['active_leaf'] is None, 'Campaign finish state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign finish previous revision differs')
    leaves = {row['leaf_index'] for row in state['leaf'].values()
              if row['campaign_id'] == campaign_id}
    completed = set((progress or {}).get(campaign_id, ()))
    _check(bool(leaves) and completed.issuperset(leaves),
           'Campaign finish before every leaf advanced')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None, 'Campaign finish has no terminal hash')
        manifest = _json(_durable_object(db, terminal))
        _bind_manifest(state, campaign_id, manifest, terminal, leaves, completed)
        _check(record['evidence'] == [terminal], 'Campaign finish evidence differs')
        objects = []
    else:
        manifest, terminal = manifest_provider(campaign_id, state, progress)
        _bind_manifest(state, campaign_id, manifest, terminal, leaves, completed)
        _check(record['evidence'] == [terminal], 'Campaign finish evidence differs')
        objects = [canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign finish immutable field differs')
    _check(run['state'] == 'completed' and run['active_leaf'] is None
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign finish revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign finish key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects


## F2: select

def _select(state, event, receipt, record, progress, joins, live=None, replay=False):
    """First unfinished leaf; completion is certified by an injected verifier."""
    if not replay:
        require(joins is not None, 'Unavailable',
                'Campaign completion joins are unavailable; select refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign select rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None, 'Campaign select run is absent')
    _check(current['state'] == 'running' and current['active_leaf'] is None
           and current['result_object'] is None, 'Campaign select state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign select previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign select immutable field differs')
    _check(run['state'] == 'running' and run['result_object'] is None
           and run['revision'] == current['revision'] + 1,
           'Campaign select revision or state differs')
    leaves = sorted(row['leaf_index'] for row in state['leaf'].values()
                    if row['campaign_id'] == campaign_id)
    _check(bool(leaves), 'Campaign select has no leaves')
    completed = dict((progress or {}).get(campaign_id, {}))
    unfinished = [index for index in leaves if index not in completed]
    _check(bool(unfinished), 'Campaign select has no unfinished leaf')
    selected = unfinished[0]
    _check(all(index in completed for index in leaves if index < selected),
           'Campaign select skipped an unfinished predecessor')
    _check(run['active_leaf'] == selected, 'Campaign select leaf differs')
    _check((campaign_id, selected) not in state['leaf_plan'],
           'Campaign select leaf already has a Plan')
    _check(receipt.get('digest') is not None, 'Campaign select receipt differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign select key differs')
    _check(sorted(completed.values()) == record['evidence'],
           'Campaign select evidence differs from completed result refs')
    if not replay:
        joins(campaign_id, sorted(completed), state)
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)


## F2: advance

def _advance(state, event, receipt, record, progress, advance_proof, replay=False):
    """Advance one leaf only with certified claim/exit/settlement proof."""
    if not replay:
        require(advance_proof is not None, 'Unavailable',
                'Claim/exit/settlement proof is unavailable; advance refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign advance rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'running'
           and current['active_leaf'] is not None, 'Campaign advance state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign advance previous revision differs')
    _check(len(record['evidence']) == 1, 'Campaign advance evidence differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign advance immutable field differs')
    _check(run['state'] == 'running' and run['active_leaf'] is None
           and run['result_object'] is None
           and run['revision'] == current['revision'] + 1,
           'Campaign advance revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign advance key differs')
    index = current['active_leaf']
    _check((campaign_id, index) in state['leaf_plan'],
           'Campaign advance leaf has no bound Plan')
    if not replay:
        advance_proof(campaign_id, index, record['evidence'][0], state)
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    if progress is not None:
        progress.setdefault(campaign_id, {})[index] = record['evidence'][0]


## F3: stop-outcome (now binds manifest)

def _stop_outcome(state, event, receipt, record, progress, stop_provider, replay=False,
                  db=None):
    """Stop-pending resolves to stopped only when the outcome verifies fully."""
    if not replay:
        require(stop_provider is not None, 'Unavailable',
                'Authenticated stop outcome is unavailable; stop-outcome refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign stop-outcome rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'stop-pending',
           'Campaign stop-outcome state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign stop-outcome previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None and len(record['evidence']) == 2
               and terminal in record['evidence'], 'Campaign stop-outcome evidence differs')
        kinds = {}
        for hashed in record['evidence']:
            value = _json(_durable_object(db, hashed))
            _check(type(value) is dict and type(value.get('schema')) is str,
                   'Campaign stop-outcome evidence object differs')
            kinds[value['schema']] = value
        _check(set(kinds) == {'capstone-campaign-manifest-v2',
                              'capstone-campaign-stop-v2'},
               'Campaign stop-outcome evidence roles differ')
        outcome = kinds['capstone-campaign-stop-v2']
        stop_leaves = {row['leaf_index'] for row in state['leaf'].values()
                       if row['campaign_id'] == campaign_id}
        _bind_manifest(state, campaign_id, kinds['capstone-campaign-manifest-v2'],
                       terminal, stop_leaves,
                       set((progress or {}).get(campaign_id, ())))
        _check(digest(canonical(kinds['capstone-campaign-manifest-v2'])) == terminal,
               'Campaign stop-outcome manifest differs')
        verified = outcome.get('verified')
        _check(type(verified) is bool,
               'Campaign stop-outcome durable verification flag differs')
        _check(run['state'] in ('stopped', 'recovery-required'),
               'Campaign stop-outcome state differs')
        _check((run['state'] == 'stopped') is verified,
               'Campaign stop-outcome state contradicts durable evidence')
        objects = []
    else:
        manifest, terminal, outcome, verified = stop_provider(
            campaign_id, state, record['evidence'])
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and terminal == digest(canonical(manifest))
               and type(outcome) is dict and type(verified) is bool,
               'Campaign stop-outcome evidence differs')
        _check(outcome.get('verified') is verified,
               'Campaign stop-outcome verification flag differs')
        _check(record['evidence'] == sorted({digest(canonical(outcome)), terminal}),
               'Campaign stop-outcome evidence differs')
        objects = [canonical(outcome), canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign stop-outcome immutable field differs')
    expected_state = 'stopped' if verified else 'recovery-required'
    expected_leaf = None if verified else current['active_leaf']
    _check(run['state'] == expected_state and run['active_leaf'] == expected_leaf
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign stop-outcome revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign stop-outcome key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects


## Fence (now binds manifest)

def _fence(state, event, receipt, record, progress, fence_provider, replay=False, db=None):
    """Controller-authenticated cut to recovery-required; never resumes work."""
    if not replay:
        require(fence_provider is not None, 'Unavailable',
                'Authenticated fence evidence is unavailable; fence refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign fence rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] in ('running', 'stop-pending'),
           'Campaign fence state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign fence previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None and len(record['evidence']) == 3
               and terminal in record['evidence'], 'Campaign fence evidence differs')
        kinds = {}
        for hashed in record['evidence']:
            value = _json(_durable_object(db, hashed))
            _check(type(value) is dict and type(value.get('schema')) is str,
                   'Campaign fence evidence object differs')
            kinds[value['schema']] = value
        _check(set(kinds) == {'capstone-campaign-manifest-v2',
                              'capstone-failure-v1', 'capstone-campaign-fence-v2'},
               'Campaign fence evidence roles differ')
        manifest = kinds['capstone-campaign-manifest-v2']
        snapshot = kinds['capstone-campaign-fence-v2']
        fence_leaves = {row['leaf_index'] for row in state['leaf'].values()
                        if row['campaign_id'] == campaign_id}
        _bind_manifest(state, campaign_id, manifest, terminal, fence_leaves,
                       set((progress or {}).get(campaign_id, ())))
        _check(manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and digest(canonical(manifest)) == terminal
               and snapshot.get('campaign_operation_id') == current['campaign_operation_id']
               and snapshot.get('owner_epoch') == current['owner_epoch']
               and snapshot.get('observed_owner') in ('present', 'absent')
               and snapshot.get('active_leaf') == current['active_leaf']
               and snapshot.get('cut') in ('owner-lost', 'binding-gap', 'claim-gap',
                                           'accounting-gap', 'dispatch-unknown',
                                           'evidence-failure'),
               'Campaign fence durable evidence differs')
        objects = []
    else:
        manifest, terminal, failure, snapshot = fence_provider(
            campaign_id, state, record['evidence'])
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and terminal == digest(canonical(manifest)),
               'Campaign fence manifest differs')
        _check(type(failure) is dict and failure.get('schema') == 'capstone-failure-v1',
               'Campaign fence failure record differs')
        _check(type(snapshot) is dict
               and snapshot.get('schema') == 'capstone-campaign-fence-v2'
               and snapshot.get('campaign_operation_id') == current['campaign_operation_id']
               and snapshot.get('owner_epoch') == current['owner_epoch']
               and snapshot.get('observed_owner') in ('present', 'absent')
               and snapshot.get('active_leaf') == current['active_leaf']
               and snapshot.get('cut') in ('owner-lost', 'binding-gap', 'claim-gap',
                                           'accounting-gap', 'dispatch-unknown',
                                           'evidence-failure'),
               'Campaign fence snapshot differs')
        _check(record['evidence'] == sorted({digest(canonical(failure)),
                                             digest(canonical(snapshot)), terminal}),
               'Campaign fence evidence differs')
        objects = [canonical(failure), canonical(snapshot), canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign fence immutable field differs')
    _check(run['state'] == 'recovery-required'
           and run['active_leaf'] == current['active_leaf']
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign fence revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign fence key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects
