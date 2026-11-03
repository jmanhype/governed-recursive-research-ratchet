"""Operator-authorized TypeSafe Jev broker adapter.

This module is the *only* place the research runner talks to the external
TypeSafe service.  It upholds the architecture contract:

* the candidate never reaches the network; only this broker does;
* only sanitized, public corpus metadata is transmitted (never source code,
  holdout fixtures, credentials, or raw experiment logs);
* the API credential is read from the environment or an operator-owned
  secret file and is never written to the repository, logs, or evidence;
* the returned value is a *probabilistic recommendation*, never a verdict.

The HTTP call is implemented with the standard library so the repository
keeps a minimal dependency surface.
"""

import hashlib
import json
import math
import os
import re
import stat
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

API_KEY_ENV = "TYPESAFE_API_KEY"
BASE_URL_ENV = "TYPESAFE_BASE_URL"
MODEL_ENV = "TYPESAFE_DEFAULT_MODEL"
DISABLE_ENV = "GRRR_JEV_DISABLE"

DEFAULT_BASE_URL = "https://api.typesafe.ai"
DEFAULT_MODEL = "jev-latest"
SYSTEM_ONE_PATH = "/v1/systemone"
MODELS_PATH = "/v1/models"
DEFAULT_TIMEOUT = 30.0
MAX_RESPONSE_BYTES = 1_000_000
MAX_TEXT_BYTES = 128
PROBABILITY_EPSILON = 1e-6
CREDENTIAL_ECHO_MESSAGE = "Jev response failed credential safety validation"
EXTERNAL_REF_DOMAIN = b"grrr-jev-opaque-v1"
BANNED_OUTBOUND_MARKERS = (
    "GRRR-VC-D",
    "GRRR-VC-C",
    "kind",
    "variant",
    "public_fixture",
    "seeded-defect",
    "clean-negative",
)

ALLOWED_CATEGORIES = frozenset({
    "alias-collision-precedence",
    "case-path-lookup",
    "concurrency-locking",
    "deterministic-repetition",
    "filename-title-resolution",
    "filesystem-invalid-paths",
    "frontmatter-index-invalidation",
    "integrity-tampering",
    "links-headings-inert",
    "rename-delete-cache",
})

# Operator-owned fallback secret location (mode 0600, outside the repo).
SECRET_FILE = Path.home() / ".codex" / "secrets" / "jev_api_key"

SCORE_CRITERIA = (
    "very unlikely this challenge exposes a real defect",
    "unlikely",
    "plausible",
    "likely",
    "very likely this challenge exposes a real defect",
)


class JevError(RuntimeError):
    """Raised when the Jev broker cannot produce a usable answer."""


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse redirects, including same-origin redirects.

    urllib's redirect implementation preserves authenticated request headers.
    A redirect is therefore an authorization-boundary change even when the
    destination looks harmless; never construct the follow-up request.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url, code, "Jev redirect rejected", headers, fp
        )


_build_opener = urllib.request.build_opener


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise JevError(detail)


def _bounded_text(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(value)
             and len(value.encode("utf-8")) <= MAX_TEXT_BYTES,
             f"Jev {label} is invalid")
    return value


def _outbound_model(value: Any) -> str:
    model = _bounded_text(value, "model")
    _require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", model) is not None,
             "Jev model identifier is invalid")
    _require(not any(marker in model for marker in BANNED_OUTBOUND_MARKERS),
             "Jev model identifier contains prohibited corpus semantics")
    return model


def _number(value: Any, label: str, minimum: float, maximum: float) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool)
             and math.isfinite(float(value))
             and minimum <= float(value) <= maximum,
             f"Jev {label} is invalid")
    return float(value)


def _token_count(value: Any) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool)
             and 0 <= value <= 10**12,
             "Jev token count is invalid")
    return value


def _require_https_url(url: str) -> None:
    parsed = urlsplit(url)
    _require(isinstance(url, str) and parsed.scheme == "https"
             and bool(parsed.hostname) and parsed.username is None
             and parsed.password is None and not parsed.query and not parsed.fragment,
             "Jev base URL is invalid")


