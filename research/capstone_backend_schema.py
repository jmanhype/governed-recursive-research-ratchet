"""Uninstalled backend-v2 SQL contract. No production installer or migration.

The declarations here are source fixtures only. Matching SQL is necessary but
never sufficient to establish issuance, approval, or execution authority.
"""
from common import require
from capstone_journal_schema import validate_schema as validate_journal_schema

PREFIX = 'backend_v2_'
TABLE_COLUMNS = {
    'issuance': ('auth_hash', 'campaign_id', 'issuance_id', 'spec_hash', 'registry_hash',
                 'auth_raw', 'spec_raw', 'intent_anchor', 'phase', 'bundle_raw', 'issued_anchor'),
    'campaign': ('campaign_id', 'control_run', 'issuance_id', 'stop_epoch', 'stopped',
                 'stop_operation', 'stop_anchor'),
    'leaf': ('campaign_id', 'leaf_index', 'leaf_id', 'grant_id', 'request_run', 'request_hash'),
    'binding': ('operation_id', 'grant_id', 'plan_hash', 'start_hash', 'start_raw', 'bind_anchor'),
    'launch': ('launch_id', 'operation_id', 'control_run', 'epoch', 'session_id',
               'intent_anchor', 'record'),
    'projection': ('operation_id', 'record'),
    'campaign_run': ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                     'auth_hash', 'owner_epoch', 'state', 'active_leaf', 'result_object',
                     'intent_anchor', 'revision', 'last_event'),
    'leaf_plan': ('campaign_id', 'leaf_index', 'operation_id', 'plan_hash',
                  'plan_bytes_sha256', 'plan_raw', 'review_hash'),
}
PRIMARY_KEYS = {name: columns[:1] for name, columns in TABLE_COLUMNS.items()}
PRIMARY_KEYS.update(leaf=('campaign_id', 'leaf_index'), leaf_plan=('campaign_id', 'leaf_index'))
BLOBS = {'issuance': {'auth_raw', 'spec_raw', 'bundle_raw'}, 'binding': {'start_raw'},
         'launch': {'record'}, 'projection': {'record'}, 'campaign_run': {'plan_raw'},
         'leaf_plan': {'plan_raw'}}

