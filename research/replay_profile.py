"""Fixed replay-only artifact pins. No caller-selected image or identity."""
from pathlib import Path
from common import EVALUATOR, RUNNER, canonical, digest, fields, identifier, require
from corpus_execution import SUPERVISOR, HELPER, LIMITS as CORPUS_LIMITS
from corpus_evaluation import _validate_receipt
from persistent_budget import ACTIVE
from replay_fixtures import FLOOR, catalog
from trusted_execution import configuration_digest, protected_bytes, root_record

ROOT = Path('/Library/GRRR/independent-replay-input/v1')
IMAGE = '977783b9bae0b76e7288afbf31e9018b86a7345072b5729257f8392d45e256cf'
PROFILE = '01cc844ee183f88c4d897e3be523add2708d07c0c6913fda992a3899be9e8de3'
RECEIPT = '38a4cf0dc3740d2bad964c593b4598b5837a6b3b76f6f49c5644af39b1f30640'
PINS = {'input.iso': IMAGE, 'prepared-profile.json': PROFILE, 'preparation.json': RECEIPT}
LIMITS = dict(CORPUS_LIMITS, minimum_host_free_bytes=FLOOR)


def identity() -> dict:
    return {'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR, 'helper': HELPER}


def validate_inputs() -> dict:
    require(ROOT.is_absolute() and not ROOT.is_symlink() and
            {entry.name for entry in ROOT.iterdir()} == set(PINS),
            'IntegrityFailure', 'Replay-only artifact membership differs')
    return {name: digest(protected_bytes(ROOT / name, hashed)) for name, hashed in PINS.items()}


def configure(config: dict) -> dict:
    """Parent-only projection keeps the same cumulative accounting authority."""
    result = dict(config, **identity())
    result.update(limits=LIMITS, corpus_binding=digest(canonical(catalog())),
                  accounting_binding=digest(canonical(root_record(ACTIVE))))
    result['execution_profile'] = configuration_digest(result)
    return validate_config(result)


def validate_config(config: dict) -> dict:
    fields(config, {'version', 'profile', 'image', 'supervisor', 'helper', 'host_code', 'operator_uid',
                   'limits', 'network', 'host_shares', 'paid_dispatch', 'read_only_inputs',
                   'qemu_installation', 'corpus_binding', 'accounting_binding', 'bootstrap_sha256',
                   'python_sha256', 'execution_profile'})
    for name in ('host_code', 'qemu_installation', 'bootstrap_sha256', 'python_sha256', 'accounting_binding'):
        identifier(config[name], True)
    require(type(config['version']) is int and config['version'] == 1
            and all(config[name] == hashed for name, hashed in identity().items())
            and config['limits'] == LIMITS and config['network'] is False
            and config['host_shares'] is False and config['paid_dispatch'] is False
            and config['read_only_inputs'] is True
            and config['corpus_binding'] == digest(canonical(catalog()))
            and config['accounting_binding'] == digest(canonical(root_record(ACTIVE)))
            and type(config['operator_uid']) is int and config['operator_uid'] not in (0, EVALUATOR, RUNNER)
            and config['execution_profile'] == configuration_digest(config),
            'GateBlocked', 'Replay execution profile differs')
    return config


def validate_receipt(value: dict, request: dict, execution_profile: str) -> dict:
    return _validate_receipt(value, request, execution_profile, identity())
