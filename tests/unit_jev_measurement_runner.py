import copy
import contextlib
import io
import json
import os
import tempfile
import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

import jev_adapter  # noqa: E402
import jev_measurement_runner as runner  # noqa: E402
import selector_comparison  # noqa: E402


FAKE_KEY = "test-only-not-a-real-credential"
AUTHORIZATION = {
    "schema_version": 1,
    "authorized_by": "operator-speed",
    "action": "typesafe-jev-selector-measurement",
    "corpus_freeze_digest": selector_comparison.CORPUS_FREEZE_DIGEST,
    "max_calls": 32,
    "selected_budget": 8,
    "retries_allowed": False,
    "measured_usage": "token-only",
    "credential_echo_fail_closed": True,
    "approval_quote": "operator approval quote for offline runner proof",
    "approval_time": "2026-11-03T19:13:27Z",
}


def response_for_ref(challenge_ref):
    probabilities = {str(index): 0.2 for index in range(5)}
    return {
        "model": "jev-test",
        "answers": {
            "defect_likelihood": {
                "type": "score",
                "score": 2,
                "confidence": 0.5,
                "legend": {0: "unlikely", 4: "likely"},
                "probabilities": probabilities,
            }
        },
        "usage": {"input_tokens": 101, "output_tokens": 11},
    }


class OfflineRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        # Resolve macOS's /var -> /private/var symlink before handing a path to
        # the runner; the runner itself deliberately refuses symlink ancestors.
        self.root = Path(self.temporary.name).resolve()
        self.authorization_path = self.root / "authorization.json"
        self.authorization_path.write_text(
            json.dumps(AUTHORIZATION, sort_keys=True), encoding="utf-8"
        )
        self.originals = {
            name: os.environ.get(name)
            for name in (
                runner.REAL_RUN_ENV,
                jev_adapter.API_KEY_ENV,
                jev_adapter.BASE_URL_ENV,
                jev_adapter.DISABLE_ENV,
            )
        }
        self.original_available = selector_comparison.jev_adapter.is_available
        self.original_key = selector_comparison.jev_adapter.resolve_api_key
        self.original_build = selector_comparison.jev_adapter._build_opener
        os.environ[jev_adapter.API_KEY_ENV] = FAKE_KEY
        os.environ[jev_adapter.DISABLE_ENV] = "0"
        os.environ.pop(runner.REAL_RUN_ENV, None)
        self.addCleanup(self._restore)

    def _restore(self):
        selector_comparison.jev_adapter.is_available = self.original_available
        selector_comparison.jev_adapter.resolve_api_key = self.original_key
        selector_comparison.jev_adapter._build_opener = self.original_build
        for name, value in self.originals.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temporary.cleanup()

    def _forbid_real_boundary(self):
        selector_comparison.jev_adapter.is_available = lambda: (_ for _ in ()).throw(
            AssertionError("availability was probed before refusal")
        )
        selector_comparison.jev_adapter._build_opener = lambda *args: (_ for _ in ()).throw(
            AssertionError("network opener was constructed")
        )

    def _enable_injected_adapter(self):
        selector_comparison.jev_adapter.is_available = lambda: True
        selector_comparison.jev_adapter.resolve_api_key = lambda: FAKE_KEY
        selector_comparison.jev_adapter._build_opener = lambda *args: (_ for _ in ()).throw(
            AssertionError("network opener was constructed")
        )

    def _write_authorization(self, value):
        self.authorization_path.write_text(
            json.dumps(value, sort_keys=True), encoding="utf-8"
        )

    def _events(self, output):
        return [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]

    def _report(self, output):
        return json.loads((output / "report.json").read_text())

    def test_default_invocation_refuses_before_secret_availability_or_network(self):
        self._forbid_real_boundary()
        output = self.root / "refused-output"
        code = runner.main(
            ["--authorization", str(self.authorization_path), "--output-dir", str(output)],
            environ={},
        )
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_malformed_authorization_refuses_before_availability_probe(self):
        bad = copy.deepcopy(AUTHORIZATION)
        bad["extra"] = True
        self._write_authorization(bad)
        self._forbid_real_boundary()
        output = self.root / "refused-output"
        code = runner.main(
            ["--authorization", str(self.authorization_path), "--output-dir", str(output)],
            environ={runner.REAL_RUN_ENV: "1"},
        )
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_exact_schema_rejects_missing_wrong_and_extra_fields(self):
        missing = copy.deepcopy(AUTHORIZATION)
        missing.pop("retries_allowed")
        wrong = copy.deepcopy(AUTHORIZATION)
        wrong["max_calls"] = 33
        extra = copy.deepcopy(AUTHORIZATION)
        extra["endpoint"] = "https://typesafe.invalid"
        for value in (missing, wrong, extra):
            self._write_authorization(value)
            with self.subTest(value=value):
                with self.assertRaises(runner.AuthorizationError):
                    runner.load_authorization(self.authorization_path)

    def test_exact_schema_rejects_float_and_boolean_integers(self):
        invalid_values = [
            ("schema_version", 1.0),
            ("schema_version", True),
            ("max_calls", 32.0),
            ("max_calls", True),
            ("selected_budget", 8.0),
            ("selected_budget", False),
        ]
        for field, value in invalid_values:
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(AUTHORIZATION)
                invalid[field] = value
                self._write_authorization(invalid)
                self._forbid_real_boundary()
                with self.assertRaises(runner.AuthorizationError):
                    runner.load_authorization(self.authorization_path)

    def test_default_cli_transport_records_adapter_http_calls_offline(self):
        requests = []

        class FakeResponse(io.BytesIO):
            status = 200

        class FakeOpener:
            def open(self, request, timeout):
                body = json.loads(request.data.decode("utf-8"))
                requests.append((request.full_url, dict(request.headers), body, timeout))
                return FakeResponse(json.dumps(
                    response_for_ref(body["state"]["challenge_ref"])
                ).encode("utf-8"))

        self._enable_injected_adapter()
        selector_comparison.jev_adapter._build_opener = lambda handler: FakeOpener()
        output = self.root / "default-cli-transport"
        code = runner.main(
            ["--authorization", str(self.authorization_path), "--output-dir", str(output)],
            environ={runner.REAL_RUN_ENV: "1"},
        )

        self.assertEqual(code, 0)
        self.assertEqual(len(requests), 32)
        self.assertTrue(all(
            request[0] == "https://api.typesafe.ai/v1/systemone"
            for request in requests
        ))
        report = self._report(output)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["attempts"], {
            "attempted_calls": 32,
            "returned_responses": 32,
            "retry_count": 0,
        })
        events = self._events(output)
        self.assertEqual(len(events), 64)
        self.assertEqual(
            [event["event"] for event in events[::2]],
            ["call_attempt_started"] * 32,
        )
        self.assertEqual(
            [event["event"] for event in events[1::2]],
            ["call_attempt_finished"] * 32,
        )

    def _transport(self, records):
        def send(url, key, body, timeout):
            records.append((url, key, copy.deepcopy(body), timeout))
            return response_for_ref(body["state"]["challenge_ref"])
        return send

    def test_complete_run_is_one_shot_sums_usage_and_never_retries(self):
        records = []
        self._enable_injected_adapter()
        output = self.root / "complete"
        report = runner.execute_measurement(
            AUTHORIZATION,
            "0" * 64,
            output,
            transport=self._transport(records),
        )
        self.assertEqual(report["status"], "complete")
        self.assertEqual(len(records), 32)
        self.assertEqual(report["attempts"], {
            "attempted_calls": 32,
            "returned_responses": 32,
            "retry_count": 0,
        })
        self.assertEqual(report["usage"]["input_tokens"], 32 * 101)
        self.assertEqual(report["usage"]["output_tokens"], 32 * 11)
        self.assertTrue(report["usage"]["observation_complete"])
        self.assertIsNone(report["cost"]["usd"])
        self.assertEqual(report["cost"]["status"], "unknown-until-independent-receipt")
        self.assertEqual(len(report["selector_result"]["selected"]), 8)
        self.assertEqual(len(report["local_challenge_mapping"]), 32)

        events = self._events(output)
        self.assertEqual(len(events), 64)
        self.assertEqual([event["sequence"] for event in events], list(range(1, 65)))
        self.assertEqual(
            [event["event"] for event in events[::2]],
            ["call_attempt_started"] * 32,
        )
        self.assertEqual(
            [event["event"] for event in events[1::2]],
            ["call_attempt_finished"] * 32,
        )
        self.assertTrue(all(event["outcome"] == "transport-returned"
                            for event in events[1::2]))

    def test_partial_adapter_failure_preserves_events_and_omits_result(self):
        records = []

        def send(url, key, body, timeout):
            records.append((url, key, copy.deepcopy(body), timeout))
            raise RuntimeError("transport failed with " + FAKE_KEY)

        self._enable_injected_adapter()
        output = self.root / "partial"
        report = runner.execute_measurement(
            AUTHORIZATION, "0" * 64, output, transport=send
        )
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["failure_code"], "jev-adapter-failed")
        self.assertEqual(report["attempts"]["attempted_calls"], 1)
        self.assertEqual(report["attempts"]["retry_count"], 0)
        self.assertIsNone(report["selector_result"])
        self.assertEqual(report["local_challenge_mapping"], [])
        self.assertFalse(report["usage"]["observation_complete"])
        self.assertEqual(
            report["next_action"], "operator-review-required; do not automatically rerun"
        )
        events = self._events(output)
        self.assertEqual([event["event"] for event in events],
                         ["call_attempt_started", "call_attempt_finished"])
        self.assertEqual(events[-1]["outcome"], "transport-exception")
        self.assertEqual(len(records), 1)
        event_bytes = (output / "events.jsonl").read_bytes()
        report_bytes = (output / "report.json").read_bytes()
        self.assertNotIn(FAKE_KEY.encode(), event_bytes)
        self.assertNotIn(FAKE_KEY.encode(), report_bytes)
        self.assertNotIn(b"transport failed", event_bytes)
        self.assertNotIn(b"transport failed", report_bytes)

    def test_successful_response_credential_echo_never_reaches_report(self):
        records = []

        def send(url, key, body, timeout):
            records.append((url, key, copy.deepcopy(body), timeout))
            response = response_for_ref(body["state"]["challenge_ref"])
            response["model"] = FAKE_KEY
            return response

        self._enable_injected_adapter()
        output = self.root / "credential-echo"
        report = runner.execute_measurement(
            AUTHORIZATION, "0" * 64, output, transport=send
        )
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["failure_code"], "jev-adapter-failed")
        self.assertIsNone(report["selector_result"])
        self.assertEqual(report["attempts"]["attempted_calls"], 1)
        event_bytes = (output / "events.jsonl").read_bytes()
        report_bytes = (output / "report.json").read_bytes()
        self.assertNotIn(FAKE_KEY.encode(), event_bytes)
        self.assertNotIn(FAKE_KEY.encode(), report_bytes)
        self.assertEqual(len(records), 1)

    def test_max_call_enforcement_occurs_before_an_extra_attempt(self):
        records = []

        def send(url, key, body, timeout):
            records.append(body)
            return {"transport": "injected-offline"}

        event_path = self.root / "events.jsonl"
        event_path.write_text(
            json.dumps({"existing": True}, sort_keys=True,
                       separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        # Re-open through the production writer with O_APPEND and prove the old
        # bytes remain a prefix after two new fixed-shape records.
        parent = runner._open_existing_directory(event_path.parent)
        original_open = runner.os.open

        def append_only_open(path, flags, mode=0o777, dir_fd=None):
            return original_open(path, flags & ~runner.os.O_EXCL, mode, dir_fd=dir_fd)

        runner.os.open = append_only_open
        try:
            log = runner.EventLog(parent, "append-test")
            recorder = runner.CallRecorder(send, log, 1)
            self.assertIsNotNone(recorder(
                "https://typesafe.invalid",
                FAKE_KEY,
                {"state": {"challenge_ref": "jch_" + "0" * 64,
                           "category": "integrity-tampering"}},
                1.0,
            ))
            with self.assertRaises(runner.CallLimitExceeded):
                recorder("https://typesafe.invalid", FAKE_KEY, {"state": {}}, 1.0)
            log.close()
        finally:
            runner.os.open = original_open
            parent.close()
        self.assertEqual(len(records), 1)
        raw = event_path.read_bytes()
        self.assertTrue(raw.startswith(b'{"existing":true}\n'))
        appended = [json.loads(line) for line in raw.splitlines()[1:]]
        self.assertEqual(len(appended), 2)
        self.assertEqual([event["event"] for event in appended],
                         ["call_attempt_started", "call_attempt_finished"])
        self.assertEqual([event["sequence"] for event in appended], [1, 2])

    def test_outputs_have_no_credentials_and_events_have_no_semantic_payload(self):
        records = []
        self._enable_injected_adapter()
        output = self.root / "sanitized"
        runner.execute_measurement(
            AUTHORIZATION, "0" * 64, output, transport=self._transport(records)
        )
        event_bytes = (output / "events.jsonl").read_bytes()
        report_bytes = (output / "report.json").read_bytes()
        self.assertNotIn(FAKE_KEY.encode(), event_bytes)
        self.assertNotIn(FAKE_KEY.encode(), report_bytes)
        self.assertNotIn(b"https://typesafe.invalid", event_bytes)
        self.assertNotIn(b"Authorization", event_bytes)
        for marker in selector_comparison.jev_adapter.BANNED_OUTBOUND_MARKERS:
            self.assertNotIn(marker.encode(), event_bytes)
        for local_id in selector_comparison.load_catalog(runner.DEFAULT_CORPUS_ROOT):
            self.assertNotIn(local_id.encode(), event_bytes)
        for _, _, body, _ in records:
            encoded = json.dumps(body, sort_keys=True)
            for marker in selector_comparison.jev_adapter.BANNED_OUTBOUND_MARKERS:
                self.assertNotIn(marker, encoded)
            self.assertEqual(set(body), {"state", "model", "questions"})
            self.assertEqual(set(body["state"]), {"challenge_ref", "category"})

    def test_final_report_failure_after_calls_is_unknown_and_never_no_call(self):
        records = []
        self._enable_injected_adapter()
        output = self.root / "post-call-report-failure"
        original_write = runner._exclusive_json_write
        original_http_post = runner.jev_adapter._http_post_json
        runner.jev_adapter._http_post_json = self._transport(records)

        def failing_write(directory, name, value):
            raise runner.OutputError("injected final report failure")

        runner._exclusive_json_write = failing_write
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stderr(stderr):
                code = runner.main(
                    [
                        "--authorization", str(self.authorization_path),
                        "--output-dir", str(output),
                    ],
                    environ={runner.REAL_RUN_ENV: "1"},
                )
        finally:
            runner._exclusive_json_write = original_write
            runner.jev_adapter._http_post_json = original_http_post

        self.assertEqual(code, 4)
        self.assertEqual(len(records), 32)
        events = self._events(output)
        self.assertEqual(len(events), 64)
        self.assertFalse((output / "report.json").exists())
        message = stderr.getvalue()
        self.assertIn("INCOMPLETE/UNKNOWN", message)
        self.assertIn("32 attempted adapter call(s)", message)
        self.assertIn("do not automatically rerun", message)
        self.assertNotIn("no adapter call was made", message)


class SafePathTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def _authorization(self):
        return {
            **AUTHORIZATION,
            "corpus_freeze_digest": selector_comparison.CORPUS_FREEZE_DIGEST,
        }

    def _write_authorization(self, path):
        path.write_text(
            json.dumps(self._authorization(), sort_keys=True), encoding="utf-8"
        )

    def test_lexical_rejection_precedes_any_target_filesystem_syscall(self):
        originals = {
            name: getattr(runner.os, name)
            for name in ("open", "mkdir", "stat", "lstat", "readlink")
        }

        def refuse_filesystem_call(*args, **kwargs):
            raise AssertionError("filesystem boundary called before lexical rejection")

        for name in originals:
            setattr(runner.os, name, refuse_filesystem_call)
        try:
            paths = [
                Path("/Library/GRRR/authorization.json"),
                Path("/Library/GRRR/new-output"),
                Path(self.root / "authorization" / ".." / "authorization.json"),
                Path(self.root / "output" / ".." / "new-output"),
            ]
            for path in paths:
                with self.subTest(path=path):
                    with self.assertRaises(runner.OutputError):
                        runner._absolute_path_or_refuse(path)
        finally:
            for name, value in originals.items():
                setattr(runner.os, name, value)

    def test_double_leading_slash_rejects_authorization_and_output_before_syscalls(self):
        original_path = runner.Path
        original_abspath = runner.os.path.abspath
        originals = {
            name: getattr(runner.os, name)
            for name in ("open", "mkdir", "stat", "lstat", "readlink")
        }

        def refuse_normalization(value, *args, **kwargs):
            raise AssertionError(
                "target path reached Path/abspath normalization before rejection"
            )

        def make_refuse_target_filesystem_call(original):
            def refuse_target_filesystem_call(*args, **kwargs):
                rendered = repr(args) + repr(kwargs)
                if "Library/GRRR" in rendered:
                    raise AssertionError(
                        "target path reached a filesystem syscall before rejection"
                    )
                return original(*args, **kwargs)
            return refuse_target_filesystem_call

        runner.Path = refuse_normalization
        runner.os.path.abspath = refuse_normalization
        for name, original in originals.items():
            setattr(runner.os, name, make_refuse_target_filesystem_call(original))
        try:
            for prefix in ("//", "///"):
                with self.subTest(form="authorization", prefix=prefix):
                    with self.assertRaises(runner.OutputError):
                        runner.load_authorization(
                            prefix + "Library/GRRR/authorization.json"
                        )
                with self.subTest(form="public-output", prefix=prefix):
                    with self.assertRaises(runner.OutputError):
                        runner.execute_measurement(
                            AUTHORIZATION,
                            "0" * 64,
                            prefix + "Library/GRRR/new-output",
                        )
        finally:
            runner.Path = original_path
            runner.os.path.abspath = original_abspath
            for name, value in originals.items():
                setattr(runner.os, name, value)

    def test_authorization_rejects_symlinked_ancestor_and_leaf(self):
        real = self.root / "real"
        real.mkdir()
        authorization = real / "authorization.json"
        self._write_authorization(authorization)
        ancestor_link = self.root / "ancestor-link"
        ancestor_link.symlink_to(real, target_is_directory=True)
        leaf_link = self.root / "authorization-link.json"
        leaf_link.symlink_to(authorization)

        with self.assertRaises(runner.OutputError):
            runner.load_authorization(ancestor_link / "authorization.json")
        with self.assertRaises(runner.OutputError):
            runner.load_authorization(leaf_link)

    def test_output_rejects_symlinked_ancestor_and_existing_leaf(self):
        with self.assertRaises(runner.OutputError):
            runner._safe_output_directory(Path("/"))

        real = self.root / "real-output-parent"
        real.mkdir()
        ancestor_link = self.root / "ancestor-link"
        ancestor_link.symlink_to(real, target_is_directory=True)
        with self.assertRaises(runner.OutputError):
            runner._safe_output_directory(ancestor_link / "new-output")

        existing_leaf = self.root / "existing-output"
        existing_leaf.mkdir()
        with self.assertRaises(runner.OutputError):
            runner._safe_output_directory(existing_leaf)

        symlink_leaf = self.root / "symlink-output"
        symlink_leaf.symlink_to(real, target_is_directory=True)
        with self.assertRaises(runner.OutputError):
            runner._safe_output_directory(symlink_leaf)

    def test_evidence_descriptor_writes_do_not_follow_a_replaced_leaf(self):
        directory = runner._safe_output_directory(self.root / "replacement-race")
        try:
            flags = runner.os.O_WRONLY | runner.os.O_CREAT | runner.os.O_EXCL
            descriptor = directory.open("events.jsonl", flags, 0o600)
            replacement_target = self.root / "replacement-target"
            replacement_target.write_bytes(b"outside replacement\n")
            replacement = self.root / "replacement-link"
            replacement.symlink_to(replacement_target)
            os.replace(replacement, directory.path / "events.jsonl")
            os.write(descriptor, b"held safe descriptor\n")
            os.close(descriptor)

            replaced = directory.path / "events.jsonl"
            self.assertTrue(replaced.is_symlink())
            self.assertEqual(replacement_target.read_bytes(), b"outside replacement\n")
        finally:
            directory.close()


if __name__ == "__main__":
    unittest.main()
