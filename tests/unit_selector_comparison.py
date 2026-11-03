"""Tests for the equal-budget selector comparison."""

import copy
import email.message
import hashlib
import io
import json
import os
import shutil
import sys
import unittest
import tempfile
from pathlib import Path
import urllib.error

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

# These tests must never reach the network: force the Jev arm unavailable.
os.environ["GRRR_JEV_DISABLE"] = "1"

import jev_adapter
from selector_comparison import (
    ARMS,
    CORPUS_FREEZE_DIGEST,
    SelectorError,
    _digest,
    deterministic_select,
    jev_select,
    load_catalog,
    random_select,
    run_comparison,
    validate_selections,
)


CATALOG = (
    [f"GRRR-VC-D{i:03d}" for i in range(1, 25)]
    + [f"GRRR-VC-C{i:03d}" for i in range(1, 9)]
)
PUBLIC_CHALLENGES = json.loads(
    (ROOT / "corpus" / "public" / "challenges.json").read_bytes()
)
FAKE_KEY = "unit-boundary-credential-not-real"


def _write_json(path, value):
    path.write_bytes(json.dumps(value, separators=(",", ":")).encode())


def _rewrite_json(path, mutate):
    value = json.loads(path.read_bytes())
    mutate(value)
    _write_json(path, value)


def _rebind_public_hash(root):
    public_path = root / "public" / "challenges.json"
    expected = hashlib.sha256(public_path.read_bytes()).hexdigest()
    _rewrite_json(
        root / "manifest.json",
        lambda value: value["artifacts"].__setitem__(
            "public/challenges.json", expected
        ),
    )


def _recompute_freeze_digest(root):
    _rewrite_json(
        root / "manifest.json",
        lambda value: value.__setitem__(
            "freeze_digest",
            _digest({
                key: item for key, item in value.items()
                if key != "freeze_digest"
            }),
        ),
    )


def _mutate_manifest(root, mutate, *, recompute_freeze):
    _rewrite_json(root / "manifest.json", mutate)
    if recompute_freeze:
        _recompute_freeze_digest(root)


class TestSelectorComparison(unittest.TestCase):
    def test_deterministic_selects_lexical_order(self):
        result = deterministic_select(CATALOG, 8)
        self.assertEqual(result["selected"], sorted(CATALOG)[:8])

    def test_deterministic_is_reproducible(self):
        a = deterministic_select(CATALOG, 8, seed=123)
        b = deterministic_select(CATALOG, 8, seed=123)
        self.assertEqual(a["selected"], b["selected"])

    def test_random_selects_with_seed(self):
        result = random_select(CATALOG, 8, seed=42)
        self.assertEqual(len(result["selected"]), 8)
        self.assertNotEqual(result["selected"], sorted(CATALOG)[:8])

    def test_random_is_reproducible_with_same_seed(self):
        a = random_select(CATALOG, 8, seed=42)
        b = random_select(CATALOG, 8, seed=42)
        self.assertEqual(a["selected"], b["selected"])

    def test_random_different_with_different_seed(self):
        a = random_select(CATALOG, 8, seed=42)
        b = random_select(CATALOG, 8, seed=99)
        self.assertNotEqual(a["selected"], b["selected"])

    def test_jev_unavailable(self):
        result = jev_select(CATALOG, 8)
        self.assertFalse(result.get("available", False))
        self.assertEqual(result["selected"], [])
        self.assertIn("unavailable", result.get("reason", "").lower())

    def test_run_comparison_all_arms(self):
        result = run_comparison(CATALOG, 8)
        self.assertEqual(set(result["arms"]), set(ARMS))

    def test_comparison_incomplete_without_jev(self):
        result = run_comparison(CATALOG, 8)
        self.assertFalse(result["comparison_complete"])
        self.assertEqual(result["outcome"], "incomplete-jev-unavailable")

    def test_validate_selections_passes(self):
        result = run_comparison(CATALOG, 8)
        validate_selections(result["arms"])

    def test_corrupt_arms_reject(self):
        with self.assertRaises(SelectorError):
            validate_selections({"deterministic": {}})

    def test_equal_budget(self):
        result = run_comparison(CATALOG, 8)
        for arm in ("deterministic", "random"):
            self.assertEqual(result["arms"][arm]["budget"], 8)

    def test_catalog_freeze_digest_bound(self):
        result = run_comparison(CATALOG, 8)
        self.assertEqual(result["corpus_freeze_digest"], CORPUS_FREEZE_DIGEST)


