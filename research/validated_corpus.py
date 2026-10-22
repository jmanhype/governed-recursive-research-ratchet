"""Frozen vlt defect-corpus contracts and non-executing fixture validation.

The pinned source and protected answers are read from the accepted preserved v4
input. Seed recipes are reconstructed in memory only; no candidate binary is
built or run on the host.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import tarfile

from common import Failure, canonical, digest, fields, require
from trusted_execution import IMAGE, PRESERVED_ROOT, root_record

SOURCE_ARCHIVE = 'e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e'
SOURCE_COMMIT = '129e0b3f15a3bd6af949ee47d76f6855c582ab73'
LICENSE_BLOB = 'c004659349c7a1f6c55e5107b53a0766085e8d2e'
CORPUS_VERSION = 'GRRR-validated-corpus-v2.2-isolated'
FROZEN_AT = '2026-10-22T02:45:00Z'
CATEGORIES = (
    'filename-title-resolution', 'alias-collision-precedence', 'case-path-lookup',
    'links-headings-inert', 'frontmatter-index-invalidation', 'rename-delete-cache',
    'concurrency-locking', 'filesystem-invalid-paths', 'deterministic-repetition',
    'integrity-tampering',
)

# (file, anchor, replacement, critical, expected protected behavior)
DEFECTS = (
    ('vault.go', 'return strings.HasPrefix(name, ".") || name == ".trash"',
     'return false', True, 'Hidden and trash directories remain excluded from indexing.'),
    ('index.go', 'if rel, ok := idx.byExactName[title+".md"]; ok {',
     'if rel, ok := idx.byLowerTitle[strings.ToLower(title)]; ok {', True,
     'Exact filename lookup precedes alias lookup and preserves filename case.'),
    ('index.go', 'if _, ok := idx.byLowerAlias[la]; !ok {', 'if true {', False,
     'The first alias in deterministic walk order wins a collision.'),
    ('index.go', 'if _, ok := idx.byExactName[name]; !ok {', 'if true {', True,
     'The first exact filename in lexical walk order wins a duplicate collision.'),
    ('index.go', '\tif rel, ok := idx.byLowerTitle[norm]; ok {\n\t\treturn rel, true\n\t}\n\tif rel, ok := idx.byLowerRelNoExt[norm]; ok {\n\t\treturn rel, true\n\t}',
     '\tif false {\n\t\treturn rel, true\n\t}\n\tif false {\n\t\treturn rel, true\n\t}', True,
     'Note-title lookup is case-insensitive.'),
    ('index.go', '\tif rel, ok := idx.byLowerFile[norm]; ok {\n\t\treturn rel, true\n\t}\n\tif rel, ok := idx.byLowerRel[norm]; ok {\n\t\treturn rel, true\n\t}',
     '\tif false {\n\t\treturn rel, true\n\t}\n\tif false {\n\t\treturn rel, true\n\t}', True,
     'Attachment and embed filenames resolve without an .md extension.'),
    ('index.go', 'idx.byLowerAlias[strings.ToLower(title)]', 'idx.byLowerAlias[title]', False,
     'Frontmatter aliases resolve case-insensitively.'),
    ('wikilinks.go', 'text = MaskInertContent(text)', 'text = text', True,
     'Wikilinks inside every registered inert zone are ignored.'),
    ('wikilinks.go', 'Embed: m[1] == "!"', 'Embed: false', True,
     'Embed syntax is represented as an embed and participates in backlinks.'),
    ('wikilinks.go', 'wl.BlockID = fragment[1:]', 'wl.BlockID = fragment', False,
     'A block-reference ID excludes its caret prefix.'),
    ('wikilinks.go', 'if len(m) > 4 {', 'if false {', True,
     'Wikilink display text is captured.'),
    ('commands.go', 'if len(matches) > 1 {', 'if false {', False,
     'Duplicate headings return an ambiguous-heading error instead of selecting the first.'),
    ('frontmatter.go', "if line == \"\" || line[0] == ' ' || line[0] == '\\t' {",
     'if line == "" {', True, 'Only top-level frontmatter keys match search and property operations.'),
    ('frontmatter.go', r'''p = strings.Trim(p, "\"'")''', 'p = p', False,
     'Inline alias list members strip one balanced surrounding quote pair.'),
    ('commands.go', '\tv.registry.register(v.dir, fullPath, contentBytes)\n\tv.invalidateIndex()',
     '\tv.registry.register(v.dir, fullPath, contentBytes)', True,
     'Creating a file invalidates the cached vault index.'),
    ('commands.go', 'if _, err := os.Stat(toPath); err == nil && !force {', 'if false {', True,
     'Move refuses an existing destination unless force is explicitly set.'),
    ('commands.go', 'if oldRelNoExt != oldTitle && oldRelNoExt != newRelNoExt {', 'if false {', True,
     'Folder-only moves rewrite path-form wikilinks.'),
    ('commands.go', '\tv.registry.deregister(v.dir, fullPath)\n\tv.invalidateIndex()\n\treturn fmt.Sprintf("trashed:',
     '\tv.registry.deregister(v.dir, fullPath)\n\treturn fmt.Sprintf("trashed:', False,
     'Trashing a note also invalidates the stale cached index entry.'),
    ('lock.go', 'if bounded && time.Now().After(deadline) {', 'if false {', True,
     'A bounded lock timeout returns an error rather than waiting indefinitely.'),
    ('commands.go', 'if text != "" && !strings.HasSuffix(text, "\\n") && content != "" && !strings.HasPrefix(content, "\\n") {\n\t\ttext += "\\n"\n\t}',
     'if text != "" && !strings.HasSuffix(text, "\\n") && content != "" && !strings.HasPrefix(content, "\\n") {\n\t}', True,
     'Appending to a note lacking a final newline inserts the separator newline.'),
    ('vault.go', 'if filepath.IsAbs(userPath) {', 'if false {', True,
     'Absolute user paths are rejected before joining them to the vault root.'),
    ('vault.go', 'if cleaned != filepath.Clean(vaultDir) && !strings.HasPrefix(cleaned, vaultPrefix) {',
     'if false {', True, 'A cleaned traversal result outside the vault prefix is rejected.'),
    ('commands.go', 'if ranges[i].start <= last.end+1 {', 'if ranges[i].start < last.end {', False,
     'Adjacent search-context repetitions merge deterministically.'),
    ('integrity.go', '\tif entry.Hash == contentHash(content) {\n\t\treturn IntegrityOK\n\t}',
     '\tif true {\n\t\treturn IntegrityOK\n\t}', True,
     'Changed content is reported as an integrity mismatch.'),
)

CLEAN = (
    ('create/read round trip', 'ordinary title and path return the exact bytes'),
    ('alias resolution', 'a frontmatter alias reaches the owning note'),
    ('inert-zone negative', 'a wikilink inside fenced code is not indexed'),
    ('frontmatter preservation', 'write replaces the body and preserves frontmatter'),
    ('rename propagation', 'move updates title and path references'),
    ('traversal denial', 'absolute and .. paths are rejected'),
    ('missing-note denial', 'an absent title returns not-found rather than fabricating a note'),
    ('integrity mismatch', 'external content change reports mismatch without silently resetting'),
)


def _write(root: Path, relative: str, value: object) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical(value)
    path.write_bytes(raw)
    return digest(raw)


def _iso_records(raw: bytes) -> dict[str, tuple[int, int]]:
    require(raw[32768:32775] == b'\x01CD001\x01', 'IntegrityFailure', 'Primary ISO descriptor absent')
    root = raw[32924:32958]
    offset = int.from_bytes(root[2:6], 'little') * 2048
    size = int.from_bytes(root[10:14], 'little')
    directory = raw[offset:offset + size]
    records: dict[str, tuple[int, int]] = {}
    position = 0
    while position < len(directory):
        length = directory[position]
        if not length:
            position = (position // 2048 + 1) * 2048
            continue
        record = directory[position:position + length]
        require(len(record) >= 34, 'IntegrityFailure', 'Truncated ISO directory record')
        name = record[33:33 + record[32]]
        if name not in (b'\x00', b'\x01'):
            normalized = name.decode('ascii').split(';')[0].lower().rstrip('.')
            records[normalized] = (int.from_bytes(record[2:6], 'little') * 2048,
                                   int.from_bytes(record[10:14], 'little'))
        position += length
    return records


def pinned_source(preserved_root: Path = PRESERVED_ROOT) -> tuple[bytes, dict[str, bytes]]:
    """Read and verify vlt.tar from the exact protected v4 input image."""
    receipt = root_record(preserved_root / 'preparation.json')
    image = protected_image(preserved_root, receipt)
    expected = receipt['primary_iso_readback']['vlt.tar']['sha256']
    records = _iso_records(image)
    require('vlt.tar' in records, 'GateBlocked', 'vlt.tar absent from pinned ISO namespace')
    offset, size = records['vlt.tar']
    archive_raw = image[offset:offset + size]
    require(digest(archive_raw) == SOURCE_ARCHIVE == expected,
            'IntegrityFailure', 'Pinned vlt source archive differs')
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive_raw), mode='r:') as archive:
        inventory = receipt['source']['files']
        require(sorted(archive.getnames()) == sorted(inventory),
                'IntegrityFailure', 'Pinned source membership differs')
        for member in archive:
            require(member.isfile() and not Path(member.name).is_absolute()
                    and '..' not in Path(member.name).parts,
                    'IntegrityFailure', 'Unsafe source archive member')
            data = archive.extractfile(member).read()
            require(digest(data) == inventory[member.name]['sha256'],
                    'IntegrityFailure', 'Pinned source bytes differ: ' + member.name)
            files[member.name] = data
    require(len(files) == 52 and receipt['source']['commit'] == SOURCE_COMMIT
            and receipt['source']['license_blob'] == LICENSE_BLOB,
            'IntegrityFailure', 'Pinned source identity differs')
    return archive_raw, files


def pinned_iso_member(name: str, preserved_root: Path = PRESERVED_ROOT) -> bytes:
    """Read one exact primary-namespace member from the preserved v4 input."""
    require(name in {'go.tgz', 'guest.sh', 'input.sum', 'source.sum', 'supervis', 'helper'},
            'InvalidInput', 'Unregistered v4 ISO member')
    receipt = root_record(preserved_root / 'preparation.json')
    image = protected_image(preserved_root, receipt)
    records = _iso_records(image)
    require(name in records, 'GateBlocked', 'v4 ISO member absent: ' + name)
    offset, size = records[name]
    raw = image[offset:offset + size]
    expected = receipt['primary_iso_readback'].get(name, {}).get('sha256')
    require(expected is None or digest(raw) == expected,
            'IntegrityFailure', 'v4 ISO member differs: ' + name)
    return raw


def protected_image(preserved_root: Path = PRESERVED_ROOT, receipt: dict | None = None) -> bytes:
    image_path = preserved_root / 'input.iso'
    raw = image_path.read_bytes()
    require(digest(raw) == IMAGE == receipt['image_sha256'],
            'IntegrityFailure', 'Preserved v4 input image differs')
    return raw


def scenario_records(files: dict[str, bytes]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    public_records: list[dict] = []
    seed_records: list[dict] = []
    truth_records: list[dict] = []
    specs: list[dict] = []
    for number, (source_file, anchor, replacement, critical, behavior) in enumerate(DEFECTS, 1):
        challenge = f'GRRR-VC-D{number:03d}'
        seed = {'challenge': challenge, 'kind': 'single-unique-replacement', 'file': source_file,
                'anchor': anchor, 'replacement': replacement}
        public_records.append({
            'challenge': challenge, 'kind': 'seeded-defect', 'category': None,
            'public_fixture': 'disposable pinned-source vault invocation', 'variant': digest(canonical(seed)),
        })
        seed_records.append(seed)
        truth_records.append({'challenge': challenge, 'truth': 'defect', 'critical': critical,
                              'expected_behavior': behavior})
        specs.append(_spec(challenge, source_file, behavior, critical))
    for number, (name, behavior) in enumerate(CLEAN, 1):
        challenge = f'GRRR-VC-C{number:03d}'
        seed = {'challenge': challenge, 'kind': 'clean-control', 'file': None,
                'anchor': None, 'replacement': None}
        public_records.append({
            'challenge': challenge, 'kind': 'clean-negative', 'category': None,
            'public_fixture': name, 'variant': digest(canonical(seed)),
        })
        seed_records.append(seed)
        truth_records.append({'challenge': challenge, 'truth': 'clean', 'critical': False,
                              'expected_behavior': behavior})
        specs.append(_spec(challenge, 'pinned authoritative tests', behavior, False))
    categories = [CATEGORIES[number % len(CATEGORIES)] for number in range(len(public_records))]
    for record, category in zip(public_records, categories):
        record['category'] = category
    return public_records, seed_records, truth_records, specs


def _spec(challenge: str, source_file: str, behavior: str, critical: bool) -> dict:
    return {
        'challenge': challenge,
        'specification': 'vlt README and pinned source tests at commit ' + SOURCE_COMMIT,
        'specification_digest': digest((SOURCE_COMMIT + '\0' + source_file).encode('ascii')),
        'expected_behavior': behavior,
        'provenance': {'source_commit': SOURCE_COMMIT, 'file': source_file,
                       'license_blob': LICENSE_BLOB},
        'ambiguity': 'validated', 'critical': critical,
    }


def apply_seed(files: dict[str, bytes], seed: dict) -> str:
    fields(seed, {'challenge', 'kind', 'file', 'anchor', 'replacement'})
    if seed['kind'] == 'clean-control':
        require(seed['file'] is None and seed['anchor'] is None and seed['replacement'] is None,
                'InvalidInput', 'Clean control has no source mutation')
        return digest(canonical(seed))
    require(seed['kind'] == 'single-unique-replacement' and seed['file'] in files,
            'InvalidInput', 'Unknown seed target')
    anchor, replacement = seed['anchor'].encode('utf-8'), seed['replacement'].encode('utf-8')
    count = files[seed['file']].count(anchor)
    require(anchor != replacement and count == 1,
            'IntegrityFailure', f'Seed anchor count {count} for {seed["challenge"]} in {seed["file"]}')
    mutated = files[seed['file']].replace(anchor, replacement, 1)
    return digest(canonical({'seed': seed, 'source_sha256': digest(files[seed['file']]),
                             'mutated_sha256': digest(mutated)}))


def build(root: Path, preserved_root: Path = PRESERVED_ROOT) -> dict:
    """Generate the frozen public/protected projections from pinned source."""
    archive_raw, files = pinned_source(preserved_root)
    public_records, seeds, truths, specs = scenario_records(files)
    for record, seed in zip(public_records, seeds):
        record['variant'] = apply_seed(files, seed)
    public_specs = [{key: value for key, value in spec.items()
                     if key not in ('expected_behavior', 'critical')}
                    for spec in specs]
    holdouts = sorted(record['challenge'] for record in public_records[::4])
    training = sorted(record['challenge'] for record in public_records[1::2])
    measurement = sorted(set(record['challenge'] for record in public_records) - set(holdouts) - set(training))
    hashes: dict[str, str] = {}
    hashes['public/challenges.json'] = _write(root, 'corpus/public/challenges.json', public_records)
    hashes['public/spec-map.json'] = _write(root, 'corpus/public/spec-map.json', public_specs)
    hashes['protected/seeds.json'] = _write(root, 'corpus/protected/seeds.json', seeds)
    hashes['protected/truth.json'] = _write(root, 'corpus/protected/truth.json', truths)
    hashes['protected/holdouts.json'] = _write(root, 'corpus/protected/holdouts.json', holdouts)
    hashes['spec-map.json'] = _write(root, 'corpus/spec-map.json', specs)
    plan = {
        'version': 1, 'corpus_version': CORPUS_VERSION, 'frozen_at': FROZEN_AT,
        'arm_order': ['deterministic-risk', 'random', 'jev-guided'],
        'seeds': {'deterministic-risk': 'a' * 64, 'random': 'b' * 64, 'jev-guided': 'c' * 64},
        'randomized_repetitions': 3, 'feasibility_exception': 'No arm executes before corpus approval; VM feasibility remains not-run.',
        'feedback_policy': {'training': training, 'permitted': 'challenge IDs and aggregate pass/fail only',
                            'prohibited': 'labels, expected behavior, holdout membership, protected seeds'},
        'stopping': {'max_challenges_per_arm': 32, 'stop_on_hard_gate_failure': True,
                     'ties': 'lower public ID after exact defect-deduplication'},
        'deduplication': 'one credit per protected truth challenge; repeated observation adds no denominator',
        'cost': {'allocation': 'per isolated invocation', 'amortization': 'source build charged to first arm repetition',
                 'denominator': 'unique detected truth labels divided by fully allocated cost'},
        'uncertainty': 'bootstrap 95% interval over challenge labels and three fixed-seed repetitions',
        'approval': {'state': 'not-approved', 'measurement_started': False},
    }
    hashes['evaluation-plan.json'] = _write(root, 'corpus/evaluation-plan.json', plan)
    manifest = {
        'version': 1, 'visibility': 'protected-operator-review',
        'corpus_version': CORPUS_VERSION, 'frozen_at': FROZEN_AT,
        'source': {'commit': SOURCE_COMMIT, 'license_blob': LICENSE_BLOB,
                   'archive_sha256': digest(archive_raw), 'source_files': len(files),
                   'input_iso_sha256': IMAGE},
        'counts': {'defects': len(DEFECTS), 'clean': len(CLEAN), 'total': len(public_records),
                   'critical': sum(1 for item in DEFECTS if item[3])},
        'categories': list(CATEGORIES), 'challenge_ids': [item['challenge'] for item in public_records],
        'partitions': {'training': training, 'measurement': measurement, 'holdout': holdouts},
        'artifacts': hashes,
        'public_projection': 'corpus/public; no truth, expected behavior, seed anchors, or holdout membership',
        'protected_projection': 'corpus/protected plus corpus/spec-map.json',
        'fixture_validation': {'path': 'static source-recipe and accepted v4 observation reference only',
                               'seeded_variant_execution': 'not-run',
                               'blocked_reason': 'new reviewed input/profile and non-stopped accounting required'},
    }
    manifest['freeze_digest'] = digest(canonical(manifest))
    _write(root, 'corpus/manifest.json', manifest)
    return manifest


def load_json(path: Path) -> object:
    value = json.loads(path.read_bytes())
    require(isinstance(value, (dict, list)), 'InvalidInput', 'Corpus record must be structured JSON')
    return value


def validate(root: Path, preserved_root: Path = PRESERVED_ROOT) -> dict:
    """Fail closed on corpus drift; this never builds or executes a candidate."""
    corpus = root / 'corpus'
    manifest = load_json(corpus / 'manifest.json')
    fields(manifest, {'version', 'corpus_version', 'frozen_at', 'source', 'counts', 'categories',
                      'challenge_ids', 'partitions', 'artifacts', 'public_projection', 'visibility',
                      'protected_projection', 'fixture_validation', 'freeze_digest'})
    require(manifest['visibility'] == 'protected-operator-review',
            'GateBlocked', 'Root corpus manifest must not be treated as selector-visible')
    frozen = {key: value for key, value in manifest.items() if key != 'freeze_digest'}
    require(manifest['version'] == 1 and manifest['corpus_version'] == CORPUS_VERSION
            and manifest['frozen_at'] == FROZEN_AT and digest(canonical(frozen)) == manifest['freeze_digest'],
            'IntegrityFailure', 'Corpus freeze digest differs')
    for relative, expected in manifest['artifacts'].items():
        require(digest((corpus / relative).read_bytes()) == expected,
                'IntegrityFailure', 'Corpus artifact differs: ' + relative)
    public = load_json(corpus / 'public/challenges.json')
    seeds = load_json(corpus / 'protected/seeds.json')
    truths = load_json(corpus / 'protected/truth.json')
    specs = load_json(corpus / 'spec-map.json')
    require(manifest['counts'] == {'defects': 24, 'clean': 8, 'total': 32, 'critical': 17},
            'InvalidInput', 'Corpus counts differ')
    require(set(manifest['categories']) == set(CATEGORIES) and len(manifest['categories']) == len(CATEGORIES),
            'InvalidInput', 'Required category coverage differs')
    require(len(public) == len(seeds) == len(truths) == len(specs) == 32,
            'InvalidInput', 'Corpus projection lengths differ')
    archive_raw, files = pinned_source(preserved_root)
    variants = []
    for record, seed, truth, spec in zip(public, seeds, truths, specs):
        challenge = record['challenge']
        require(challenge == seed['challenge'] == truth['challenge'] == spec['challenge'],
                'IntegrityFailure', 'Challenge binding differs')
        variant = apply_seed(files, seed)
        variants.append(variant)
        require(record['variant'] == variant and truth['truth'] == ('defect' if seed['kind'] != 'clean-control' else 'clean'),
                'IntegrityFailure', 'Seed/truth differs for ' + challenge)
        require(spec['ambiguity'] == 'validated' and spec['expected_behavior'] == truth['expected_behavior'],
                'GateBlocked', 'Unsupported specification for ' + challenge)
    require(len(set(variants)) == 32, 'IntegrityFailure', 'Corpus variants are not independent')
    public_raw = (corpus / 'public/challenges.json').read_bytes() + (corpus / 'public/spec-map.json').read_bytes()
    for leaked in ('expected_behavior', '"truth"', 'critical', 'anchor', 'replacement', 'holdout'):
        require(leaked.encode('ascii') not in public_raw, 'GateBlocked', 'Protected corpus data leaked publicly')
    snapshot_path = root / 'docs/evidence/trusted-observation/v4-run-9d3df87/evaluator/snapshot.json'
    snapshot = json.loads(snapshot_path.read_bytes())
    from ledger import verifySnapshot
    verifySnapshot(snapshot, snapshot['receipt']['digest'])
    completed = sum(1 for row in snapshot['events'] if row['event'].get('decision', {}).get('baseline_correctness'))
    clean_pass = sum(1 for row in snapshot['events']
                     if row['event'].get('decision', {}).get('baseline_correctness') == 'pass')
    fault_fail = sum(1 for row in snapshot['events']
                     if row['event'].get('decision', {}).get('baseline_correctness') == 'fail')
    require(completed == 8 and clean_pass == 2 and fault_fail == 6,
            'IntegrityFailure', 'Accepted v4 observation summary differs')
    return {
        'status': 'static-validation-pass; seeded isolated execution not-run',
        'corpus_version': CORPUS_VERSION, 'freeze_digest': manifest['freeze_digest'],
        'source_archive_sha256': digest(archive_raw), 'variants': len(set(variants)),
        'defects': 24, 'clean': 8, 'critical': 17,
        'accepted_v4_observation': {'snapshot_sha256': digest(snapshot_path.read_bytes()),
                                    'receipt': snapshot['receipt']['digest'], 'completed': completed,
                                    'clean_pass': clean_pass, 'fault_fail': fault_fail},
        'blocked_gates': {'seeded_variant_execution': 'not-run',
                          'independent_replay': 'not-run', 'admission': 'blocked',
                          'reason': 'pinned v4 input admits only fixed variants; new reviewed profile/input required'},
        'verified': False, 'admission': 'blocked',
    }


def generate_report(root: Path, preserved_root: Path = PRESERVED_ROOT) -> dict:
    if not (root / 'corpus/manifest.json').is_file():
        build(root, preserved_root)
    result = validate(root, preserved_root)
    evidence = root / 'docs/evidence/validated-corpus'
    evidence.mkdir(parents=True, exist_ok=True)
    result_path = evidence / 'corpus-validation.json'
    result_path.write_bytes(canonical(result))
    return result


if __name__ == '__main__':
    import sys
    require(len(sys.argv) == 2, 'InvalidInput', 'Usage: validated_corpus.py REPO_ROOT')
    root = Path(sys.argv[1]).resolve(strict=True)
    build(root)
    print(canonical(generate_report(root)).decode('ascii'))
