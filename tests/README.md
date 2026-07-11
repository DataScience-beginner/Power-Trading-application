# Active Automated Tests

This folder contains deterministic tests that are safe for the automated golden gate.

Run the default gate before normal commits:

```bash
python scripts/quality/golden_test.py --mode standard
```

Run the rigorous gate before risky refactors/releases:

```bash
python scripts/quality/golden_test.py --mode rigorous
```

## Policy

Active tests must be:

- deterministic;
- timeout-bounded;
- safe for local execution;
- free from production writes;
- independent of local generated Excel files unless the test creates its own fixture.

Historical manual tests that require localhost servers, Railway networking, or generated `Data/` files are archived under:

```text
archive/legacy/tests/manual/
```

Those tests should be converted into controlled integration tests before returning to `tests/`.

