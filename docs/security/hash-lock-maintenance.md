# Hash-locked dependency maintenance

The repository uses complete, transitive, SHA-256-hashed requirement locks for the **Linux x86_64 / Python 3.11 / manylinux 2.28** execution boundary used by the protected-main CI, rootless container build, and synthetic parser-fuzzing jobs. The source input files remain human-reviewable (`requirements.txt`, `requirements-runtime.txt`, and `requirements/fuzz.in`); only the committed files under `requirements/locks/` are installation inputs for automated environments.

> Hash checking is deliberately all-or-nothing. Every installed direct and transitive distribution is version-pinned and carries one or more SHA-256 hashes. Runtime and fuzz jobs also use `--only-binary=:all:`. The full development lock retains its hash-verified `antlr4-python3-runtime==4.9.3` source distribution because that required upstream version publishes no compatible wheel; it therefore uses `--require-hashes` without `--only-binary`. See **SRC-053**.

## Regeneration procedure

Run the following on a reviewed Linux x86_64 maintainer environment with Python 3.11 compatibility available:

```bash
uv --version
./scripts/generate_hash_locks.sh
python -m pip install --dry-run --require-hashes \
  -r requirements/locks/development-py311-manylinux_2_28.txt
python -m pip install --dry-run --require-hashes --only-binary=:all: \
  -r requirements/locks/runtime-py311-manylinux_2_28.txt
python -m pip install --dry-run --require-hashes --only-binary=:all: \
  -r requirements/locks/fuzz-py311-manylinux_2_28.txt
```

The locks in this change were generated with `uv 0.12.1`. A pull request that changes an input dependency or lock must include the regenerated lock diff, resolver validation, the complete test suite, source audit, and the protected-main CI/container/CodeQL checks. Do not delete hashes, add `--no-require-hashes`, use placeholder hashes, or reuse these Linux locks for a different Python ABI or platform.

When support for another execution platform is introduced, add a separately generated and reviewed platform lock, update the relevant automated installation command atomically, and extend the regression tests. The source inputs are not themselves runtime installation files in CI or containers.