TABLE_SQL = (
    """CREATE TABLE backend_v2_issuance(
auth_hash TEXT PRIMARY KEY NOT NULL, campaign_id TEXT UNIQUE NOT NULL,
issuance_id TEXT UNIQUE NOT NULL, spec_hash TEXT NOT NULL, registry_hash TEXT NOT NULL,
auth_raw BLOB NOT NULL CHECK(typeof(auth_raw)='blob'),
spec_raw BLOB NOT NULL CHECK(typeof(spec_raw)='blob'), intent_anchor TEXT NOT NULL,
phase TEXT NOT NULL CHECK(phase IN ('intent','issued')),
bundle_raw BLOB CHECK(bundle_raw IS NULL OR typeof(bundle_raw)='blob'), issued_anchor TEXT,
CHECK((phase='intent' AND bundle_raw IS NULL AND issued_anchor IS NULL) OR
(phase='issued' AND bundle_raw IS NOT NULL AND issued_anchor IS NOT NULL)))""",
    """CREATE TABLE backend_v2_campaign(
campaign_id TEXT PRIMARY KEY NOT NULL REFERENCES backend_v2_issuance(campaign_id),
control_run TEXT UNIQUE NOT NULL,
issuance_id TEXT UNIQUE NOT NULL REFERENCES backend_v2_issuance(issuance_id),
stop_epoch INTEGER NOT NULL CHECK(typeof(stop_epoch)='integer' AND stop_epoch IN (0,1)),
stopped INTEGER NOT NULL CHECK(typeof(stopped)='integer' AND stopped IN (0,1)),
stop_operation TEXT, stop_anchor TEXT,
CHECK((stopped=0 AND stop_epoch=0 AND stop_operation IS NULL AND stop_anchor IS NULL) OR
(stopped=1 AND stop_epoch=1 AND stop_operation IS NOT NULL AND stop_anchor IS NOT NULL)))""",
    """CREATE TABLE backend_v2_leaf(
campaign_id TEXT NOT NULL REFERENCES backend_v2_campaign(campaign_id),
leaf_index INTEGER NOT NULL CHECK(typeof(leaf_index)='integer' AND leaf_index>=0 AND leaf_index<256),
leaf_id TEXT UNIQUE NOT NULL,
grant_id TEXT UNIQUE NOT NULL REFERENCES capstone_grants(grant_id),
request_run TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL,
PRIMARY KEY(campaign_id,leaf_index))""",
    """CREATE TABLE backend_v2_binding(
operation_id TEXT PRIMARY KEY NOT NULL,
grant_id TEXT UNIQUE NOT NULL REFERENCES backend_v2_leaf(grant_id),
plan_hash TEXT NOT NULL, start_hash TEXT NOT NULL,
start_raw BLOB NOT NULL CHECK(typeof(start_raw)='blob'), bind_anchor TEXT NOT NULL)""",
    """CREATE TABLE backend_v2_launch(
launch_id TEXT PRIMARY KEY NOT NULL,
operation_id TEXT UNIQUE NOT NULL REFERENCES backend_v2_binding(operation_id),
control_run TEXT NOT NULL, epoch INTEGER NOT NULL CHECK(typeof(epoch)='integer' AND epoch>=0),
session_id TEXT NOT NULL, intent_anchor TEXT NOT NULL,
record BLOB NOT NULL CHECK(typeof(record)='blob'))""",
    """CREATE TABLE backend_v2_projection(
operation_id TEXT PRIMARY KEY NOT NULL REFERENCES backend_v2_binding(operation_id),
record BLOB NOT NULL CHECK(typeof(record)='blob'))""",
    """CREATE TABLE backend_v2_campaign_run(
campaign_id TEXT PRIMARY KEY NOT NULL REFERENCES backend_v2_campaign(campaign_id),
campaign_operation_id TEXT UNIQUE NOT NULL, plan_hash TEXT UNIQUE NOT NULL,
plan_raw BLOB NOT NULL CHECK(typeof(plan_raw)='blob'), auth_hash TEXT NOT NULL,
owner_epoch TEXT NOT NULL,
state TEXT NOT NULL CHECK(state IN ('running','completed','stop-pending','stopped','recovery-required')),
active_leaf INTEGER CHECK(active_leaf IS NULL OR (typeof(active_leaf)='integer' AND active_leaf>=0 AND active_leaf<256)),
result_object TEXT, intent_anchor TEXT NOT NULL,
revision INTEGER NOT NULL CHECK(typeof(revision)='integer' AND revision>=0), last_event TEXT NOT NULL,
CHECK((state IN ('running','stop-pending') AND result_object IS NULL) OR
(state IN ('completed','stopped','recovery-required') AND result_object IS NOT NULL)),
CHECK(state NOT IN ('completed','stopped') OR active_leaf IS NULL))""",
    """CREATE TABLE backend_v2_leaf_plan(
campaign_id TEXT NOT NULL REFERENCES backend_v2_campaign_run(campaign_id),
leaf_index INTEGER NOT NULL CHECK(typeof(leaf_index)='integer' AND leaf_index>=0 AND leaf_index<256),
operation_id TEXT UNIQUE NOT NULL REFERENCES backend_v2_binding(operation_id),
plan_hash TEXT NOT NULL, plan_bytes_sha256 TEXT NOT NULL,
plan_raw BLOB NOT NULL CHECK(typeof(plan_raw)='blob'), review_hash TEXT NOT NULL,
PRIMARY KEY(campaign_id,leaf_index))""",
)


