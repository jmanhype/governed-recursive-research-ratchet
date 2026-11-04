"""No backend, grant issuance, accounting reader, or runtime capability installed."""
import os
from pathlib import Path
from common import Failure, require
from capstone_contract import validate_record
from capstone_client import test_endpoint
from trusted_transport import AuthenticatedServer


class RefusalService:
    def __init__(self, operator_uid: int) -> None:
        require(type(operator_uid) is int and 0 < operator_uid < 4294967295
                and operator_uid not in (320, 321), 'InvalidInput', 'Invalid operator UID')
        self.operator_uid = operator_uid

    def handle(self, authenticated_uid: int, request: dict) -> dict:
        """Principal must come from transport; this direct API is not authentication."""
        require(type(authenticated_uid) is int and authenticated_uid == self.operator_uid,
                'Unauthorized', 'Operator identity differs')
        require(type(request) is dict, 'InvalidInput', 'Expected request')
        require(type(request.get('version')) is int and request['version'] == 1,
                'InvalidInput', 'UnsupportedProtocolVersion')
        action = request.get('action')
        require(type(action) is str and action in ('observe', 'start', 'status', 'stop'),
                'InvalidInput', 'Unknown action')
        validate_record(request, action.title())
        if action in ('status', 'stop'):
            raise Failure('Unavailable', 'Operation capability absent; no cessation or settlement claimed')
        bindings = request['request']['bindings'] if action == 'observe' else request['plan']['request']['bindings']
        if bindings['accounting_version'] != 1:
            raise Failure('RecoveryRequired', 'UnsupportedAccountingVersion:%d' % bindings['accounting_version'])
        # Receipt requires an issued raw grant hash. None exists: do not manufacture
        # a receipt from caller claims, a zero balance, or an invented null digest.
        raise Failure('RecoveryRequired', 'GrantUnissued: history unknown; allowance null; start blocked')


class TestService:
    """Ephemeral unprivileged sockets only; NEVER installed endpoint evidence."""
    def __init__(self, root: Path) -> None:
        require(os.getuid() not in (0, 320, 321), 'Unauthorized', 'Unprivileged fixture required')
        data = test_endpoint(root / 'data.sock')
        control = test_endpoint(root / 'control.sock')
        facade = RefusalService(os.getuid())
        self.data = AuthenticatedServer(Path(data), facade.handle, allowed_uid=os.getuid())
        try:
            self.control = AuthenticatedServer(Path(control), facade.handle, control=True, allowed_uid=os.getuid())
        except Exception:
            self.data.close()
            raise

    def close(self) -> None:
        self.data.close()
        self.control.close()


def test_service(root: Path) -> TestService:
    return TestService(root)
