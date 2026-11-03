# GRRR-z3w9 Stage Q independent review request

## Exact scope

Review only the sandbox-only v4 installer core, checkout CLI, tests, retained
session-durability repair, and retained logs/report. Do not access or mutate
`/Library/GRRR`. Do not stage protected records, execute a protected installer,
amend a budget, reconcile, execute replay, admit, promote, mutate production,
merge, or push.

## Base state

- Story HEAD: `5c130a02958042975c8522f71e134f19627c999d`
- Stage P package SHA-256:
  `ba7e8a45486a21ff399027821d3b0bd1d21c6577730597f900f3c21fb192c0b1`
- Stage P review:
  `STAGE_P_NARROW_REWORK_REVIEW: APPROVED`

## Installer files and identities

- `research/replay_successor_installer.py`
  SHA-256 `7a190063907675da2e017098a411fb097b66cfff812bc8d568aef31525257939`
- `scripts/install-replay-successor-v4`
  SHA-256 `7ee2728f99408b2f83b6626fe61c187d91d3b6d04b386e026e68fdc7abcaaaa3`
- `tests/unit_replay_successor_installer.py`
  SHA-256 `8c50a598a0a4d21ce5a0e554b88310d8151be5bde042ba8c956954a17ce500e1`

## Durability files and identities

- `research/spendability_provenance.py`
  SHA-256 `9595d8ad932a4b26579a5c48ac77632b210e488ac82722a31a000a02e3695cce`
- `research/spendability_per_record.py`
  SHA-256 `6ba7d803d54df752ca65390cd57890c064df8810253e7df3bc4e58eb284a1985`
- `research/spendability_request_search.py`
  SHA-256 `f1110d740feec51ec22e32a889202187097c930b1fd5dcdda6e65ee4172e5f33`
- `tests/unit_spendability_provenance.py`
  SHA-256 `01db40fc3934d6d73c6bca0104307cd6a80d42ab8aa777074bf6be40779116e6`
- `tests/unit_spendability_per_record.py`
  SHA-256 `38de0010620261f8452c925ff36d063f5e5c48f34872bd1f20a1973d68bb41dd`
- `tests/unit_spendability_request_search.py`
  SHA-256 `212e6e04178fddbf84d5d229f07c5161a8b84485fff536c4b4f8cd4a13e863ec`
- `docs/evidence/spendability/stage-l/RETAINED-SESSION-SEARCH.json`
  SHA-256 `e568f36d965aa425971744573b562f005c3f1279ba73fef7610bc495224faaa3`

## Logs

- `docs/evidence/replay-authority/stage-q/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `0972ed674d44400427e782b86e7c5d81acb284127f3bcdbd1a7b19ae58d9fe00`
- `docs/evidence/replay-authority/stage-q/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `304ddb452d09184b0f8baa950f9743a22a474f1a2f36cee997d23ee7a7ee0236`
- `docs/evidence/replay-authority/stage-q/FULL-HOMEBREW-3.14.log`
  SHA-256 `bbe13281625f3603e6e2fd4bbe7e65410d6f15180fdb43accfc5b41c761098dc`
- `docs/evidence/replay-authority/stage-q/FULL-MINICONDA-3.12.log`
  SHA-256 `609812ee26596d876f2f2ed6288a47ed970473db5a5325751d5413985919862b`

## Independent commands to rerun

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_spendability_provenance.py' -v
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_spendability_per_record.py' -v
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_spendability_request_search.py' -v
```

## Review questions

1. Does the installer core operate only on caller-supplied sandbox paths and
   never on `/Library/GRRR`?
2. Does it validate the exact eight roles, distinct hashes, Stage N/O basis,
   predecessor identities, plan, review, and external authorization?
3. Does it reject wrong root/toolchain identity, source tampering, target
   collision, authority injection, and malformed schema types before effects?
4. Does successful sandbox installation create only a stopped, empty v4 store
   with no budget, reconciliation, replay, admission, promotion, merge, or push
   authority?
5. Does injected failure preserve uncertain evidence without retry or success?
6. Does postflight verify binding/database hashes, device/inode, integrity,
   stopped state, exact tables, and empty accounting rows?
7. Does the checkout CLI refuse malformed grammar and even exact live grammar?
8. Does the durability repair preserve original-source identity and uncertainty
   without treating a missing mutable session archive as zero or fabricating
   raw bytes?
9. Are retained fallbacks hash-pinned and subordinate to live source
   reproduction when the original archive exists?
10. Does implementation avoid weakening any existing accounting/replay gate?

## Required verdict

Return exactly one:

- `STAGE_Q_INSTALLER_CORE_REVIEW: APPROVED`
- `STAGE_Q_INSTALLER_CORE_REVIEW: REJECTED`

Approval covers only this repository-retained WIP. It does not approve exact
protected source issuance, protected staging, operator authorization, protected
installation, budget amendment, reconciliation, replay, admission, promotion,
merge, or push.