def _response_for_ref(challenge_ref):
    """Return a deterministic valid score derived only from the opaque ref."""
    rotation = int(challenge_ref[-2:], 16) % 5
    distribution = [10, 10, 20, 20, 40]
    probabilities = {
        str(index): distribution[(index - rotation) % 5] / 100
        for index in range(5)
    }
    score = max(range(5), key=lambda index: probabilities[str(index)])
    return {
        "model": "jev-test",
        "answers": {
            "defect_likelihood": {
                "type": "score",
                "score": score,
                "confidence": 0.5,
                "legend": {0: "very unlikely", 4: "very likely"},
                "probabilities": probabilities,
            }
        },
        "usage": {"input_tokens": 100, "output_tokens": 10},
    }


class TestJevArmWithInjectedTransport(unittest.TestCase):
    """Proves the Jev arm ranks and reports without network access."""

    def setUp(self):
        self.records = []
        os.environ["GRRR_JEV_DISABLE"] = "0"
        self._original = {
            name: os.environ.get(name)
            for name in (
                "TYPESAFE_BASE_URL",
                "TYPESAFE_DEFAULT_MODEL",
            )
        }
        self._temporary = tempfile.TemporaryDirectory()
        self._orig_secret = jev_adapter.SECRET_FILE
        self._orig_build_opener = jev_adapter._build_opener
        os.environ["TYPESAFE_API_KEY"] = FAKE_KEY
        os.environ["TYPESAFE_BASE_URL"] = "https://typesafe.invalid"
        os.environ.pop("TYPESAFE_DEFAULT_MODEL", None)
        jev_adapter.SECRET_FILE = Path(self._temporary.name) / "absent-secret"
        jev_adapter._build_opener = self._forbid_network
        self.addCleanup(self._restore)

    def _forbid_network(self, *args, **kwargs):
        raise AssertionError("test attempted a real network call")

    def _restore(self):
        for name, value in self._original.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        # Never read, retain, or restore a real credential value in tests.
        os.environ.pop(jev_adapter.API_KEY_ENV, None)
        # The suite invariant is offline-by-default after every injected test.
        os.environ["GRRR_JEV_DISABLE"] = "1"
        jev_adapter.SECRET_FILE = self._orig_secret
        jev_adapter._build_opener = self._orig_build_opener
        self._temporary.cleanup()

    def _transport(self, response=None):
        def send(url, key, body, timeout):
            self.records.append((url, key, copy.deepcopy(body), timeout))
            if response is not None:
                return copy.deepcopy(response)
            return _response_for_ref(body["state"]["challenge_ref"])
        return send

    def test_jev_select_ranks_and_is_reproducible(self):
        first = jev_select(CATALOG, 8, transport=self._transport())
        second = jev_select(CATALOG, 8, transport=self._transport())
        self.assertTrue(first["available"])
        self.assertEqual(len(first["selected"]), 8)
        self.assertEqual(first["selected"], second["selected"])
        self.assertTrue(first["recommendation_only"])
        self.assertEqual(first["model"], ["jev-test"])
        self.assertEqual(first["usage"]["input_tokens"], 32 * 100)

    def test_jev_select_rejects_missing_public_metadata(self):
        with self.assertRaises(SelectorError):
            jev_select(["GRRR-VC-NOTREAL"], 8, transport=self._transport())

    def test_jev_ranking_is_probabilistic_not_verdict(self):
        result = jev_select(CATALOG, 8, transport=self._transport())
        validate_selections({
            "deterministic": deterministic_select(CATALOG, 8),
            "random": random_select(CATALOG, 8),
            "jev": result,
        })
        for entry in result["ranking"]:
            self.assertLessEqual(entry["confidence"], 1.0)

    def test_outbound_payload_has_no_semantic_ids_or_labels(self):
        jev_select(CATALOG, 32, transport=self._transport())
        self.assertEqual(len(self.records), len(CATALOG))
        semantic_markers = (
            "GRRR-VC-D", "GRRR-VC-C", "kind", "variant", "public_fixture",
            "seeded-defect", "clean-negative",
        )
        for url, key, body, timeout in self.records:
            self.assertEqual(url, "https://typesafe.invalid/v1/systemone")
            self.assertEqual(key, FAKE_KEY)
            self.assertEqual(timeout, jev_adapter.DEFAULT_TIMEOUT)
            self.assertEqual(set(body), {"state", "model", "questions"})
            self.assertEqual(set(body["state"]), {"challenge_ref", "category"})
            encoded = json.dumps(body, sort_keys=True)
            for marker in semantic_markers:
                self.assertNotIn(marker, encoded)
            for local_id in CATALOG:
                self.assertNotIn(local_id, encoded)
        refs = [body["state"]["challenge_ref"] for _, _, body, _ in self.records]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertTrue(all(ref.startswith("jch_") and len(ref) == 68 for ref in refs))

    def test_opaque_reference_is_frozen_and_local_mapping_retained(self):
        local_id = CATALOG[0]
        expected = jev_adapter.external_challenge_ref(local_id, CORPUS_FREEZE_DIGEST)
        self.assertTrue(expected.startswith("jch_"))
        self.assertNotEqual(
            expected,
            jev_adapter.external_challenge_ref(local_id, "0" * 64),
        )
        result = jev_select(CATALOG, 32, transport=self._transport())
        self.assertEqual(
            {entry["challenge"] for entry in result["ranking"]},
            {item["challenge"] for item in PUBLIC_CHALLENGES},
        )

    def test_run_comparison_accepts_injected_transport_without_network(self):
        result = run_comparison(CATALOG, 8, transport=self._transport())
        self.assertTrue(result["jev_available"])
        self.assertTrue(result["comparison_complete"])
        self.assertEqual(result["outcome"], "complete")
        validate_selections(result["arms"])

    def test_disabled_arm_is_unavailable_and_never_invokes_transport(self):
        os.environ["GRRR_JEV_DISABLE"] = "1"
        result = jev_select(CATALOG, 8, transport=self._transport())
        self.assertFalse(result["available"])
        self.assertEqual(result["selected"], [])
        self.assertEqual(self.records, [])

    def test_malformed_responses_fail_closed(self):
        valid = _response_for_ref("jch_" + "0" * 64)
        malformed = []

        def variant(change):
            value = copy.deepcopy(valid)
            change(value)
            malformed.append(value)

        variant(lambda value: value.pop("usage"))
        variant(lambda value: value["usage"].update(input_tokens=True))
        variant(lambda value: value["usage"].update(output_tokens=-1))
        variant(lambda value: value["answers"]["defect_likelihood"].update(score=4.1))
        variant(lambda value: value["answers"]["defect_likelihood"].update(confidence=1.1))
        variant(lambda value: value["answers"]["defect_likelihood"].update(score="3"))
        variant(lambda value: value.update(model=""))
        variant(lambda value: value["answers"]["defect_likelihood"]["probabilities"].update({"4": 0.0}))
        variant(lambda value: value["answers"]["defect_likelihood"].pop("probabilities"))
        variant(lambda value: value["answers"]["defect_likelihood"].update(type="text"))

        for response in malformed:
            with self.subTest(response=response):
                with self.assertRaises(jev_adapter.JevError):
                    jev_adapter.score_challenge(
                        PUBLIC_CHALLENGES[0],
                        corpus_freeze_digest=CORPUS_FREEZE_DIGEST,
                        api_key=FAKE_KEY,
                        base_url="https://typesafe.invalid",
                        transport=self._transport(response),
                    )

    def test_transport_error_is_sanitized(self):
        def send(url, key, body, timeout):
            raise RuntimeError("boundary failed " + FAKE_KEY)

        with self.assertRaises(jev_adapter.JevError) as raised:
            jev_adapter.score_challenge(
                PUBLIC_CHALLENGES[0],
                corpus_freeze_digest=CORPUS_FREEZE_DIGEST,
                api_key=FAKE_KEY,
                base_url="https://typesafe.invalid",
                transport=send,
            )
        self.assertNotIn(FAKE_KEY, str(raised.exception))

    def test_transport_jev_error_is_sanitized(self):
        def send(url, key, body, timeout):
            raise jev_adapter.JevError(
                "injected transport boundary failed " + FAKE_KEY
            )

        with self.assertRaises(jev_adapter.JevError) as raised:
            jev_adapter.score_challenge(
                PUBLIC_CHALLENGES[0],
                corpus_freeze_digest=CORPUS_FREEZE_DIGEST,
                api_key=FAKE_KEY,
                base_url="https://typesafe.invalid",
                transport=send,
            )
        self.assertNotIn(FAKE_KEY, str(raised.exception))
        self.assertNotIn("injected transport boundary failed", str(raised.exception))

    def test_successful_response_credential_echo_fails_closed(self):
        response = _response_for_ref(PUBLIC_CHALLENGES[0]["challenge"])
        response["model"] = FAKE_KEY
        selector_result = None

        with self.assertRaises(jev_adapter.JevError) as raised:
            selector_result = jev_select(
                CATALOG, 8, transport=self._transport(response)
            )

        message = str(raised.exception)
        self.assertEqual(message, jev_adapter.CREDENTIAL_ECHO_MESSAGE)
        self.assertNotIn(FAKE_KEY, message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertNotIn(FAKE_KEY, repr(raised.exception))
        self.assertEqual(len(self.records), 1)
        self.assertEqual(self.records[0][1], FAKE_KEY)
        self.assertIsNone(selector_result)
        serialized_selector_result = json.dumps(selector_result)
        self.assertEqual(serialized_selector_result, "null")
        self.assertNotIn(FAKE_KEY, serialized_selector_result)

    def test_redirect_is_rejected_without_following_authorization(self):
        installations = []
        attempts = []
        redirect_destinations = []
        redirect_rejections = []
        follow_ups = []

        class RecordingParent:
            def open(self, request, timeout=None):
                follow_ups.append(request.full_url)

        class RedirectOpener:
            def open(self, request, timeout=None):
                attempts.append(request.full_url)
                for destination in (
                    request.full_url,
                    "https://redirect.invalid/collect",
                ):
                    redirect_destinations.append(destination)
                    handler = jev_adapter._RejectRedirectHandler()
                    handler.parent = RecordingParent()
                    headers = email.message.Message()
                    headers["Location"] = destination
                    try:
                        handler.http_error_302(
                            request,
                            io.BytesIO(b"redirected"),
                            302,
                            "Found",
                            headers,
                        )
                    except urllib.error.HTTPError as rejection:
                        rejection_code = rejection.code
                        rejection.close()
                        redirect_rejections.append(
                            (destination, rejection_code)
                        )
                raise AssertionError("redirect handling unexpectedly completed")

        def build(*handlers):
            installations.append(handlers)
            return RedirectOpener()

        original_build = jev_adapter._build_opener
        jev_adapter._build_opener = build
        try:
            with self.assertRaises(jev_adapter.JevError) as raised:
                jev_adapter._http_post_json(
                    "https://typesafe.invalid/v1/systemone",
                    FAKE_KEY,
                    {"public": True},
                    jev_adapter.DEFAULT_TIMEOUT,
                )
        finally:
            jev_adapter._build_opener = original_build
        self.assertEqual(
            str(raised.exception),
            "Jev HTTP request failed; outcome is unknown",
        )
        self.assertNotIn(FAKE_KEY, str(raised.exception))
        self.assertEqual(len(installations), 1)
        self.assertTrue(any(
            handler is jev_adapter._RejectRedirectHandler
            for handler in installations[0]
        ))
        self.assertEqual(attempts, ["https://typesafe.invalid/v1/systemone"])
        self.assertEqual(redirect_destinations, [
            "https://typesafe.invalid/v1/systemone",
            "https://redirect.invalid/collect",
        ])
        self.assertEqual(redirect_rejections, [
            ("https://typesafe.invalid/v1/systemone", 302),
            ("https://redirect.invalid/collect", 302),
        ])
        self.assertEqual(follow_ups, [])

    def test_catalog_binding_rejects_mismatch_before_transport(self):
        invented = "GRRR-VC-ZZZZ"
        cases = [
            ("invented catalog ID", CATALOG + [invented], None),
            ("missing catalog ID", CATALOG[:-1], None),
            ("public artifact byte mismatch", CATALOG, lambda root: (
                root / "public" / "challenges.json"
            ).write_bytes(
                (root / "public" / "challenges.json").read_bytes() + b"\n"
            )),
            ("invented manifest ID", CATALOG, lambda root: _rewrite_json(
                root / "manifest.json",
                lambda value: value["challenge_ids"].append(invented),
            )),
        ]

        def remove_public_id(root):
            public_path = root / "public" / "challenges.json"
            public = json.loads(public_path.read_bytes())
            public.pop()
            _write_json(public_path, public)
            _rebind_public_hash(root)

        def add_public_id(root):
            public_path = root / "public" / "challenges.json"
            public = json.loads(public_path.read_bytes())
            entry = copy.deepcopy(public[0])
            entry["challenge"] = invented
            public.append(entry)
            _write_json(public_path, public)
            _rebind_public_hash(root)

        cases.extend((
            ("missing public ID", CATALOG, remove_public_id),
            ("extra public ID", CATALOG, add_public_id),
        ))

        for name, catalog, mutate in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    (root / "public").mkdir()
                    shutil.copyfile(
                        ROOT / "corpus" / "manifest.json", root / "manifest.json"
                    )
                    shutil.copyfile(
                        ROOT / "corpus" / "public" / "challenges.json",
                        root / "public" / "challenges.json",
                    )
                    if mutate is not None:
                        mutate(root)

                    with self.assertRaises(SelectorError):
                        jev_select(
                            catalog, 8, corpus_path=root,
                            transport=self._transport(),
                        )
                    self.assertEqual(self.records, [])

    def test_manifest_freeze_self_verification_rejects_forgery(self):
        invented = "GRRR-VC-ZZZZ"

        def append_manifest_id(value):
            value["challenge_ids"].append(invented)

        def replace_artifact_hash(value):
            value["artifacts"]["public/challenges.json"] = "0" * 64

        def rebind_public_bytes(root):
            public_path = root / "public" / "challenges.json"
            public = json.loads(public_path.read_bytes())
            entry = copy.deepcopy(public[0])
            entry["challenge"] = invented
            public.append(entry)
            _write_json(public_path, public)
            _rebind_public_hash(root)
            _recompute_freeze_digest(root)

        cases = (
            (
                "membership mutation with rebound freeze digest",
                True,
                (lambda root: _mutate_manifest(
                    root, append_manifest_id, recompute_freeze=True
                ),),
            ),
            (
                "artifact hash mutation with rebound freeze digest",
                True,
                (lambda root: _mutate_manifest(
                    root, replace_artifact_hash, recompute_freeze=True
                ),),
            ),
            (
                "membership forgery retaining pinned freeze literal",
                False,
                (lambda root: _mutate_manifest(
                    root, append_manifest_id, recompute_freeze=False
                ),),
            ),
            (
                "artifact-hash forgery retaining pinned freeze literal",
                False,
                (lambda root: _mutate_manifest(
                    root, replace_artifact_hash, recompute_freeze=False
                ),),
            ),
            (
                "rebound public bytes under a self-consistent forged manifest",
                True,
                (rebind_public_bytes,),
            ),
        )

        for name, rebound_freeze, mutations in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    (root / "public").mkdir()
                    shutil.copyfile(
                        ROOT / "corpus" / "manifest.json", root / "manifest.json"
                    )
                    shutil.copyfile(
                        ROOT / "corpus" / "public" / "challenges.json",
                        root / "public" / "challenges.json",
                    )
                    for mutate in mutations:
                        mutate(root)
                    forged = json.loads(
                        (root / "manifest.json").read_bytes()
                    )["freeze_digest"]
                    if rebound_freeze:
                        self.assertNotEqual(forged, CORPUS_FREEZE_DIGEST)

                    with self.assertRaises(SelectorError):
                        jev_select(
                            CATALOG, 8, corpus_path=root,
                            transport=self._transport(),
                        )
                    self.assertEqual(self.records, [])

    def test_non_https_base_url_rejects_before_transport(self):
        with self.assertRaises(jev_adapter.JevError):
            jev_adapter.score_challenge(
                PUBLIC_CHALLENGES[0],
                corpus_freeze_digest=CORPUS_FREEZE_DIGEST,
                api_key=FAKE_KEY,
                base_url="http://typesafe.invalid",
                transport=self._transport(),
            )
        self.assertEqual(self.records, [])

    def test_semantic_model_identifier_rejects_before_transport(self):
        with self.assertRaises(jev_adapter.JevError):
            jev_adapter.score_challenge(
                PUBLIC_CHALLENGES[0],
                corpus_freeze_digest=CORPUS_FREEZE_DIGEST,
                api_key=FAKE_KEY,
                base_url="https://typesafe.invalid",
                model="GRRR-VC-D001",
                transport=self._transport(),
            )
        self.assertEqual(self.records, [])

    def test_duplicate_response_fields_reject(self):
        raw = b'{"model":"x","model":"y","answers":{},"usage":{}}'
        with self.assertRaises(jev_adapter.JevError):
            jev_adapter._decode_response_bytes(raw)


if __name__ == "__main__":
    unittest.main()