def _guard(table, columns, condition):
    identities = ' OR '.join('NEW.' + c + ' IS NOT OLD.' + c for c in columns)
    return ('CREATE TRIGGER backend_v2_' + table + '_guard_update BEFORE UPDATE ON backend_v2_' +
            table + '\nWHEN ' + identities + ' OR NOT (' + condition + ')\n' +
            "BEGIN SELECT RAISE(ABORT,'invalid backend transition'); END")


TRIGGER_SQL = tuple(
    'CREATE TRIGGER backend_v2_' + table + '_no_delete BEFORE DELETE ON backend_v2_' +
    table + " BEGIN SELECT RAISE(ABORT,'immutable backend row'); END"
    for table in TABLE_COLUMNS
) + tuple(
    'CREATE TRIGGER backend_v2_' + table + '_no_update BEFORE UPDATE ON backend_v2_' +
    table + " BEGIN SELECT RAISE(ABORT,'immutable backend row'); END"
    for table in ('leaf', 'binding', 'leaf_plan')
) + (
    _guard('issuance', TABLE_COLUMNS['issuance'][:8],
           "OLD.phase='intent' AND NEW.phase='issued' AND OLD.bundle_raw IS NULL AND "
           'OLD.issued_anchor IS NULL AND NEW.bundle_raw IS NOT NULL AND NEW.issued_anchor IS NOT NULL'),
    _guard('campaign', TABLE_COLUMNS['campaign'][:3],
           'OLD.stopped=0 AND OLD.stop_epoch=0 AND NEW.stopped=1 AND NEW.stop_epoch=1 '
           'AND NEW.stop_operation IS NOT NULL AND NEW.stop_anchor IS NOT NULL'),
    _guard('launch', TABLE_COLUMNS['launch'][:-1], "typeof(NEW.record)='blob'"),
    _guard('projection', ('operation_id',), "typeof(NEW.record)='blob'"),
    _guard('campaign_run', TABLE_COLUMNS['campaign_run'][:6] + ('intent_anchor',),
           "NEW.revision=OLD.revision+1 AND NEW.last_event IS NOT OLD.last_event AND ("
           "(OLD.state='running' AND NEW.state='running' AND ("
           'OLD.active_leaf IS NULL OR NEW.active_leaf IS NULL OR NEW.active_leaf=OLD.active_leaf)) OR '
           "(OLD.state='running' AND NEW.state='completed' AND OLD.active_leaf IS NULL) OR "
           "(OLD.state='running' AND NEW.state='stop-pending' AND NEW.active_leaf IS OLD.active_leaf) OR "
           "(OLD.state IN ('running','stop-pending') AND NEW.state='recovery-required' "
           'AND NEW.active_leaf IS OLD.active_leaf) OR '
           "(OLD.state='stop-pending' AND NEW.state='stopped'))"),
)
BACKEND_SQL = TABLE_SQL + TRIGGER_SQL
INDEX_COUNTS = {'issuance': 3, 'campaign': 3, 'leaf': 4, 'binding': 2, 'launch': 2,
                'projection': 1, 'campaign_run': 3, 'leaf_plan': 2}


def validate_schema(db):
    """Exact SQL/index/connection checks, without creating or repairing anything."""
    validate_journal_schema(db)
    owned = {PREFIX + name for name in TABLE_COLUMNS}
    actual, indexes = set(), set()
    for kind, name, table, sql in db.execute('SELECT type,name,tbl_name,sql FROM main.sqlite_master'):
        if table in owned or name.startswith('backend_'):
            if sql is None:
                indexes.add((kind, name, table))
            else:
                actual.add(sql)
    expected_indexes = {('index', 'sqlite_autoindex_' + PREFIX + t + '_' + str(n), PREFIX + t)
                        for t, count in INDEX_COUNTS.items() for n in range(1, count + 1)}
    require(actual == set(BACKEND_SQL) and indexes == expected_indexes,
            'IntegrityFailure', 'Backend SQL/index inventory differs')
    require(not db.execute('PRAGMA foreign_key_check').fetchall(),
            'IntegrityFailure', 'Backend foreign key violation')
