# Commands used for the v4 recovery record

All paths below are relative to the main repository unless stated otherwise.
Commands after the worktree heading were run from
`.claude/worktrees/dev-GRRR-gu87`.

```bash
pvg story claim GRRR-gu87
git worktree add --checkout .claude/worktrees/dev-GRRR-gu87 story/GRRR-gu87
git -C .claude/worktrees/dev-GRRR-gu87 rev-parse HEAD
# Required result: c717a85456624a0e659898d94ed0e8070a76ae97

git clone https://github.com/paivot-ai/vlt \
  .tmp-sr_pm/trusted-observation/source-recovery
git -C .tmp-sr_pm/trusted-observation/source-recovery checkout --detach \
  129e0b3f15a3bd6af949ee47d76f6855c582ab73
git -C .tmp-sr_pm/trusted-observation/source-recovery rev-parse HEAD
git -C .tmp-sr_pm/trusted-observation/source-recovery rev-parse HEAD:LICENSE
git -C .tmp-sr_pm/trusted-observation/source-recovery status --porcelain --untracked-files=all
# Commit, license blob, and clean status were verified before packaging.

curl --fail --location --retry 3 --retry-delay 2 \
  --output .tmp-sr_pm/trusted-observation/go1.26.10.linux-arm64.tar.gz \
  https://go.dev/dl/go1.26.10.linux-arm64.tar.gz
shasum -a 256 .tmp-sr_pm/trusted-observation/go1.26.10.linux-arm64.tar.gz
```

## Fresh story worktree

```bash
python3 scripts/prepare-trusted-observation \
  ../../../.tmp-sr_pm/trusted-observation/source-recovery \
  ../../../.tmp-sr_pm/trusted-observation/go1.26.10.linux-arm64.tar.gz \
  ../../../.tmp-sr_pm/vm \
  ../../../.tmp-sr_pm/trusted-observation/prepared-v3-recovery
```

The first retained-anchor attempt correctly failed. The command reproduced below
uses the authentic retained receipt hash:

```bash
python3 scripts/verify-trusted-preparation \
  ../../../.tmp-sr_pm/trusted-observation/prepared-v3-recovery \
  775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c
# Exit 1: Preparation receipt differs from retained anchor.
```

An earlier prose transcription ended `...ae9d0c0c`; if encountered in history it
is a mistyped-anchor variant, not the authentic retained-anchor check.

The v4 candidate is verified against its own recovered receipt anchor:

```bash
python3 scripts/verify-trusted-preparation \
  ../../../.tmp-sr_pm/trusted-observation/prepared-v3-recovery \
  3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7
```

## Direct receipt/profile comparison

The comparison read both `preparation.json` files and both
`prepared-profile.json` files, compared the complete mappings listed in
`COMPARISON.json`, and confirmed that exactly five top-level receipt fields
differ. The decisive checks were:

```python
old["source"]["files"] == new["source"]["files"]
old["primary_iso_readback"] == new["primary_iso_readback"]
old["supervisor"] == new["supervisor"]
old["helper"] == new["helper"]
old["toolchain_sha256"] == new["toolchain_sha256"]
old["shared_assets"] == new["shared_assets"]
old["compiler"] == new["compiler"]
old["compiler_license_sha256"] == new["compiler_license_sha256"]
old["development_binding_sha256"] == new["development_binding_sha256"]
{k: v for k, v in old_profile.items() if k != "input_image_sha256"} == \
    {k: v for k, v in new_profile.items() if k != "input_image_sha256"}
```

The canonical source inventory digest and payload hashes are recorded in
`COMPARISON.json`; the generated 52-line `source.sum` payload is identical
inside both ISOs.
