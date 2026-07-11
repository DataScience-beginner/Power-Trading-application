# Archived Manual Tests

These files were moved out of the active pytest suite because they are not deterministic pre-commit tests.

They depend on one or more of:

- a running localhost API server;
- Railway production/staging network access;
- generated Excel files under local `Data/`;
- mutable local database state;
- manual inspection of printed output.

They are preserved here as historical workflow knowledge.

Before moving any of them back into `tests/`, convert them to:

- use isolated fixtures;
- use explicit timeouts;
- avoid production writes;
- avoid mandatory external network access;
- assert expected results instead of only printing output.

