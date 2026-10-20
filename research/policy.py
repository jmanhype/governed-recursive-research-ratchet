"""Registered immutable policy and authenticated evaluator-only loading."""
import os
from pathlib import Path
import json
from common import EVALUATOR, GATES, Failure, canonical, digest, fields, require

LIMITS = {'memory_mib': 512, 'vcpus': 1, 'boot_seconds': 30,
          'command_seconds': 5,
          'stop_ack_seconds': 2, 'term_grace_seconds': 5, 'output_bytes': 1048576,
          'challenge_seconds': 300, 'minimum_free_bytes': 15000000000,
          'poc_execution_seconds': 21600, 'milestone_execution_seconds': 86400,
          'poc_money_cents': 5000, 'milestone_money_cents': 15000,
          'poc_review_seconds': 3600, 'milestone_review_seconds': 10800,
          'concurrent_challenges': 1}


def default_policy(operator: int) -> dict:
    return {'version': 1, 'operator_uid': operator, 'challenge': 'grrr-walk-001',
            'limits': LIMITS, 'gates': list(GATES), 'paid_dispatch': False,
            'semantic': 'synthetic-walkthrough-only; exact CLEAN newline and exit zero',
            'replay_review_admission': 'not-run'}


def loadPolicy(principal: int, path: Path, ref: str) -> dict:
    require(principal == EVALUATOR and os.getuid() == EVALUATOR,
            'Unauthorized', 'Only evaluator may load protected policy')
    require(path.is_file() and not path.is_symlink(), 'Unavailable', 'Missing protected policy')
    stat = path.stat()
    require(stat.st_uid == EVALUATOR and stat.st_mode & 0o077 == 0,
            'IntegrityFailure', 'Policy ownership/mode invalid')
    raw = path.read_bytes()
    require(digest(raw) == ref, 'StaleBinding', 'Policy digest mismatch')
    policy = json.loads(raw)
    require(policy == default_policy(policy.get('operator_uid')),
            'InvalidInput', 'Unregistered policy configuration')
    return policy