def external_challenge_ref(challenge_id: str, corpus_freeze_digest: str) -> str:
    """Return a deterministic non-semantic external challenge reference."""
    _require(isinstance(challenge_id, str)
             and re.fullmatch(r"GRRR-VC-[A-Za-z0-9]{4}", challenge_id) is not None,
             "Jev local challenge identifier is invalid")
    _require(isinstance(corpus_freeze_digest, str)
             and re.fullmatch(r"[0-9a-f]{64}", corpus_freeze_digest) is not None,
             "Jev corpus freeze digest is invalid")
    material = (EXTERNAL_REF_DOMAIN + b"\0" + corpus_freeze_digest.encode("ascii")
                + b"\0" + challenge_id.encode("ascii"))
    return "jch_" + hashlib.sha256(material).hexdigest()


def _public_state(challenge: Mapping[str, Any], corpus_freeze_digest: str) -> Dict[str, str]:
    """Build the sole allowlisted outbound representation of a challenge."""
    _require(set(challenge) == {"challenge", "category", "kind", "public_fixture", "variant"},
             "Jev public challenge projection has unexpected fields")
    category = challenge.get("category")
    _require(isinstance(category, str) and category in ALLOWED_CATEGORIES,
             "Jev public category is not allowlisted")
    return {
        "challenge_ref": external_challenge_ref(challenge["challenge"], corpus_freeze_digest),
        "category": category,
    }


def _unique_json_object(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _decode_response_bytes(raw: bytes) -> Dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise JevError("Jev response is not valid JSON") from exc
    _require(isinstance(value, dict), "Jev response must be an object")
    return value


def _validated_response(response: Any) -> Dict[str, Any]:
    _require(isinstance(response, Mapping), "Jev response must be an object")
    model = _bounded_text(response.get("model"), "model")
    answers = response.get("answers")
    _require(isinstance(answers, Mapping), "Jev answers must be an object")
    answer = answers.get("defect_likelihood")
    _require(isinstance(answer, Mapping), "Jev defect answer must be an object")
    _require(answer.get("type") == "score", "Jev defect answer has the wrong type")

    probabilities_value = answer.get("probabilities")
    _require(isinstance(probabilities_value, Mapping)
             and set(probabilities_value) == {str(index) for index in range(len(SCORE_CRITERIA))},
             "Jev probability indices are incomplete")
    probabilities = {
        int(index): _number(value, "probability", 0.0, 1.0)
        for index, value in probabilities_value.items()
    }
    _require(abs(sum(probabilities.values()) - 1.0) <= PROBABILITY_EPSILON,
             "Jev probabilities do not sum to one")

    usage_value = response.get("usage")
    _require(isinstance(usage_value, Mapping)
             and set(usage_value) == {"input_tokens", "output_tokens"},
             "Jev usage inventory is invalid")
    usage = {
        name: _token_count(usage_value.get(name))
        for name in ("input_tokens", "output_tokens")
    }
    expected_weight = sum(
        weight * probability
        for weight, probability in probabilities.items()
    )
    _number(expected_weight, "expected defect weight", 0.0, float(len(SCORE_CRITERIA) - 1))
    return {
        "model": model,
        "score": _number(answer.get("score"), "score", 0.0, float(len(SCORE_CRITERIA) - 1)),
        "confidence": _number(answer.get("confidence"), "confidence", 0.0, 1.0),
        "probabilities": probabilities,
        "expected_defect_weight": expected_weight,
        "usage": usage,
    }


def _reject_credential_echo(response: Any, credential: str) -> None:
    """Reject a successful response if any JSON string echoes the credential."""
    pending = [response]
    seen_containers: Dict[int, Any] = {}
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            _require(credential not in value, CREDENTIAL_ECHO_MESSAGE)
        elif isinstance(value, Mapping):
            marker = id(value)
            if marker in seen_containers:
                continue
            seen_containers[marker] = value
            pending.extend(value.keys())
            pending.extend(value.values())
        elif isinstance(value, (list, tuple, set, frozenset)):
            marker = id(value)
            if marker in seen_containers:
                continue
            seen_containers[marker] = value
            pending.extend(value)


def resolve_api_key() -> Optional[str]:
    """Return the operator-provisioned key, or None when unprovisioned."""
    key = os.environ.get(API_KEY_ENV, "").strip()
    if key:
        return key
    try:
        if SECRET_FILE.is_file():
            mode = stat.S_IMODE(SECRET_FILE.stat().st_mode)
            if mode & 0o077:
                raise JevError("Jev secret file permissions are too broad")
            key = SECRET_FILE.read_text().strip()
            return key or None
    except (OSError, UnicodeError):
        return None
    return None


def resolve_base_url() -> str:
    return (os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL).rstrip("/")


def resolve_model() -> str:
    model = _outbound_model(os.environ.get(MODEL_ENV) or DEFAULT_MODEL)
    return model


def is_available() -> bool:
    """True only when an operator-provisioned credential exists.

    ``GRRR_JEV_DISABLE=1`` forces the arm unavailable so tests and offline
    runs never reach the network.
    """
    if os.environ.get(DISABLE_ENV, "").strip() not in ("", "0"):
        return False
    return resolve_api_key() is not None


def _http_post_json(url: str, key: str, body: Dict, timeout: float) -> Dict:
    _require_https_url(url)
    payload = json.dumps(body, separators=(",", ":"), allow_nan=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        # The explicit handler is the security boundary: default urlopen would
        # follow redirects and could forward Authorization to the destination.
        with _build_opener(_RejectRedirectHandler).open(
            request, timeout=timeout
        ) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            status = getattr(response, "status", None)
            _require(not (isinstance(status, int) and 300 <= status < 400),
                     "Jev HTTP response was a redirect")
        _require(len(raw) <= MAX_RESPONSE_BYTES, "Jev response is too large")
        return _decode_response_bytes(raw)
    except Exception:  # pragma: no cover - network path
        raise JevError("Jev HTTP request failed; outcome is unknown") from None


def score_challenge(
    challenge: Dict,
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    corpus_freeze_digest: str,
    timeout: float = DEFAULT_TIMEOUT,
    transport: Optional[Callable[[str, str, Dict, float], Dict]] = None,
) -> Dict:
    """Ask Jev for the probability that one public challenge exposes a defect.

    ``challenge`` must contain only sanitized public metadata.
    """
    key = api_key if api_key is not None else resolve_api_key()
    if not isinstance(key, str) or not key:
        raise JevError("no operator-provisioned Jev credential")

    state = _public_state(challenge, corpus_freeze_digest)
    body = {
        "state": state,
        "model": _outbound_model(model) if model is not None else resolve_model(),
        "questions": {
            "defect_likelihood": {
                "type": "score",
                "criteria": list(SCORE_CRITERIA),
            }
        },
    }
    send = transport or _http_post_json
    url = f"{(base_url or resolve_base_url())}{SYSTEM_ONE_PATH}"
    _require_https_url(url)
    try:
        response = send(url, key, body, timeout)
    except Exception:
        raise JevError("Jev transport failed; outcome is unknown") from None
    _reject_credential_echo(response, key)
    validated = _validated_response(response)

    return {
        "challenge": challenge["challenge"],
        "challenge_ref": state["challenge_ref"],
        "category": state["category"],
        **validated,
    }


def rank_challenges(
    challenges: Sequence[Dict],
    *,
    corpus_freeze_digest: str,
    transport: Optional[Callable[[str, str, Dict, float], Dict]] = None,
    **kwargs,
) -> List[Dict]:
    """Score every challenge and return a deterministic descending ranking.

    Ties break on the opaque reference so the arm stays reproducible.
    """
    _require(bool(challenges), "Jev ranking requires at least one challenge")
    local_ids = [challenge.get("challenge") for challenge in challenges]
    _require(all(isinstance(value, str) for value in local_ids)
             and len(local_ids) == len(set(local_ids)),
             "Jev ranking contains duplicate or invalid challenge IDs")
    scored = [
        score_challenge(
            challenge,
            corpus_freeze_digest=corpus_freeze_digest,
            transport=transport,
            **kwargs,
        )
        for challenge in challenges
    ]
    refs = [item["challenge_ref"] for item in scored]
    _require(len(refs) == len(set(refs)), "Jev opaque references collided")
    scored.sort(key=lambda item: (-item["expected_defect_weight"],
                                  -item["score"],
                                  item["challenge_ref"]))
    return scored
